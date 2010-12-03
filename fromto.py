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

                # for every from/to edge add the nodes and edges to the graph
                for fr, fr_region, to, to_region in fromto(html_file):
                    sizes[fr] = sizes.get(fr, 0) + 1
                    sizes[to] = sizes.get(to, 0) + 1
                    if not g.has_node(fr):
                        g.add_node(fr, {'region': fr_region}),
                    if not g.has_node(to):
                        g.add_node(to, {'region': to_region})
                    if not g.has_edge((fr, to)):
                        g.add_edge((fr, to))
                    print "%s %s -> %s" % (html_file, fr, to)

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


def fromto(html_file):
    """the gnarly part
    """
    html = codecs.open(html_file, 'r', 'utf-8').read()

    # for every from/to pair (cables can be sent to multiple people)
    # yeild the from, to tuple
    m = re.search('&#x000A;...? ([A-Z ]+?)(?:&#x000A;)+DE ([A-Z]+?) #\d+', html)
    if m:
        t, f = m.groups()
        # can be sent to multiple places
        for p in t.split(" "):
            if not p: 
                continue
            yield country(f), region(f), country(p), region(p)
    else:
        print "didn't recognize: %s" % html_file


def country(station):
    station = station.strip()
    return stations[station]['country_name']


def region(station):
    station = station.strip()
    return stations[station]['region']


if __name__ == "__main__":
    wikileaks_dir = sys.argv[1]
    process_html(os.path.join(wikileaks_dir, 'cable'))
