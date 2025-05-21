from pprint import pprint
from typing import Type
from scapy.all import *
import argparse
import numpy
import random

# from pprint import print
import string
from tqdm import tqdm
from topleiz import get_input, compute_hash


from scapy.packet import Packet


class BatchingHeader(Packet):
    """definizione del formato del pacchetto di batching"""

    name = "BatchingHeader"
    fields_desc = [BitField("custom", 0, 64)]
    linktype = ETHER_TYPES


def add_batching_header(batch: list):
    """Aggiunge un header di batching ai pacchetti nel batch"""
    if len(batch) == 2:
        header = 1 << 49 | 1 << 48 | len(batch[0]) << 32 | len(batch[1]) << 16
        custom_header = BatchingHeader(custom=header)
    elif len(batch) == 3:

        header = (
            1 << 50
            | 1 << 49
            | 1 << 48
            | len(batch[0]) << 32
            | len(batch[1]) << 16
            | len(batch[2])
        )
        custom_header = BatchingHeader(custom=header)
    elif len(batch) == 4:
        header = (
            1 << 51
            | 1 << 50
            | 1 << 49
            | 1 << 48
            | len(batch[0]) << 32
            | len(batch[1]) << 16
            | len(batch[2])
        )
        custom_header = BatchingHeader(custom=header)
    else:
        header = 0 << 51 | 0 << 50 | 0 << 49 | 0 << 48
        custom_header = BatchingHeader(custom=header)
        print("Batch size non valido")

    pkt = batch[0]
    for i in range(1, len(batch)):
        pkt = pkt / batch[i]

    pkt = custom_header / pkt
    # pkt = pkt.__class__(bytes(pkt))

    return pkt


def gen_payload(size):
    """genera una stringa di dimensione size da usare come payload"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=size))


def create_flows(args, flows_packets):
    """Crea un insieme di flussi di pacchetti, ciascuno con un pacchetto di tipo diverso"""
    # print(len(flows_packets))
    if len(flows_packets) == args.n_flows:
        return flows_packets
    else:
        for i in range(args.n_flows - len(flows_packets)):
            src = str(RandIP(args.s_subnet))
            dst = str(RandIP(args.d_subnet))
            sport = int(RandShort())
            dport = int(RandShort())
            if args.l4_proto == "MIX":
                proto = random.choice(["TCP", "UDP"])
            else:
                proto = args.l4_proto

            flows_packets.add((src, dst, proto, sport, dport))
    return create_flows(args, flows_packets)


def uniform_dist(args):
    """genera una lista di indici ripetuti uniformemente da usare per scegliere i flussi lunga args.n_pkts"""
    uniform_list = []
    # Calcolare il numero di ripetizioni per ogni numero
    rep = math.ceil(args.n_pkts / args.n_flows)
    # Riempire la lista ripetendo i numeri da 0 a n_flows-1
    for i in range(args.n_flows):
        uniform_list.extend([i] * rep)
    # Troncamento della lista alla lunghezza specificata da n_pkt
    uniform_list = uniform_list[: args.n_pkts]
    random.shuffle(uniform_list)

    return uniform_list


def spacial_locality_dist(args):
    """genera una lista di indici da 0 a args.n_flows dove lo stesso ondice è ripetuto args.dist_param volte lunga args.n_pkts"""
    spacial_list = []
    while len(spacial_list) < args.n_pkts:
        spacial_list.extend(
            [i for i in range(args.n_flows) for _ in range(args.dist_param)]
        )
    return spacial_list[: args.n_pkts]


def gen_pkts_rss(args, set_flows):

    list_flows = list(set_flows)
    distr = uniform_dist(args)
    # normal_payload_size = [
    #    int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkts)
    # ]
    qpkts = [[] for _ in range(args.n_queues)]
    pkts = []
    # Inizia la barra di progresso
    for i in tqdm(
        range(0, len(distr)), desc="Generazione pacchetti uniform e hashed", unit="pkt"
    ):
        batch = []
        # Crea il batch di pacchetti

        flow = list_flows[distr[i] % args.n_flows]

        src, dst, proto, sport, dport = flow
        smac = "e8:eb:d3:78:95:8d"
        dmac = "58:a2:e1:d0:69:ce"

        # Crea pacchetto TCP o UDP
        if proto == "TCP":
            pkt = (
                Ether(src=smac, dst=dmac)
                / IP(src=src, dst=dst)
                / TCP(dport=dport, sport=sport)
                / Raw(str(i))
            )
        else:
            pkt = (
                Ether(src=smac, dst=dmac)
                / IP(src=src, dst=dst)
                / UDP(dport=dport, sport=sport)
                / Raw(str(i))
            )

        # Evita l'operazione ridondante
        pkt = pkt.__class__(bytes(pkt)) if proto == "UDP" else pkt
        pkts.append(pkt)
        key = (
            compute_hash(get_input(src, dst, int(sport), int(dport)), 12)
        ) % args.n_queues
        qpkts[key].append(pkt)

    # scompatta code rss
    hashed_pkts = []
    offset = 0
    for i in tqdm(
        range(args.n_pkts // args.locality_size),
        desc="Scompattamento code RSS",
        unit="pkt",
    ):
        for j in range(args.n_queues):
            hashed_pkts.extend(qpkts[j][offset : offset + args.locality_size])
        offset += args.locality_size

    # batch pkts
    batched_pkts = []
    for i in tqdm(
        range(0, len(pkts), args.batch_size), desc="Batching pacchetti", unit="pkt"
    ):
        batch = []
        for x in range(min(args.batch_size, args.n_pkts - i)):
            pkt = pkts[i + x]
            batch.append(pkt)

        # # Aggiunge header di batching a tutti i pacchetti tranne l'ultimo
        # for x in range(args.batch_size - 1):
        #     pkt = batch[x]
        #     next_len = len(batch[x + 1])
        #     pkt = add_batching_header(pkt, next_len) / Raw(batch[x + 1])
        #     batched_pkts.append(pkt)
        pkt = add_batching_header(batch)
        batched_pkts.append(pkt)

    # batch hashed pkts
    batched_hashed_pkts = []
    for i in tqdm(
        range(0, len(hashed_pkts), args.batch_size),
        desc="Batching pacchetti hashed",
        unit="pkt",
    ):
        batch = []
        for x in range(min(args.batch_size, args.n_pkts - i)):
            pkt = hashed_pkts[i + x]
            batch.append(pkt)

        # # Aggiunge header di batching a tutti i pacchetti tranne l'ultimo
        # for x in range(args.batch_size - 1):
        #     pkt = batch[x]
        #     next_len = len(batch[x + 1])
        #     pkt = add_batching_header(pkt, next_len) / Raw(batch[x + 1])
        #     batched_hashed_pkts.append(pkt)
        pkt = add_batching_header(batch)
        batched_hashed_pkts.append(pkt)

    return batched_hashed_pkts, batched_pkts


def batch_pcap(pkts, batch_size, batch_byte_limit ):
    """Aggiunge header di batching ai pacchetti nel batch"""
    # print(len(pkts))
    # pkts = rdpcap(pcap_file)
    # print(len(pkts))
    batched_pkts = []
    pacchetti = sorted(pkts, key=len, reverse=True)

    while pacchetti:

        best_batch = []
        best_sum = 0

        for i in tqdm( range(1, len(pacchetti) + 1), desc="Batching pacchetti", unit="pkt"):
            for combo in combinations(pacchetti, i):
                total = sum(combo)
                if total <= max_size and total > best_sum:
                    best_sum = total
                    best_batch = list(combo)
                    if best_sum == max_size:
                        break
            if best_sum == max_size:
                break

        for p in best_batch:
            pacchetti.remove(p)
        batched_pkts.append(best_batch)
    return batched_pkts


def gen_pkts(args, set_flows):
    """Genera args.n_pkts pacchetti distribuiti secondo la distribuzione zipf con parametro args.dist_param partendo dai flussi set_flows"""
    list_flows = list(set_flows)
    pkts = []

    # Scelta della distribuzione
    if args.distribution == "UNIFORM":
        distr = uniform_dist(args)
    elif args.distribution == "ZIPF":
        distr = numpy.random.zipf(a=args.dist_param, size=args.n_pkts)
    elif args.distribution == "LOCALITY":
        distr = spacial_locality_dist(args)

    smac = "e8:eb:d3:78:95:8d"
    dmac = "58:a2:e1:d0:69:ce"
    if args.fixed:
        src = "192.168.101.1"
        dst = "192.168.101.2"
        sport = 2000
        dport = 8901

    # Precalcola anche la dimensione del payload con distribuzione gaussiana
    # normal_payload_size = [int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkts)]
    total_batch_size = 0
    # Ciclo principale per creare pacchetti in batch
    for i in tqdm(
        range(0, len(distr), args.batch_size), desc="Generazione pacchetti", unit="pkt"
    ):
        batch = []

        # Crea il batch di pacchetti
        for x in range(min(args.batch_size, args.n_pkts - i)):
            flow = list_flows[distr[i + x] % args.n_flows]

            if not args.fixed:
                src, dst, proto, sport, dport = flow
            else:
                _, _, proto, _, _ = flow

            # Crea pacchetto TCP o UDP
            if proto == "TCP":
                pkt = (
                    Ether(src=smac, dst=dmac)
                    / IP(src=src, dst=dst)
                    / TCP(dport=dport, sport=sport)
                )
            else:
                pkt = (
                    Ether(src=smac, dst=dmac)
                    / IP(src=src, dst=dst)
                    / UDP(dport=dport, sport=sport)
                )
                # pkt = Ether(src=smac, dst=dmac) / IP(src=src, dst=dst) / UDP(dport=dport, sport=sport) / Raw(str(i + x)*((x+1)*40)) #payload diversi tra primo e secondo pacchetto

            # add payload
            if args.payload_size:  # add a payload of size payload_size
                pkt = pkt / Raw(str(i + x) * args.payload_size)
            elif args.pkt_size > len(pkt):
                pkt = pkt / Raw(str(i + x) * (args.pkt_size - len(pkt)))
            elif args.total_batch_size > len(
                pkt
            ):  # add much payload to the packet to fit batch_size packet in the batch
                payload_size = ((args.total_batch_size - 8) // args.batch_size) - len(
                    pkt
                )
                if payload_size < 0:
                    payload_size = 1
                pkt = pkt / Raw(str(i + x) * payload_size)
            else:
                pkt = pkt / Raw(str(i + x))

            # add len
            pkt = pkt.__class__(bytes(pkt))
            batch.append(pkt)
            total_batch_size += len(pkt)

        pkt = add_batching_header(batch)
        pkts.append(pkt)

    return pkts


def n_pkt_to_int(arg):
    mult = {"K": 1000, "M": 1000000, "G": 1000000000}

    if arg[-1] in mult:
        return int(arg[:-1]) * mult[arg[-1]]
    else:
        return int(arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--n_pkts",
        help="Numero di pacchetti da generare",
        default=10,
        type=n_pkt_to_int,
    )
    parser.add_argument(
        "--n_flows", help="Numero di flussi da generare", type=n_pkt_to_int, default=4
    )
    parser.add_argument(
        "--l4_proto",
        help="Protocollo di livello quattro, [TCP | UDP  | MIX]",
        type=str,
        default="UDP",
        choices=["TCP", "UDP", "MIX"],
    )
    parser.add_argument(
        "--dist_param",
        help="Parametro della distribuzione scelta alfa per zip o locality per locality",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--distribution",
        help="Tipo di distribuzione [ZIPF | UNIFORM | LOCALITY | RSS]",
        type=str,
        default="ZIPF",
        choices=["ZIPF", "UNIFORM", "LOCALITY", "RSS"],
    )
    parser.add_argument(
        "--output", help="Nome del file di output .pcap", type=str, default="batch"
    )
    parser.add_argument(
        "--batch_size", help="Dimensione del batch", type=int, default=2
    )
    parser.add_argument(
        "--avg_payload_size",
        help="Dimensione in valore medio del payload, è calcolata usando una distribuzione gaussiana centrata al valore passato con devstd=2",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--payload_size",
        help="Dimesione fissa del payload per ogni pacchetto",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--pkt_size",
        help="Dimensione totale del pacchetto, il valore deve essere maggiore o uguale del minimo valore, in caso contrario questo campo non verrà consdierato",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--total_batch_size",
        help="Dimensione totale del batch, il valore deve essere maggiore o uguale del minimo valore, in caso contrario questo campo non verrà consdierato",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--s_subnet", help="Subnet IP sorgente", type=str, default="0.0.0.0/0"
    )
    parser.add_argument(
        "--d_subnet", help="Subnet IP destinazione", type=str, default="0.0.0.0/0"
    )
    parser.add_argument(
        "--fixed",
        help="Set fixed value for dmac, smac, dport, sport",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "--n_queues",
        help="Numero di queues diverse per la suddivisione per hash",
        type=n_pkt_to_int,
        default=2,
    )
    parser.add_argument(
        "--locality_size",
        help="Parametro della selezione dei pacchetti vicini o del numero di pacchetti scelti per ogni queue",
        type=n_pkt_to_int,
        default=2,
    )

    parser.add_argument("--pcap", help="File pcap di input", type=str)
    parser.add_argument(
        "--batch-size-limit",
        help="Limite della dimensione del batch",
        type=int,
        default=0,
    )

    args = parser.parse_args()

    # bind_bottom_up(BatchingHeader, Ether, type=0x1234)
    # bind_top_down(BatchingHeader, Ether, type=0x1234)

    # test args
    # args.distribution ="LOCALITY"
    # args.dist_param = 2
    # args.n_pkts = 10
    # args.n_flows = 10
    # args.batch_size= 2

    conf.l2types.register(
        1, BatchingHeader
    )  # Assegna il numero 1 al tuo BatchingHeader
    output_filename = (
        f"{args.output}_{args.distribution}_{args.n_pkts}pkts_{args.n_flows}flows.pcap"
    )

    if args.pcap:
        pkts = rdpcap(args.pcap)
        print("pcap loaded...")
        batched_pkts = batch_pcap(pkts, args.batch_size, args.batch_size_limit)
        print("Writing pcap...")
        wrpcap(output_filename, batched_pkts)
    else:
        flows_packets = set()
        flows_packets = create_flows(args, flows_packets)
    # print(flows_packets)


    if args.distribution == "RSS":
        hashed_pkts, pkts = gen_pkts_rss(args, flows_packets)
        print("Writing pcap1...")
        wrpcap(output_filename, pkts)
        print("Writing pcap2...")
        wrpcap(f"hashed_{output_filename}", hashed_pkts)
    else:
        pkts = gen_pkts(args, flows_packets)
        print("Writing pcap...")
        wrpcap(output_filename, pkts)

    # bind_layers( BatchingHeader, Ether, {'type':0} )

    # conf.l2types.register(BatchingHeader, 1)  # Assegna il numero 147 al tuo BatchingHeader
    # # print(conf.l2types)
    # pcap_writer = PcapWriter("batching_packet.pcap", linktype=1)  # 1 è il tipo Ethernet
    # pcap_writer.write(pkts)
    # pcap_writer.close()

    # Esempio di utilizzo della funzione modify_ethernet
    # example_pkt = Ether() / IP(dst="192.168.1.1") / UDP(dport=12345, sport=54321)/Raw(load=gen_payload(10))
    # print(example_pkt.__class__)
    # modified_pkt = add_batching_header(example_pkt,3)
    # print(modified_pkt.show())
    # print(len(modified_pkt))
