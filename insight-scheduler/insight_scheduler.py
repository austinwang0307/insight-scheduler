#! /usr/bin/env python

# Cpoyright (c) 2015 Hao-Ping Wang (austinwang0307@gmail.com)
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
    """Scheduler which awares of VC members and their topology."""

    def __init__(self, cluster_info):
        """Initial the scheduler"""

        # 1. Nova authentication.
        # 2. query numbers of compute nodes.

        creds = self.__nova_creds()
        nova = client.Client(**creds)
        self.hypervisors_num = len(nova.hypervisors.list())
        self.cluster_info = cluster_info
        #====================================================================
        self.hypervisors = [PDCStack06, PDCStack07, PDCStack13, PDCStack14]
        self.net_id = "net-id=e5aaee27-1a2e-4372-b09f-35fec66e89a7"
        self.key_name = "demo-key"
        self.security_group = "default"
        #====================================================================

    def __nova_creds(self):
        """Handles nova credentials"""

        # 1. get shell environment variables.

        cred = {}
        cred['username'] = os.environ['OS_USERNAME']
        cred['api_key'] = os.environ['OS_PASSWORD']
        cred['auth_url'] = os.environ['OS_AUTH_URL']
        cred['project_id'] = os.environ['OS_TENANT_NAME']
        return cred

    def __build_pmg(self):
        """Build physical machines graph using the self.hypervisors property"""

        # 1. construct physical machines graph, every pairs of PMs are connected.

        #pm_graph = Graph(directed=False)
        #pm_node_list = pm_graph.add_vertex(self.hypervisors)
        #for i in range(0, self.hypervisors):
        #    pm_graph.add_edge(pm_graph.vertex(i), pm_graph.vertex(0 if (i+1)==self.hypervisors else (i+1))

        pm_graph = complete_graph(self.hypervisors_num)

        return pm_graph

    def __build_vcg(self):
        """Build virtual cluster graph of the given vertices and edeges."""

        # vertices: list of vertices' ids, eg. [1, 2, 3]
        # edges: list of tuples of vertices, eg. [(1,2), (1,3)]
        # 1. make graph, according to template.json
        # 2. combined vertices to be placed together 

        #1.1 (tested)
        vc_graph = Graph(directed=False)
        vc_node_list = vc_graph.add_vertex(self.cluster_info["members"])
        for node_index in range(0, self.cluster_info["members"]):
            for link_node in self.cluster_info["topology"][node_index]["link"]:
                vc_graph.add_edge(vc_graph.vertex(node_index), vc_graph.vertex(link_node))
        remove_parallel_edges(vc_graph)
        
        #1.2 (tested)
        vprop_nodes = vc_graph.new_vertex_property("vector<int>")
        vprop_beScheduled = vc_graph.new_vertex_property("bool")
        vc_graph.vertex_properties["nodes"] = vprop_nodes
        vc_graph.vertex_properties["beScheduled"] = vprop_beScheduled
        for vertex_id in vc_node_list:
            #vprop_nodes[vc_graph.vertex(vertex_id)] = [vertex_id] # may not be needed
            vprop_beScheduled[vc_graph.vertex(vertex_id)] = True
        
        #2.1 (tested)
        for vertex_id in range(0, self.cluster_info["members"]):
            if(vprop_beScheduled[vc_graph.vertex(vertex_id)]):
                for node in self.cluster_info["topology"][vertex_id]["nodes_with_critical_link"]:
                    vprop_beScheduled[vc_graph.vertex(node)] = False
                critical_link_nodes = self.cluster_info["topology"][vertex_id]["nodes_with_critical_link"]
                critical_link_nodes.append(vertex_id)
                vprop_nodes[vc_graph.vertex(vertex_id)] = critical_link_nodes

        #2.2 (tested)
        removed_nodes = []
        for v in vc_graph.vertices():
            if not vprop_beScheduled[vc_graph.vertex(int(v))]:
                removed_nodes.append(int(v))
        for item in removed_nodes:
            vc_graph.remove_vertex(vc_graph.vertex(int(item)))

        return vc_graph

    def schedule_cluster(self):
        """Mapping of VC members and PMs"""

        # 1. construct PMG and VCG
        # 2. generate subgraph isomorphism
        # 3. nova boot cluster
        # 4. handle exceptions

        #1 (tested)
        pmg = __build_pmg()
        vcg = __build_vcg()

        #2 (tested)
        mappings = subgraph_isomorphism(vcg, pmg)

        #3.1 (tested)
        for m in range(0, len(mappings)):
            #print "mapping: " + str(m)
            for n in vcg.vertices():
                host = mappings[m][vcg.vertex(int(n))]
                #print "===begin==="
                #print host
                vm_list = []
                for vms in vcg.vertex_properties["nodes"][vcg.vertex(int(n))]:
                	vm_list.append(vms)
                #print vm_list
                #print "===end==="

                #3.2
                for vm in vm_list:
                    image = self.cluster_info["topology"][vm]["image"]
                    flavor = self.cluster_info["topology"][vm]["flavor"]
                    name = self.cluster_info["name"] + "-" + str(vm)
                    zone_host = "nova:" + self.hypervisors[host]
                    sub_P = subprocess.Popen(["nova", "boot", "--flavor", flavor, "--image", image, "--nic", self.net_id, "--security-group", self.security_group, "--key-name", self.key_name, "--availability-zone", zone_host, name])
                    stdout, stderr = sub_P.communicate()
                    exitCode = sub_P.returncode
                    if exitCode != 1:
                        sys.exit(stderr)
                    else:
                        print stdout

if __name__ == '__main__':
    """main function, program begins right here."""

    cluster = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "cluster="])
    except getopt.GetoptError as e:
        print "insight_scheduler.py --cluster <cluster.json>"
        sys.exit(2)
        #Unix programs generally use 2 for command line syntax errors and 1 for all other kind of errors. 

    if(len(opts) <= 0):
        print "insight_scheduler.py --cluster <cluster.json>"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "insight_scheduler.py --cluster <cluster.json>"
            sys.exit()
        elif opt in ("-c", "--cluster"):
            cluster = arg

    #print cluster
    
    with open(cluster) as data_file:
        cluster_info = json.load(data_file)

    #pprint(cluster_info)

    scheduler = InsightScheduler(cluster_info)
    scheduler.schedule_cluster()