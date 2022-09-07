import yaml
import os
import json
import requests
import ssl

### Specific CVP Libraries
from cvplibrary import CVPGlobalVariables, GlobalVariableNames
from cvplibrary import RestClient
from cvplibrary import Form


__author__ = "Eric Gullickson"
__license__ = "BSD"
__version__ = "0.0.1"
__date__ = "08/17/2022"


# Get tenant config via yaml pasted into text field.
tenet_input = Form.getFieldById( 'yaml_input' ).getValue()

# Load data from yaml into variable
tenant_config = yaml.safe_load(tenet_input)

# Get tenant config via yaml pasted into text field.
switch_input = Form.getFieldById( 'yaml_input' ).getValue()

# Load data from yaml into variable
switches = yaml.safe_load(switch_input)

#Test switch
hostname="leaf1-DC1"

if __name__ == '__main__':

    # Build VRFs
    for tenant in tenant_config["Tenants"]:
        print("vrf instance %s" % tenant )
        print("ip routing vrf %s" % tenant )

    # Build VLANs
    for tenant in tenant_config["Tenants"]:
        for L2VNI in tenant_config["Tenants"][tenant]["L2VNI"]:
            print("VLAN %s" % tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VLANID'])

    # Tenant to VXLAN interface mapping
    for tenant in tenant_config["Tenants"]:
         for L2VNI in tenant_config["Tenants"][tenant]["L2VNI"]:
            print("interface vlan %s" % tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VLANID'])
            print("vrf %s" % tenant )
            print("ip address virtual %s" % tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['SVI'])

    print("interface vxlan1")
    print("vxlan source-interface Loopback1")
    print("vxlan udp-port 4789")
    for tenant in tenant_config["Tenants"]:
        print("vxlan vrf %s vni %s" % (tenant,tenant_config['Tenants'][tenant]['L3VNI']))
    for tenant in tenant_config["Tenants"]:
         for L2VNI in tenant_config["Tenants"][tenant]["L2VNI"]:
            print("vxlan vlan %s vni %s" % (tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VLANID'],tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VNID']))

    print("router bgp %s" % switches[hostname]["BGP"]["ASN"])
    for tenant in tenant_config["Tenants"]:
        print("  vrf %s" % tenant )
        print("    rd %s:%s" % (switches[hostname]['interfaces']['loopback0']['ipv4'],tenant_config['Tenants'][tenant]['L3VNI']))
        print("    route-target import evpn %s:%s" % (tenant_config['Tenants'][tenant]['L3VNI'],tenant_config['Tenants'][tenant]['L3VNI']))
        print("    route-target export evpn %s:%s" % (tenant_config['Tenants'][tenant]['L3VNI'],tenant_config['Tenants'][tenant]['L3VNI']))
    for tenant in tenant_config["Tenants"]:
         for L2VNI in tenant_config["Tenants"][tenant]["L2VNI"]:
            print("  VLAN %s" % tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VLANID'])
            print("    rd auto")
            print("    route-target both %s:%s" % (tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VNID'],tenant_config['Tenants'][tenant]['L2VNI'][L2VNI]['VNID']))
            print("    redistribute learned")
            print("    address-family evpn")
            print("      neighbor EVPN activate")
