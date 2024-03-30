#Configure Loopback Interface
def config_loopback(ip_loopback, protocol):
    config = []
    
    # Creation du netmask à partir du /mask
    ip_loopback0,netmask0 = ip_loopback.split("/")
    netmask1 = str(256 - 2**(32-int(netmask0)))
    netmask = "255.255.255.x".replace("x",netmask1)

    config.append("conf t")
    config.append("interface Loopback0")
    config.append(f"ip address {ip_loopback0} {netmask}")
    config.append("no shutdown")

    if protocol == "OSPF":
        config.append("ip ospf 666 area 0")

    config.append("end")

    return config



# Configure each interface
def config_interface(interfaces, protocol, router, as_type, all_as):
    config = []

    if protocol == "OSPF":  
        config.append('conf t')
        config.append("router ospf 666")
        router_id = router.loopback_address.split("/")[0]
        config.append(f"router-id {router_id}")
        config.append("end")
    


    for interface in interfaces:

        ip_address = interface["ip_address"]
        ip_address0,netmask0 = ip_address.split("/")
        netmask1 = str(256 - 2**(32-int(netmask0)))
        netmask = "255.255.255.x".replace("x",netmask1)

        #liste router as provider
        r_list = []
        for r in all_as[0].routers:
            r_list.append(r.name)

        config.append("conf t")
        config.append(f"interface {interface['name']}")

        if interface['neighbor'] == "None":
            config.append("shutdown")


        else:
            if ip_address:

                config.append(f"ip address {ip_address0} {netmask}")
                config.append("no shutdown")

                
                if protocol == "OSPF":  
                    config.append("ip ospf 666 area 0")
                
                #Ne fais pas cette commande pour les interfaces de bordure
                if as_type == "Provider" and interface["neighbor"] in r_list:
                    config.append("mpls ip")
            
            else:
                config.append("no ip address")


        config.append("end")



    return config 



# Configure bgp 
def config_bgp(router, as_info, all_as):
    config = []
    
    if router.type == "eBGP":
        as_number = router.as_number

        router.as_number = as_number

        config.append("conf t")
        config.append(f"router bgp {as_number}")
        router_id = router.loopback_address.split("/")[0]
        
        # Comme ca les routeurs qui ont la même addresse loopback n'auront pas le même router id
        if as_info.type == "Client":

            if router.name[2] == "B":
                router_id = ".".join([router_id.rsplit(".", 1)[0], str(int(router_id.rsplit(".", 1)[1]) + 1)])

        config.append(f"bgp router-id {router_id}")


        
        if as_info.type == "Provider":

            #cherche l'id voisin si as provider
            for r in as_info.routers:
                if r.type == "eBGP" and router.name != r.name:
                    id_voisin = r.loopback_address.split("/")[0]

                    config.append(f"neighbor {id_voisin} remote-as {as_number}")
                    config.append(f"neighbor {id_voisin} update-source Loopback0")
                    config.append(f"address-family ipv4")
                    config.append(f"no neighbor {id_voisin} activate")
                    config.append(f"exit-address-family")
                    config.append(f"address-family vpnv4")
                    config.append(f"neighbor {id_voisin} activate")
                    config.append(f"neighbor {id_voisin} send-community extended")
                    config.append(f"exit-address-family")



        elif as_info.type == "Client":

            #avoir une liste des routers dans as provider pour avoir acces  l'ip des voisins
            r_list = []
            for r in all_as[0].routers:
                r_list.append(r.name)

            for i in router.interfaces:

                if i["neighbor"] in r_list:
                    neighbor_name = i["neighbor"]
                    neighbor_interface = i["neighbor_interface"]


                    for rr in all_as[0].routers:
                        if rr.name == neighbor_name:

                            for interf in rr.interfaces:
                                if interf["name"] == neighbor_interface:
                                    ip_voisin, _ = interf["ip_address"].split("/")
                                    loopback = router.loopback_address.split("/")[0]
                                    remote_as = all_as[0].routers[0].as_number

                                    config.append(f"neighbor {ip_voisin} remote-as {remote_as}")
                                    config.append(f"address-family ipv4")
                                    config.append(f"network {loopback} mask 255.255.255.255")
                                    config.append(f"neighbor {ip_voisin} activate")
                                    config.append(f"neighbor {ip_voisin} allowas-in 1")
                                    config.append(f"exit-address-family")


        config.append("end")

    return config
    


#configure the vrfs

def config_vrf(router, as_info, all_as, part):
    
    config = []

    if as_info.type == "Provider" and router.type == "eBGP":

        # invertit les exports et imports pour les routeurs de bordure
        invert = False

        if router.name[-1] == "2":
            invert = True


        r_list = []
        for r in all_as[1].routers:
                r_list.append(r.name)
        
        for interface in router.interfaces:

            if interface["neighbor"] in r_list:
                neighbor_name = interface["neighbor"]
                neighbor_interface = interface["neighbor_interface"]

                for rr in all_as[1].routers:
                    if rr.name == neighbor_name:
                        as_voisin = rr.as_number
                        couleur = rr.couleur
                        for interf in rr.interfaces:
                            if interf["name"] == neighbor_interface:
                                ip_voisin, _ = interf["ip_address"].split("/")

                                # On appelle la fonction une premiere fois pour aoir les vrfs quand on set les addresses ip sinon erreur
                                if part == 1:
                                    config.append("enable")
                                    config.append("conf t")
                                    config.append(f'ip vrf {couleur}')
                                    config.append(f'rd {as_voisin}:1')
                                    
                                    if not invert:
                                        config.append(f'route-target export {as_voisin}:2')
                                        config.append(f'route-target import {as_voisin}:3')
                                    else:
                                        config.append(f'route-target export {as_voisin}:3')
                                        config.append(f'route-target import {as_voisin}:2')

                                    config.append("end")
                                

                                # On l'appelle une deuxieme fois à la fin pour les family address
                                else:

                                    interface_name = interface["name"]
                                    ip_address = interface["ip_address"]
                                    ip_address0,netmask0 = ip_address.split("/")
                                    netmask1 = str(256 - 2**(32-int(netmask0)))
                                    netmask = "255.255.255.x".replace("x",netmask1)

                                    config.append("conf t")
                                    config.append(f"interface {interface_name}")
                                    config.append(f"ip vrf forwarding {couleur}")
                                    config.append(f"ip address {ip_address0} {netmask}")
                                    config.append("no shutdown")
                                    config.append("end")

                                    config.append("conf t")
                                    config.append(f"router bgp {router.as_number}")
                                    config.append(f"address-family ipv4 vrf {couleur}")
                                    config.append(f"neighbor {ip_voisin} remote-as {as_voisin}")
                                    config.append(f"neighbor {ip_voisin} activate")
                                    config.append(f"neighbor {ip_voisin} allowas-in 1")
                                    config.append(f"exit-address-family")
                                    config.append("end")


    return config
