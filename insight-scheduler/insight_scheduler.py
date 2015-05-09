#! /usr/bin/env python

# Cpoyright (c) 2015 austinwang0307@gmail.com
# All Rights Reserved.

"""

The InsightScheduler is for Virtual Cluster placement on OpenStack
Currently, OpenStack isn't aware of VCs nor VNIs (Virtual Network Infrastructure)
Also, VM-Ensembles scheduling is in a blueprint of Nova
At this moment, we use OpenStack API to help shceduling VCs
As soon as Nova supports VM-Ensembles scheduling
We will integrate InsightScheduler to Nova source code.

https://blueprints.launchpad.net/nova/+spec/vm-ensembles

"""

import subprocess
from graph_tool.all import *

class InsightScheduler(object):
    """Scheduler which awares of VC members."""

    def schedule_cluster(self, vcg, pmg):
    	"""Mapping of VC members and PMs"""

    	# To-do:
    	# inputs: VC graph, PMs graph
    	
    def make_graph(self, vertex, weighted_edge):
    	"""Construct graph of the given vertice and weighted edeges."""
    	