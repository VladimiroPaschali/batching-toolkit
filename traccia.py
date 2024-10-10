from typing import Type
from scapy.all import *
import argparse 
import numpy
import random
from pprint import pprint
from topleiz import get_input, compute_hash 

from scapy.packet import Packet

def gen_payload(size):
    '''genera una stringa di dimensione size da usare come payload'''
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))


def create_flows(args, flows_packets):
    '''Crea un insieme di flussi di pacchetti, ciascuno con un pacchetto di tipo diverso'''
    # print(len(flows_packets))
    if len(flows_packets) == args.n_flows:
        return flows_packets
    else:
        for i in range(args.n_flows - len(flows_packets)):
            src = str(RandIP(args.s_subnet))
            dst = str(RandIP(args.d_subnet))
            sport = str(RandShort())
            dport = str(RandShort())
            if args.l4_proto == "MIX":
                proto = random.choice(["TCP", "UDP"])
            else:
                proto = args.l4_proto

            flows_packets.add((src, dst, proto, sport, dport))
    return create_flows(args, flows_packets) 

def uniform_dist(args):
    '''genera una lista di indici ripetuti uniformemente da usare per scegliere i flussi lunga args.n_pkt'''
    uniform_list=[]
    # Calcolare il numero di ripetizioni per ogni numero
    rep = math.ceil(args.n_pkt / args.n_flows)
    # Riempire la lista ripetendo i numeri da 0 a n_flows-1
    for i in range(args.n_flows):
        uniform_list.extend([i] * rep)
    # Troncamento della lista alla lunghezza specificata da n_pkt
    uniform_list = uniform_list[:args.n_pkt]
    random.shuffle(uniform_list)
    
    return uniform_list

def spacial_locality_dist(args):
    '''genera una lista di indici da 0 a args.n_flows dove lo stesso ondice è ripetuto args.locality_size volte lunga args.n_pkt'''
    spacial_list=[]
    while len(spacial_list) < args.n_pkt:
        spacial_list.extend([i for i in range(args.n_flows) for _ in range(args.locality_size)])
    return spacial_list[:args.n_pkt]

def gen_pkts(args,set_flows):
    '''Genera args.n_pkt pacchetti distribuiti secondo la distribuzione zipf con parametro args.locality_size partendo dai flussi set_flows'''
    list_flows = list(set_flows)

    print("uniform")
    distr = uniform_dist(args)
    print(distr)
    
    normal_payload_size = [int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkt)]
    qpkts = [[] for _ in range(args.n_queues)] 
    pkts = []
    for i in range(0,len(distr)):

        flow = list_flows[distr[(i)]%args.n_flows]
        src, dst, proto, sport, dport = flow
        
        key = (compute_hash(get_input(src, dst, int(sport), int(dport)), 12)) % args.n_queues

        if proto == "TCP":
            pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / TCP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i]))
        else:
            pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / UDP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i]))
        
        qpkts[key].append(pkt)
        pkts.append(pkt)

    output_pkts = []
    
    for i in range(args.n_pkt//args.locality_size):
        for j in range(args.n_queues):
            output_pkts.extend(qpkts[j][offset:offset+args.locality_size])
        offset += args.locality_size
 
    return output_pkts, pkts


def gen_pkts_chiesa(args,set_flows):

    '''Genera args.n_pkt pacchetti distribuiti secondo la distribuzione zipf con parametro args.locality_size partendo dai flussi set_flows'''
    list_flows = list(set_flows)

    print("locality")
    distr = spacial_locality_dist(args)
    print(distr)

    normal_payload_size = [int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkt)]
    pkts = []
    for i in range(0,len(distr)):

        flow = list_flows[distr[(i)]%args.n_flows]
        src, dst, proto, sport, dport = flow
        
        if proto == "TCP":
            pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / TCP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i]))
        else:
            pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / UDP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i]))
        
        pkts.append(pkt)
 
    return pkts

def n_pkt_to_int(arg):
    mult = {
        "K": 1000,
        "M": 1000000,
        "G": 1000000000
    }

    if arg[-1] in mult:
        return int(arg[:-1]) * mult[arg[-1]]
    else:
        return int(arg)     

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generatore di tracce di pacchetti')
        
    parser.add_argument("--n_pkt", help="Numero di pacchetti da generare", default=100, type=n_pkt_to_int)
    parser.add_argument("--n_flows", help="Numero di flussi da generare", type=int, default=40)
    parser.add_argument("--l4_proto", help="Protocollo di livello quattro, [TCP | UDP  | MIX]", type=str, default="MIX", choices=["TCP", "UDP", "MIX"])
    parser.add_argument("--locality_size", help="Parametro della selta o dei pacchetti vicini o del numero di pacchetti scelti per ogni queue", type=int, default=2)
    parser.add_argument("--distribution", help="Tipo di distribuzione [ZIPF | UNIFORM | LOCALITY]", type=str, default="LOCALITY", choices=["ZIPF", "UNIFORM", "LOCALITY"])
    parser.add_argument("--output", help="Nome del file di output .pcap", type=str, default="batch")
    parser.add_argument("--payload_size", help="Dimensione in valore medio del payload, è calcolata usando una distribuzione gaussiana centrata al valore passato con devstd=2",  type=int, default=10)
    parser.add_argument("--s_subnet", help="Subnet IP sorgente", type=str, default="0.0.0.0/0")
    parser.add_argument("--d_subnet", help="Subnet IP destinazione", type=str, default="0.0.0.0/0")
    parser.add_argument("--n_queues", help="Numero di queues diverse per la suddifisione per hash", type=int, default=2)
    
    args = parser.parse_args()
    
    flows_pkts = set()
    flows = create_flows(args, flows_pkts)

    output_filename=f"{args.output}_{args.distribution}_{args.n_pkt}pkts_{args.n_flows}flows.pcap"    

    #hashed
    if(args.distribution == "UNIFORM"):
        output_pkts, pkts = gen_pkts(args, flows)
        offset = 0    
        wrpcap(output_filename, pkts)
        wrpcap(f"hashed_{output_filename}", output_pkts)
    else:
        
        output_pkts = gen_pkts_chiesa(args, flows)
        pprint(output_pkts)
        wrpcap(f"chiesa{output_filename}", output_pkts)
    
    pass
    