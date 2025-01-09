import socket
import scapy.all as sc
from tqdm import tqdm 

def get_info_from_bpkt(pkt : sc.Packet) -> list:
    # get num pkt inside batch
    pkt_bytes = bytes(pkt)[8:]
    n_batched_pkt = bin(int(pkt_bytes[:2].hex())).count("1")
    len1, len2= [map(pkt_bytes[2:4], int)]
    
    print(len1, len2, len3)
    return 

def is_batched(pkt : sc.Packet) -> bool:
    return pkt['Ether'].type == 0x69ce # 0x69ce are some smac bytes, if the packet is batched these bytes are shifted

def get_info_from_pkt(pkt : sc.Packet ) -> tuple:
    if pkt.haslayer('IP'):
        return pkt['IP'].src, pkt['IP'].dst, pkt['IP'].sport, pkt['IP'].dport, pkt['IP'].proto 
    
def ex_info(file_pcap, file_output):
    try:
        print(f"Lettura del file PCAP: {file_pcap}")
        pacchetti = sc.rdpcap(file_pcap)
        print(f"Pacchetti letti: {len(pacchetti)}")
        
        # check if packet is batched
        if is_batched(pacchetti[0]):
            print("Removing batch header")
            pacchetti = [get_info_from_bpkt(pkt) for pkt in pacchetti]
            return            
        
        info = set() # use a set to collect unique pkt 5-tuple
        for i in tqdm(range(len(pacchetti)),desc="Estrazione IP sorgenti",unit="pkt"):
            pkt = pacchetti[i]
            print(pkt.summary())
            pkt5 = get_info_from_pkt(pkt)
            info.add(pkt5)
            
        with open(file_output, "w") as file:
            file.write("\n".join([f"{ip[0]} {ip[1]} {ip[2]} {ip[3]} {ip[4]}" for ip in info]))
        
        print(f"IP sorgenti estratti e salvati in: {file_output}")
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