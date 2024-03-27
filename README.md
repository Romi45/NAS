# NAS PROJECT

The project consists in the deployment of a network whose scheme is shown in the tpologie.png file. We first deployed it manually in GNS3 but rapidely generated it automatically with Telnet. The latters where implemented specifically for the project, i.e. it can't be used for any kind of network .

## Usage

The project generates configuration for a IPv4 and OPSF network that also runs MPLS and BGP on border-routers. iBGP sessions are established between all border-routers and each of them can establish eBGP session with client border-routers. This network is capable of providing BGP/MPLS VPN solution for clients that want VPN connection between several sites.


