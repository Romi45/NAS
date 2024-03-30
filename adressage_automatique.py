import json

class Router:
    def __init__(self, name, as_number, interfaces, couleur= None, type=None):
        self.name = name
        self.type = type
        self.loopback_address = ""
        self.interfaces = interfaces
        self.as_number = as_number
        self.couleur = couleur

    def __str__(self):
        return f"Router(Name: {self.name}, Type: {self.type}, Loopback: {self.loopback_address}, Interfaces: {self.interfaces}, As_number: {self.as_number}, Couleur: {self.couleur})"

class AS:
    def __init__(self, type, ip_range, protocol, routers):
        self.type = type
        self.ip_range = ip_range
        self.protocol = protocol
        self.routers = [self.regle_router(router) for router in routers]

    # on utilise cette fonction comme ca je peux set les attributs à None si ils figurent pas sur le json
    def regle_router(self, router):

        type = router.get('type')
        couleur = router.get('couleur')
        return Router(router['name'], router['as_number'], router['interfaces'], couleur, type)

    def __str__(self):
        router_str = '\n  '.join(str(router) for router in self.routers)
        return f"AS(type: {self.type}, IP Range: {self.ip_range}, Protocol: {self.protocol}, Routers:\n  {router_str})"
    

def generate_ip(iteration,iteration_client, router, AS, Autre_AS):

    #Loop sur toutes les interfaces et check si on leur a deja assigner une addresse ip    
    for interface in router.interfaces:

        if "ip_address" not in interface:
            neighbour_name = interface["neighbor"]

            not_same_as = True


            for r in AS.routers:
                if r.name == neighbour_name:
                    ip_address = (AS.ip_range).replace('x',str(iteration*4 + 1))
                    interface["ip_address"] =  ip_address
                    not_same_as = False


                    #Cherche l'interface correspondante sur l'autre routeur de la connexion
                    for rr in AS.routers:
                        if rr.name == neighbour_name:

                            for interf in rr.interfaces:
                                if interf["neighbor_interface"] == interface["name"]:
                                    mirror_ip_address = (AS.ip_range).replace('x',str(iteration*4 + 2))
                                    interf["ip_address"] =  mirror_ip_address


                    break


            #Assignation des addresses ip pour les routeurs de bordure
            if not_same_as:
                ip_address = (Autre_AS.ip_range).replace('x','1').replace('y',str(iteration_client))
                interface["ip_address"] =  ip_address


                for rr in Autre_AS.routers:
                        if rr.name == neighbour_name:

                            for interf in rr.interfaces:
                                if interf["neighbor_interface"] == interface["name"]:
                                    mirror_ip_address = (Autre_AS.ip_range).replace('x','2').replace('y',str(iteration_client))
                                    interf["ip_address"] =  mirror_ip_address

    


def generate_loopback(loopback_iteration,router,as_content):

    # Les routeurs clients d'un côté ont tous la même addresse loopback (c'est un peu moche comme code)

    loopback_address = ""

    if as_content.type == "Client":
        if router.name[2] == "A":
            router.loopback_address = "x.x.x.x/32".replace("x",str(loopback_iteration))

        else:
            for r in as_content.routers:
                if r.name[2] == "A" and router.name[-1] == r.name[-1]:
                    router.loopback_address = r.loopback_address
                    break


    else:
        router.loopback_address = "x.x.x.x/32".replace("x",str(loopback_iteration))
