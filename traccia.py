from typing import Type
from scapy.all import *
import argparse
import numpy
import random
from pprint import pprint
from topleiz import get_input, compute_hash
from tqdm import tqdm  # Importa tqdm per la barra di progresso
import string
from scapy.packet import Packet


def gen_payload(size):
    """genera una stringa di dimensione size da usare come payload"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=size))


def create_flows(args, flows_packets):
    """Crea un insieme di flussi di pacchetti, ciascuno con un pacchetto di tipo diverso"""
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
    """genera una lista di indici ripetuti uniformemente da usare per scegliere i flussi lunga args.n_pkts"""
    uniform_list = []
    rep = math.ceil(args.n_pkts / args.n_flows)
    for i in range(args.n_flows):
        uniform_list.extend([i] * rep)
    uniform_list = uniform_list[: args.n_pkts]
    random.shuffle(uniform_list)

    return uniform_list


def spacial_locality_dist(args):
    """genera una lista di indici da 0 a args.n_flows dove lo stesso indice è ripetuto args.locality_size volte lunga args.n_pkts"""
    spacial_list = []
    while len(spacial_list) < args.n_pkts:
        spacial_list.extend(
            [i for i in range(args.n_flows) for _ in range(args.locality_size)]
        )
    return spacial_list[: args.n_pkts]


def gen_pktss(args, set_flows):
    """Genera args.n_pkts pacchetti distribuiti secondo la distribuzione zipf con parametro args.locality_size partendo dai flussi set_flows"""
    list_flows = list(set_flows)

    distr = uniform_dist(args)

    normal_payload_size = [
        int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkts)
    ]
    qpkts = [[] for _ in range(args.n_queues)]
    pkts = []

    # Inizia la barra di progresso
    for i in tqdm(
        range(0, len(distr)), desc="Generazione pacchetti uniform", unit="pkt"
    ):
        flow = list_flows[distr[i] % args.n_flows]
        src, dst, proto, sport, dport = flow

        key = (
            compute_hash(get_input(src, dst, int(sport), int(dport)), 12)
        ) % args.n_queues

        if proto == "TCP":
            pkt = (
                Ether()
                / IP(src=src, dst=dst)
                / TCP(dport=int(dport), sport=int(sport))
                / Raw(load=gen_payload(normal_payload_size[i]))
            )
        else:
            pkt = (
                Ether()
                / IP(src=src, dst=dst)
                / UDP(dport=int(dport), sport=int(sport))
                / Raw(load=gen_payload(normal_payload_size[i]))
            )

        qpkts[key].append(pkt)
        pkts.append(pkt)

    output_pkts = []
    offset = 0  # Devi inizializzare offset prima dell'uso
    for i in range(args.n_pkts // args.locality_size):
        for j in range(args.n_queues):
            output_pkts.extend(qpkts[j][offset : offset + args.locality_size])
        offset += args.locality_size

    return output_pkts, pkts


def gen_pktss_chiesa(args, set_flows):
    """Genera args.n_pkts pacchetti distribuiti secondo la distribuzione zipf con parametro args.locality_size partendo dai flussi set_flows"""
    list_flows = list(set_flows)

    distr = spacial_locality_dist(args)

    normal_payload_size = [
        int(random.normalvariate(args.payload_size, 2)) for _ in range(args.n_pkts)
    ]
    pkts = []

    # Inizia la barra di progresso
    for i in tqdm(
        range(0, len(distr)), desc="Generazione pacchetti locality", unit="pkt"
    ):
        flow = list_flows[distr[i] % args.n_flows]
        src, dst, proto, sport, dport = flow

        if proto == "TCP":
            pkt = (
                Ether()
                / IP(src=src, dst=dst)
                / TCP(dport=int(dport), sport=int(sport))
                / Raw(load=gen_payload(normal_payload_size[i]))
            )
        else:
            pkt = (
                Ether()
                / IP(src=src, dst=dst)
                / UDP(dport=int(dport), sport=int(sport))
                / Raw(load=gen_payload(normal_payload_size[i]))
            )

        pkts.append(pkt)

    return pkts


def n_pkts_to_int(arg):
    mult = {"K": 1000, "M": 1000000, "G": 1000000000}

    if arg[-1] in mult:
        return int(arg[:-1]) * mult[arg[-1]]
    else:
        return int(arg)


def n_flows_to_int(arg):
    mult = {"K": 1000, "M": 1000000, "G": 1000000000}

    if arg[-1] in mult:
        return int(arg[:-1]) * mult[arg[-1]]
    else:
        return int(arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generatore di tracce di pacchetti")

    parser.add_argument(
        "--n_pkts",
        help="Numero di pacchetti da generare",
        default=100,
        type=n_pkts_to_int,
    )
    parser.add_argument(
        "--n_flows",
        help="Numero di flussi da generare",
        type=n_flows_to_int,
        default=40,
    )
    parser.add_argument(
        "--l4_proto",
        help="Protocollo di livello quattro, [TCP | UDP  | MIX]",
        type=str,
        default="MIX",
        choices=["TCP", "UDP", "MIX"],
    )
    parser.add_argument(
        "--locality_size",
        help="Parametro della selezione dei pacchetti vicini o del numero di pacchetti scelti per ogni queue",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--distribution",
        help="Tipo di distribuzione [ZIPF | UNIFORM | LOCALITY]",
        type=str,
        default="LOCALITY",
        choices=["ZIPF", "UNIFORM", "LOCALITY"],
    )
    parser.add_argument(
        "--output", help="Nome del file di output .pcap", type=str, default="batch"
    )
    parser.add_argument(
        "--payload_size",
        help="Dimensione in valore medio del payload, è calcolata usando una distribuzione gaussiana centrata al valore passato con devstd=2",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--s_subnet", help="Subnet IP sorgente", type=str, default="0.0.0.0/0"
    )
    parser.add_argument(
        "--d_subnet", help="Subnet IP destinazione", type=str, default="0.0.0.0/0"
    )
    parser.add_argument(
        "--n_queues",
        help="Numero di queues diverse per la suddivisione per hash",
        type=int,
        default=2,
    )

    args = parser.parse_args()

    flows_pkts = set()
    flows = create_flows(args, flows_pkts)

    output_filename = (
        f"{args.output}_{args.distribution}_{args.n_pkts}pkts_{args.n_flows}flows.pcap"
    )

    # hashed
    if args.distribution == "UNIFORM":
        output_pkts, pkts = gen_pktss(args, flows)
        offset = 0
        print("Writing pcap...")
        wrpcap(output_filename, pkts)
        wrpcap(f"hashed_{output_filename}", output_pkts)
    else:
        output_pkts = gen_pktss_chiesa(args, flows)
        print("Writing pcap...")
        wrpcap(f"chiesa_{output_filename}", output_pkts)

    pass
