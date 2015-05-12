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

import sys
import os
import getopt
import subprocess
import simplejson as json
from graph_tool.all import *
from novaclient.v1_1 import client
#from pprint import pprint

class InsightScheduler(object):
    """Scheduler which awares of VC members."""

    def __init__(self):
        """Initial the scheduler"""

        creds = __nova_creds()
        nova = client.Client(**creds)
        self.hypervisors = len(nova.hypervisors.list())

    def __nova_creds(self):
        """Handles nova credentials"""

        cred = {}
        cred['username'] = os.environ['OS_USERNAME']
        cred['api_key'] = os.environ['OS_PASSWORD']
        cred['auth_url'] = os.environ['OS_AUTH_URL']
        cred['project_id'] = os.environ['OS_TENANT_NAME']
        return cred

    def __build_pmg(self):
        """Build physical machines graph using the self.hypervisors property"""

    def schedule_cluster(self, vcg, pmg):
    	"""Mapping of VC members and PMs"""

    	# To-do:
    	# inputs: VC graph, PMs graph
    	
    def build_vcg(self, vertices, edges):
    	"""Build virtual cluster graph of the given vertices and edeges."""

        # vertices: list of vertices' ids, eg. [1, 2, 3]
        # edges: list of tuples of vertices, eg. [(1,2), (1,3)]
    	
if __name__ == '__main__':
    """main function, begins right here."""

    cluster = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "cluster="])
    except getopt.GetoptError as e:
        print "insight_scheduler.py -cluster <cluster.json>"
        sys.exit(2)

    if(len(opts) <= 0):
        print "insight_scheduler.py -cluster <cluster.json>"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "insight_scheduler.py -cluster <cluster.json>"
            sys.exit()
        elif opt in ("-c", "--cluster"):
            cluster = arg

    #print cluster
    
    with open(cluster) as data_file:
        cluster_info = json.load(data_file)

    #pprint(cluster_info)

    