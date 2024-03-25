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



# Configure each interface(已完成)
def config_interface(interfaces, protocol, router):
    config = []

    for interface in interfaces:
        config.append("conf t")

        config.append(f"interface {interface['name']}")
        config.append("no ip address")

        if interface['neighbor'] == "None":
            config.append("shutdown")

        else:

            if interface.ip_address:
                config.append(f"ip address {interface.ip_address}")
                config.append("no shutdown")

                
                if protocol == "OSPF":  
                    config.append("end")
                    config.append('conf t')
                    config.append("router ospf 666")
                    router_id = router.loopback_address.split("/")[0]
                    config.append(f"router-id {router_id}")
                    
                    config.append("end")

                    config.append("conf t")
                    config.append(f"interface {interface['name']}")
                    config.append("ip ospf 666 area 0")


        config.append("end")



    return config  # Moved return statement outside the loop



# Configure bgp neighbor
def config_bgp(router, router_id, routers, connections_matrix_name, routers_dict):
    config = []
    current_as = routers_dict[router.name]['AS']
    neighbor_liste = []

    config.append("conf t")
    config.append(f"router bgp {current_as}")
    config.append(f"bgp router-id {router_id}")
    
    if router.router_type == "eBGP":
        neighbor_ip = None

        for elem in connections_matrix_name:
            ((r1, r2), state) = elem

            if state == 'border':
                if router.name == r1:
                    neighbor = r2
                elif router.name == r2:
                    neighbor = r1
                else:
                    neighbor = None

                if neighbor:
                    for routeur in routers:
                        if routeur.name == neighbor:
                            for interface in routeur.interfaces:
                                if interface['neighbor'] == router.name:
                                    print(router.name)
                                    neighbor_ip = interface.get('ip_address', '')
                                    print(f"找到邻居ip了{neighbor_ip}")
                                    break

                    if neighbor_ip:
                        as_number = routers_dict[neighbor]['AS']
                        config.append(f"neighbor {neighbor_ip[:-3]} remote-as {as_number}")
                        neighbor_liste.append(neighbor_ip[:-3])

    for routeur_name, routeur_info in routers_dict.items():
        if routeur_name != router.name and routeur_info['AS'] == current_as:
            config.append(f"neighbor {routeur_info['loopback'][:-4]} remote-as {routeur_info['AS']}")
            config.append(f"neighbor {routeur_info['loopback'][:-4]} update-source Loopback0")
            neighbor_liste.append(routeur_info['loopback'][:-4])


    config.append("address-family ipv6 unicast")

    


    # Activate neighbor IP loopback
    for ip_neighbor in neighbor_liste:
        config.append(f"neighbor {ip_neighbor} activate")

    config.append("end")

    return config

# Configure LDP for MPLS
def config_mpls(interfaces):
     
    config = []    

    for interface in interfaces:
           
            config.append("conf t")
            config.append("mpls ip")
            config.append("mpls label protocol ldp") 
            config.append(f"interface {interface['name']}")
            config.append("mpls ip")
            config.append("exit")

    return config
    


#configure the vrfs

def config_vrf(router, router_id, routers, connections_matrix_name, routers_dict,client_name):
    
    config = []
    current_as = routers_dict[router.name]['AS']
    neighbor_liste = []


    if router.router_type == "eBGP":
        neighbor_ip = None

        for elem in connections_matrix_name:
            ((PE, CE), state) = elem

            if state == 'border':
                if router.name == PE:
                    neighbor = CE
                elif router.name == CE:
                    neighbor = PE
                else:
                    neighbor = None