import yaml
import os
import json
import requests
import ssl

### Specific CVP Libraries
from cvplibrary import CVPGlobalVariables, GlobalVariableNames 
from cvplibrary import RestClient 
from cvplibrary import Form


# Deactivate warnings and error for self-signed certificates.
ssl._create_default_https_context = ssl._create_unverified_context

"""
Credit to https://github.com/titom73 for functions
"""

__author__ = "Eric Gullickson"
__license__ = "BSD"
__version__ = "0.0.1"
__date__ = "08/12/2022"


# Get config via yaml pasted into text field.
ingest_config = Form.getFieldById( 'yaml_input' ).getValue()

# Load data from yaml into variable
switches = yaml.load(ingest_config)

# CVP IP address to connect to. 
# Should not be changed unless you know what to do.
CVP_ADDRESS='127.0.0.1'

def get_hostname(deviceIP):
    """
    Get device hostname from CVP from a managment IP
    
    Parameters
    ----------
    deviceIP : str
        Managment IP of device to look for hostname.
    
    Returns
    -------
    str
        device hostname if found, else return None
    """
    query_string = 'https://{0}/cvpservice/inventory/devices'.format(CVP_ADDRESS)
    client = RestClient(query_string, 'GET')
    if client.connect():
        device_list = json.loads(client.getResponse())

    for device in device_list:
        if deviceIP == device['ipAddress']:
            return device['hostname']
    return None

if __name__ == '__main__':

    # get hostname for a given management IP
    device_mgtIp =CVPGlobalVariables.getValue( GlobalVariableNames.CVP_IP )
    hostname = get_hostname(device_mgtIp)

    print("service routing protocols model multi-agent\n")
    # Generate the interface config
    for iface in switches[hostname]['interfaces']:
        print("interface %s" % iface)
        ip = switches[hostname]['interfaces'][iface]['ipv4']
        mask = switches[hostname]['interfaces'][iface]['mask']
        print(" ip address %s/%s" % (ip, mask))
        if "Ethernet" in iface:
            print(" no switchport")
            print(" mtu 9124")

    # prefix list config block
    print("ip prefix-list LOOPBACK")
    if "DC1" in hostname:
        for prefix in switches["global"]["DC1"]["loopbacks"]:
            print("  permit %s eq 32" % prefix)
    else:
        for prefix in switches["global"]["DC2"]["loopbacks"]:
            print("  permit %s eq 32" % prefix)
    
    # route-map config block
    print("route-map LOOPBACK permit 10")
    print("  match ip address prefix-list LOOPBACK")

    # Leaf AS filter on Spines
    if "spine" in hostname:
        print("peer-filter LEAF-AS-RANGE")
        print("  10 match as-range 65000-65535 result accept")
    #BGP Config Block
    print("router bgp %s" % switches[hostname]["BGP"]["ASN"])
    print("  router-id %s" % switches[hostname]['interfaces']["loopback0"]['ipv4'])
    print("  no bgp default ipv4-unicast")
    print("  maximum-paths 3")
    print("  distance bgp 20 200 200")
    if "borderleaf" in hostname:
        print("    neighbor DCI_Peer peer group")
        print("    neighbor DCI_Peer remote-as 65000")
        print("    neighbor DCI_Peer next-hop-self")
        print("    neighbor DCI_Peer maximum-routes 12000")
        print("    neighbor %s peer group DCI_Peer" % switches[hostname]["BGP"]["DCI-peers"][0])
    if "spine" in hostname:
        print("  bgp listen range 192.168.0.0/16 peer-group LEAF_Underlay peer-filter LEAF-AS-RANGE")
        print("  neighbor LEAF_Underlay peer group")
        print("  neighbor LEAF_Underlay send-community")
        print("  neighbor LEAF_Underlay maximum-routes 12000")
        print("  redistribute connected route-map LOOPBACK")
        print("  address-family ipv4")
        print("    neighbor LEAF_Underlay activate")
        print("    redistribute connected route-map LOOPBACK")
    else:
        print("  neighbor SPINE_Underlay peer group")
        print("  neighbor SPINE_Underlay remote-as %s" % switches[hostname]["BGP"]["spine-ASN"])
        print("  neighbor SPINE_Underlay send-community")
        print("  neighbor SPINE_Underlay maximum-routes 12000")
        print("  neighbor LEAF_Peer peer group")
        print("  neighbor LEAF_Peer remote-as %s" % switches[hostname]["BGP"]["ASN"])
        print("  neighbor LEAF_Peer next-hop-self")
        print("  neighbor LEAF_Peer maximum-routes 12000")
    
        for peer in switches[hostname]['BGP']['spine-peers']:
            print("    neighbor %s peer group SPINE_Underlay" % peer)
        print("  address-family ipv4")
        print("    neighbor SPINE_Underlay activate")
        print("    neighbor LEAF_Peer activate")
        if "borderleaf" in hostname:
            print("    neighbor DCI_Peer activate")
        print("    redistribute connected route-map LOOPBACK")