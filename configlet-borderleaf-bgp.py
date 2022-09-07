from cvplibrary import CVPGlobalVariables, GlobalVariableNames, Device

def create_routes(hostname):
    number = hostname[-1:]
    if hostname.startswith("borderleaf"):
        switch_type = "10"
    for x in range(100, 200):
        print "interface Loopback%d" % (x)
        print "   ip add 172.%s.%s.%d/32" % (switch_type, "1", x)
    return
user = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME )
passwd = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_USERNAME )
ip = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_IP )

ss = Device(ip)

def get_hostname():
    show_hostname = ss.runCmds(["enable", "show hostname"])[1]
    hostname = show_hostname['response']['hostname']
    return hostname

def main():
    hostname = get_hostname()
    if hostname.startswith("borderleaf"):
      create_routes(hostname)


if __name__ == "__main__":
    main()
