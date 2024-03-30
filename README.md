# NAS PROJECT

The project consists in the deployment of a network whose scheme is shown in the tpologie.png file. We first deployed it manually in GNS3 but rapidely generated it automatically with Telnet. The latters where implemented specifically for the project, i.e. it can't be used for any kind of network .

## Usage

The project generates configuration for a IPv4 and OPSF network that also runs MPLS and BGP on border-routers. iBGP sessions are established between all border-routers and each of them can establish eBGP session with client border-routers. This network is capable of providing BGP/MPLS VPN solution for clients that want VPN connection between several sites.To test the configuration on the given network you can reproduce the network in a new GNS3 project **with the same connected interfaces** (this way you won't have to update "interface" fields in the intent file).
The configurations are generated by using telnet.
For run the project: **python3 telnet.py**

## Features

-Automated generation of IP addresses for each link of the network (physical/loopback interfaces) based on IP prefix 

-Enabling IGP on the routers in the core (OSPF)

-Automated BGP configuration

-iBGP and eBGP sessions

-Automated VPNv4 configuration

-Handling multiple VPN clients in the same addressing space

-Automated generation of LDP 

-Automated generation of vrfs

## Intent Files
The intent and architecture files are json files following a particular format.


