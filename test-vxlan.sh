!leaf switches
int eth7
channel-group 7 mode active
int po7
switchport access vlan 101
mlag 7

!host
int eth3-4
channel-group 7 mode active
int po7
no switchport
ip address 10.10.10.10/24

