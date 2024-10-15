from typing import Type
from scapy.all import *
import argparse 
import numpy
import random
# from pprint import print
import string


from scapy.packet import Packet

class BatchingHeader(Packet):
    '''definizione del formato del pacchetto di batching'''
    name = "BatchingHeader"
    fields_desc = [
        ShortField("next_len", 0),
    ]
    linktype = ETHER_TYPES


def add_batching_header(pkt,next_len):
    '''Aggiunge un header di batching al pacchetto pkt con la lunghezza del prossimo pacchetto next_len'''
    custom_header = BatchingHeader(next_len=next_len)
    return custom_header/pkt

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
    '''genera una lista di indici da 0 a args.n_flows dove lo stesso ondice è ripetuto args.dist_param volte lunga args.n_pkt'''
    spacial_list=[]
    while len(spacial_list) < args.n_pkt:
        spacial_list.extend([i for i in range(args.n_flows) for _ in range(args.dist_param)])
    return spacial_list[:args.n_pkt]


def gen_pkts(args,set_flows):
    '''Genera args.n_pkt pacchetti distribuiti secondo la distribuzione zipf con parametro args.dist_param partendo dai flussi set_flows'''
    list_flows = list(set_flows)
    pkts = []
    if args.distribution == "UNIFORM":
        print("uniform")
        distr = uniform_dist(args)
        # print(distr)
    elif args.distribution == "ZIPF":
        print("zipf")
        distr = numpy.random.zipf(a=args.dist_param, size=args.n_pkt)
        # print(distr)
    elif args.distribution == "LOCALITY":
        print("locality")
        distr = spacial_locality_dist(args)
        # print(distr)
    
    # pprint(list_flows)
    # pprint(distr)
    normal_payload_size = [int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkt)]
    # print("normal_palyoad_size: ",normal_payload_size)
    #cicla ogni batch_size
    #for i = 0; i<len(distr); i+=args.batch_size
    for i in range(0,len(distr), args.batch_size):
        batch = []
        #crea il batch di n pacchetti
        for x in range(args.batch_size):

            # flow = list_flows[(i+x)%args.n_flows]
            #usa il valore della distribuzione zipf come indice per selezionare il flusso
            flow = list_flows[distr[(i+x)]%args.n_flows]
            src, dst, proto, sport, dport = flow
            src = "192.168.101.1"
            dst = "192.168.101.2"
            sport = 2000
            dport = 8901
            smac= "e8:eb:d3:78:95:8d"
            dmac = "58:a2:e1:d0:69:ce"

            if proto == "TCP":
                # pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / TCP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i+x]))
                pkt = Ether(src=smac, dst=dmac) / IP(src=src, dst=dst) / TCP(dport=int(dport), sport=int(sport)) / Raw(str(i+x))

            else:
                # pkt = Ether(src='01:00:0c:cc:cc:cc', dst='00:11:22:33:44:55') / IP(src=src, dst=dst) / UDP(dport=int(dport), sport=int(sport)) / Raw(load=gen_payload(normal_payload_size[i+x]))
                # pkt = Ether(src=smac, dst=dmac) / IP(src=src, dst=dst, len=29) / UDP(dport=int(dport), sport=int(sport), len=9) / Raw(str(i))
                pkt = Ether(src=smac, dst=dmac) / IP(src=src, dst=dst) / UDP(dport=int(dport), sport=int(sport)) / Raw(str(i+x))

                # del pkt[IP].chksum
                pkt = pkt.__class__(bytes(pkt))

            
            batch.append(pkt)

        #aggiunge l'header di batching a tutti i pacchetti tranne l'ultimo con la lunghezza del successivo
        for x in range(args.batch_size-1):
            # pprint(batch)
            pkt = batch[x]

            #aggiungo l'header di batching al pacchetto
            # pkt = add_batching_header(pkt, len(batch[x+1]))
            pkt = add_batching_header(pkt, len(batch[x]))
            pkt = pkt/Raw(batch[x+1])

            #aggiungo il payload al pacchetto
            pkts.append(pkt)

        #ultimo pacchetto nel batch con next_len = 0
        # pkt = batch[args.batch_size-1]
        # pkt = add_batching_header(pkt, 0)
        # pkts.append(pkt)

 
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
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--n_pkt", help="Numero di pacchetti da generare", default=10, type=n_pkt_to_int)
    parser.add_argument("--n_flows", help="Numero di flussi da generare", type=int, default=4)
    parser.add_argument("--l4_proto", help="Protocollo di livello quattro, [TCP | UDP  | MIX]", type=str, default="MIX", choices=["TCP", "UDP", "MIX"])
    # parser.add_argument("--distribution", help="Parametro della distribuzione uniforme", type=bool)
    parser.add_argument("--dist_param", help="Parametro della distribuzione scelta alfa per zip o locality per locality", type=int, default=2)
    parser.add_argument("--distribution", help="Tipo di distribuzione [ZIPF | UNIFORM | LOCALITY]", type=str, default="ZIPF", choices=["ZIPF", "UNIFORM", "LOCALITY"])
    parser.add_argument("--output", help="Nome del file di output .pcap", type=str, default="batch")
    parser.add_argument("--batch_size", help="Dimensione del batch", type=int, default=2)
    parser.add_argument("--payload_size", help="Dimensione in valore medio del payload, è calcolata usando una distribuzione gaussiana centrata al valore passato con devstd=2",  type=int, default=10)
    parser.add_argument("--s_subnet", help="Subnet IP sorgente", type=str, default="0.0.0.0/0")
    parser.add_argument("--d_subnet", help="Subnet IP destinazione", type=str, default="0.0.0.0/0")
    
    args = parser.parse_args()

    # bind_bottom_up(BatchingHeader, Ether, type=0x1234)
    # bind_top_down(BatchingHeader, Ether, type=0x1234)

    #test args
    # args.distribution ="LOCALITY"
    # args.dist_param = 2
    # args.n_pkt = 10
    # args.n_flows = 10
    # args.batch_size= 2

    conf.l2types.register(1,BatchingHeader)  # Assegna il numero 1 al tuo BatchingHeader


    flows_packets = set()
    flows_packets = create_flows(args, flows_packets)
    # print(flows_packets)

    pkts = gen_pkts(args, flows_packets)
        
    output_filename=f"{args.output}_{args.distribution}_{args.n_pkt}pkts_{args.n_flows}flows.pcap"
    
    # bind_layers( BatchingHeader, Ether, {'type':0} )

    # conf.l2types.register(BatchingHeader, 1)  # Assegna il numero 147 al tuo BatchingHeader
    # # print(conf.l2types)
    # pcap_writer = PcapWriter("batching_packet.pcap", linktype=1)  # 1 è il tipo Ethernet
    # pcap_writer.write(pkts)
    # pcap_writer.close()


    wrpcap(output_filename, pkts)    


    print(pkts[0].show())
    print(hexdump(pkts[0]))
    print(pkts)


    # Esempio di utilizzo della funzione modify_ethernet
    # example_pkt = Ether() / IP(dst="192.168.1.1") / UDP(dport=12345, sport=54321)/Raw(load=gen_payload(10))
    # print(example_pkt.__class__)
    # modified_pkt = add_batching_header(example_pkt,3)
    # print(modified_pkt.show())
    # print(len(modified_pkt))
