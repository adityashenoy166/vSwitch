import socket
import sys

server_port = None
if len(sys.argv) != 2:
  print("Usage:python3 vswitch.py {VSWITCH_PORT}")
  sys.exit(1)
else:
  server_port = int(sys.argv[1])

server_addr = ("0.0.0.0",server_port)
vserver_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

vserver_sock.bind(server_addr)
print(f"[VSwitch] started at {server_addr[0]}:{server_addr[1]}")

mac_table = {}

while True:
  data,vport_addr = vserver_sock.recvfrom(1518)
  eth_header = data[:14]
  eth_dst = ":".join("{:02x}".format(x) for x in eth_header[0:6])
  eth_src = ":".join("{:02x}".format(x) for x in eth_header[6:12])
  print(f"[VSwitch] vport_addr<{vport_addr}>"
        f"src<{eth_src}> dst<{eth_dst}> datasz<{len(data)}>")
  if (eth_src not in mac_table or mac_table[eth_src]!=vport_addr):
    mac_table[eth_src] = vport_addr
    print(f"ARP Cache:{mac_table}")
  if eth_dst in mac_table:
    vserver_sock.sendto(data,mac_table[eth_dst])
    print(f"Forwarded to {eth_dst}")
  elif eth_dst == "ff:ff:ff:ff:ff:ff":
    brd_dst_macs = list(mac_table.keys())
    if eth_src in brd_dst_macs:
      brd_dst_macs.remove(eth_src)
    brd_dst_vports = {mac_table[mac] for mac in brd_dst_macs}
    print(f"Broadcasted to:{brd_dst_vports}")
    for brd_dst in brd_dst_vports:
      vserver_sock.sendto(data,brd_dst)
  else:
    print(f"Discarded")