import socket
import scapy.all as sc
from tqdm import tqdm 

def get_info_from_bpkt(pkt : sc.Packet) -> tuple:
    # get num pkt inside batch
    pkt_bytes = bytes(pkt)
    len1, len2, len3 = int(pkt_bytes[2:4].hex(), 16), int(pkt_bytes[4:6].hex(), 16), int(pkt_bytes[6:8].hex(), 16)
    
    # get pkt info
    pkts = (sc.Ether(pkt_bytes[8:8+len1]), sc.Ether(pkt_bytes[8+len1:8+len1+len2]), sc.Ether(pkt_bytes[8+len1+len2:8+len1+len2+len3]), sc.Ether(pkt_bytes[8+len1+len2+len3:]))
    
    info = []
    for i in range(4):
        if pkts[i].haslayer('IP'):
            info.append(get_info_from_pkt(pkts[i]))
    return tuple(info)

def is_batched(pkt : sc.Packet) -> bool:
    return pkt['Ether'].type == 0x69ce # 0x69ce are some smac bytes, if the packet is batched these bytes are shifted

def get_info_from_pkt(pkt : sc.Packet ) -> tuple:
    if pkt.haslayer('IP'):
        return pkt['IP'].src, pkt['IP'].dst, pkt['IP'].sport, pkt['IP'].dport, pkt['IP'].proto 
    assert False, "Packet does not have IP layer"
    
def ex_info(file_pcap, file_output):
    try:
        print(f"Lettura del file PCAP: {file_pcap}")
        pacchetti = sc.rdpcap(file_pcap)
        print(f"Pacchetti letti: {len(pacchetti)}")
        
        # check if packet is batched
        info = set() # use a set to collect unique pkt 5-tuple
        for i in tqdm(range(len(pacchetti)),desc="Estrazione PKT5 sorgenti",unit="pkt"):
            pkt = pacchetti[i]
            if is_batched(pkt):
                binfo = get_info_from_bpkt(pkt)
                info.update(binfo)
            else:    
                pkt5 = get_info_from_pkt(pkt)
                info.add(pkt5)
        print(f"PKT5 estratti: {len(info)}")
        with open(file_output, "w") as file:
            file.write("\n".join([f"{ip[0]} {ip[1]} {ip[2]} {ip[3]} {ip[4]}" for ip in info]))
        
        print(f"PKT5 estratti e salvati in: {file_output}")
    except Exception as e:
        print(f"Errore: {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ex_info.py <file_pcap> <file_output>")
        sys.exit(1)
    
    file_pcap = sys.argv[1]
    file_output = sys.argv[2]
    ex_info(file_pcap, file_output)
    pass