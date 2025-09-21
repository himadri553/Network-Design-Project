Himadri Saha

EECE 4830 - Network Design
Programming Project Phase 1

Himadri_Saha_Phase1/
│
├── phase1a/
│   ├── phase1a_UDP_client.py     
│   └── phase1a_UDP_server.py     
│
├── phase1b/
│   ├── my_cloud.bmp                # BMP file sent by client
│   ├── RDT1_client.py            
│   ├── RDT1_server.py
│   └── received.bmp**              # Will apear after running both scripts         
│
└── ReadMe.txt                    

Both Phase 1a and 1b include 2 files each: one for the server and one for the client. 
To see the project in action, start by running the server script first, then the client.
For phase 1b, a my_cloud.bmp file is included in the phase1b dirictory, which will be sent through the UDP sockets. 
The RDT1_server script will create a received.bmp, representing the .bmp file 
that the server sees based on the packets sent by the RDT clinet.