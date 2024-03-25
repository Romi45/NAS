#Configure Loopback Interface
def config_loopback(ip_loopback, protocol):
    config = []
    netmask0 = ip_loopback.split("/")[1]
    netmask1 = str(256 - 2**(32-int(netmask0)))
    netmask = "255.255.255.x".replace("x",netmask1)

    config.append("enable")
    config.append("conf t")
    config.append("interface Loopback0")
    config.append(f"ip address {ip_loopback}")
    config.append("no shutdown")

    if protocol == "OSPF":
        config.append("ip ospf 666 area 0")

    config.append("end")

    return config
