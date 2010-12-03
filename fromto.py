#!/usr/bin/env python

"""
This script scrapes the sending/receiving station in the cablegate datadump.
You'll need to point it at the location where you have downloaded the data.

   ./fromto.py /path/to/cablegate-201012021401
"""

import os
import re
import sys
import json
import codecs

from pygraph.classes.digraph import digraph


stations = json.loads(open("stations.js").read())


def process_html(cable_dir):
    # store the from, to addresses as a directed graph
    g = digraph()

    # keep track of how many times a particular node is mentioned
    # which will be used to determine the visual size of the node
    sizes = {}

    # walk the cables directory looking for html files
    for dirpath, dirnames, filenames in os.walk(cable_dir):
        for f in filenames:
            if f.endswith('.html'):
                html_file = os.path.join(dirpath, f)
                
                last = None
                stations = hops(html_file)

                # for every from/to edge add the nodes and edges to the graph
                for country, region in stations:
                    sizes[country] = sizes.get(country, 0) + 1

                    if not g.has_node(country):
                        g.add_node(country, {'region': region})

                    if last and not g.has_edge((last, country)):
                        g.add_edge((last, country))

                    last = country

    nodes = g.nodes()
    nodes.sort()
    node_names = []
    for n in nodes:
        x = {"nodeName": n, 
             "nodeTitle": n, #g.node_attributes(n)['full'], 
             "size": sizes[n],
             "region": g.node_attributes(n)['region']}
        node_names.append(x)

    # add edges using the node index number; would be nice if 
    # protoviz let you do this with the node's name &shrug;

    links = []
    for n1, n2 in g.edges():
        n1_id = nodes.index(n1)
        n2_id = nodes.index(n2)
        wt = g.edge_weight((n1, n2))
        links.append({"source": n1_id, "target": n2_id})

    data = {"nodes": node_names, "links": links}

    # write out the javascript that protoviz wants
    open("cablegate.js", "w").write("var cablegate = %s" % json.dumps(data, indent=2))


def hops(html_file):
    """the gnarly part that returns a list of hops from the originating
    station through any intermediary stations to the final destination
    Each hop in the list is a (country_name, region_name) tuple
    """
    hops = []
    html = codecs.open(html_file, 'r', 'utf-8').read()

    # extract from station
    m1 = re.search('&#x000A;...? [A-Z ]+?(?:&#x000A;)+DE ([A-Z]+?) #\d+', html)
    # extract intermediary stations
    m2 = re.search('&#x000A;...? ([A-Z ]+?)(?:&#x000A;)+DE [A-Z]+? #\d+', html)
    # extract destination station
    m3 = re.search('&#x000A;TO ([A-Z]+)/[A-Z]+', html)

    # need to at least have matches for the from and destination stations
    if m1 and m3:
        try: 
            from_station = m1.group(1)
            hops.append((country(from_station), region(from_station)))

            # if we have any intermediary stations add them in
            if m2:
                intermediary_stations = m2.group(1)
                for s in intermediary_stations.split(" "):
                    # ignore empty strings
                    if not s: 
                        continue
                    hops.append((country(s), region(s)))
        
            # final destination
            dest_station = m3.group(1)
            hops.append((country(dest_station), region(dest_station)))

        except UnknownStation, e:
            print "uhoh: %s" % e
            return []

    else:
        print "didn't recognize: %s" % html_file

    return hops


def country(station):
    try:
        station = station.strip()
        return stations[station]['country_name']
    except KeyError:
        raise UnknownStation("unknown station %s" % station)


def region(station):
    try: 
        station = station.strip()
        return stations[station]['region']
    except KeyError:
        raise UnknownStation(station)


class UnknownStation(Exception):
    pass


if __name__ == "__main__":
    wikileaks_dir = sys.argv[1]
    process_html(os.path.join(wikileaks_dir, 'cable'))
