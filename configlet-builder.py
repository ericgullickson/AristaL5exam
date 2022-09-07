#!//usr/local/bin/python3.9
import os
import yaml

# Get config via yaml pasted into text field.
#ingest_config = Form.getFieldById( 'yaml_input' ).getValue()

# Load data from yaml into variable
# switches = yaml.load(ingest_config)

# Get hostname from from
# hostname = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SERIAL)
hostname = "leaf1-DC1"

with open("/Users/egullickson/OneDrive - Vortex Optics/Development/Git-Vortex/python/Arista/switch-config.yml", "r") as file:
    switches = yaml.safe_load(file)

for switch_name,switch_config in switches.items():
    if hostname in switch_name:
        #global config lines
        print("service routing protocols model multi-agent\n")

        # Generate the interface config
        for iface in switches[switch_name]['interfaces']:
            print("interface %s" % iface)
            ip = switches[switch_name]['interfaces'][iface]['ipv4']
            mask = switches[switch_name]['interfaces'][iface]['mask']
            print(" ip address %s/%s" % (ip, mask))
            if "Ethernet" in iface:
                print(" no switchport")
                print(" mtu 9124")

        # prefix list config block
        print("ip prefix-list LOOPBACK")
        if "DC1" in hostname:
            for prefix in switches["global"]["DC1"]["loopbacks"]:
                print("  permit %s" % prefix)
        else:
            for prefix in switches["global"]["DC2"]["loopbacks"]:
                print("  permit %s" % prefix)
        
        # route-map config block
        print("route-map LOOPBACK permit 10")
        print("  match ip address prefix-list LOOPBACK")
        print("peer-filter LEAF-AS-RANGE")
        print("  10 match as-range 65000-65535 result accept")
        print("router bgp %s" % switches[switch_name]["BGP"]["ASN"])
        print("  router-id %s" % switches[switch_name]['interfaces']["loopback0"]['ipv4'])
        print("  no bgp default ipv4-unicast")
        print("  maximum-paths 3")
        print("  distance bgp 20 200 200")
        if "spine" in switch_name:
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
              print("  neighbor SPINE_Underlay remote-as %s" % switches[switch_name]["BGP"]["spine-ASN"])
              print("  neighbor SPINE_Underlay send-community")
              print("  neighbor SPINE_Underlay maximum-routes 12000")
              print("  neighbor LEAF_Peer peer group")
              print("  neighbor LEAF_Peer remote-as %s" % switches[switch_name]["BGP"]["ASN"])
              print("  neighbor LEAF_Peer next-hop-self")
              print("  neighbor LEAF_Peer maximum-routes 12000")
            
#             List the neighbor IPs here. It should be three spines for SPINE_Underlay and one LEAF_Peer
              print("  redistribute connected route-map LOOPBACK")
              print("  address-family ipv4")
              print("    neighbor SPINE_Underlay activate")
              print("    neighbor LEAF_Peer activate")





#print("router bgp %s" % switches[])

#https://github.com/sdn-pros/level5-ansible-cvp/blob/main/vars/underlay.yml