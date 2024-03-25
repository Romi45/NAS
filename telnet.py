import gns3fy
import telnetlib3
import time
import json
from adressage_automatique import *
from telnet_config import *
import threading



nodes_ports = {}

def get_nodes(project_name):

    server = gns3fy.Gns3Connector("http://localhost:3080")

    projet = gns3fy.Project(name=project_name, connector=server)
    
    projet.get()
    projet.open()

    for node in projet.nodes:
        node.get()
        nodes_ports[node.name] = node.console
        node.start()


get_nodes("NAS_PROJET_SAVE")

def telnet_write(config,port):
    
    try:
        print(port)
        tn = telnetlib3.Telnet('localhost',port)
        time.sleep(1)
        tn.write(b"\r") #To start writing
        time.sleep(1)

        for command in config:
            tn.write(command.encode())
            tn.write(b"\r")
            time.sleep(0.01)

        time.sleep(1)

        tn.write(b"write\r\r")

    except Exception as e:
        print(f"Error: {e}")


def process_router(as_index, router, all_routers):

    config = []

    config.extend(config_loopback(router.loopback_address, as_index.protocol))
    print(config)
    config.extend(config_interface(router.interfaces, as_index.protocol, router))

#     config.extend(config_bgp(router, router_id, all_routers, connections_matrix_name, routers_info))

#     config.extend(config_mpls(interfaces))

#     config.extend(config_vrf(interfaces))
    
#     ()
#     print(config)
#     telnet_write(config, nodes_ports[router.name])


get_nodes("NAS_PROJET_SAVE")
#print(nodes_ports)


with open('new intent.json', 'r') as file:
    data = json.load(file)

all_as = [AS(as_info['type'], as_info['ip_range'], as_info['protocol'], as_info['routers']) for as_info in data['AS']]
all_routers = [router for as_index in all_as for router in as_index.routers]
#Generation des addresses ip
iteration = 0
iteration_client = 0
for as_index,as_content in enumerate(all_as):
    for router in as_content.routers:
        autre_as_index = 0 if as_index==1 else 1
        iteration_client = generate_ip(iteration, iteration_client, router, all_as[as_index], all_as[autre_as_index])
        iteration += 1

#Generation des loopbacks
iteration_loopback = 1
for as_content in all_as:
    for router in as_content.routers:
        generate_loopback(iteration_loopback,router)
        iteration_loopback += 1

for as_index in all_as:
     for router in as_index.routers:
        process_router(as_index, router, all_routers)


# threads = []
# for as_index in all_as:
#     for router in as_index.routers:
#         thread = threading.Thread(target=process_router, args=(as_index, router, all_routers, connections_matrix_name, routers_info))
#         thread.start()
#         threads.append(thread)



# for thread in threads:
#     thread.join()


        
