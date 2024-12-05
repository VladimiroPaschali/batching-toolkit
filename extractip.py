import socket
from scapy.all import rdpcap
from tqdm import tqdm  # Importa tqdm per la barra di progresso

def estrai_ip_sorgenti_da_pcap(file_pcap, file_output):
    try:
        # Legge il file PCAP
        print(f"Lettura del file PCAP: {file_pcap}")
        pacchetti = rdpcap(file_pcap)
        print(f"Pacchetti letti: {len(pacchetti)}")
        
        # Usa un set per raccogliere gli IP sorgenti univoci
        # ip_sorgenti = set()
        ip_sorgenti = set()
        for i in tqdm(range(len(pacchetti)),desc="Estrazione IP sorgenti",unit="pkt"):
        # for pacchetti[i] in pacchetti:
            raw_bytes = bytes(pacchetti[i])
            # print(socket.inet_ntoa(raw_bytes[26:30]))
            if pacchetti[i].haslayer('IP'):  # Verifica se il pacchetti[i] ha il layer IP
               ip_sorgenti.add(pacchetti[i]['IP'].src)
            else:
                valid = int(raw_bytes[:2].hex(),16)
                if valid == 3:
                    lunghezza1 = int(raw_bytes[2:4].hex(),16)
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34:38]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1:38+lunghezza1]))
                elif valid == 7:
                    lunghezza1 = int(raw_bytes[2:4].hex(),16)
                    lunghezza2 = int(raw_bytes[4:6].hex(),16)
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34:38]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1:38+lunghezza1]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1+lunghezza2:38+lunghezza1+lunghezza2]))
                if valid == 15:
                    lunghezza1 = int(raw_bytes[2:4].hex(),16)
                    lunghezza2 = int(raw_bytes[4:6].hex(),16)
                    lunghezza3 = int(raw_bytes[6:8].hex(),16)
                    # lunghezza4 = len(raw_bytes)-8-lunghezza1-lunghezza2-lunghezza3
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34:38]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1:38+lunghezza1]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1+lunghezza2:38+lunghezza1+lunghezza2]))
                    ip_sorgenti.add(socket.inet_ntoa(raw_bytes[34+lunghezza1+lunghezza2+lunghezza3:38+lunghezza1+lunghezza2+lunghezza3]))


        # Scrivi gli IP sorgenti su un file di output
        with open(file_output, "w") as file:
            for ip in ip_sorgenti:
                file.write(ip + "\n")
        
        print(f"IP sorgenti estratti e salvati in: {file_output}")
    except Exception as e:
        print(f"Errore: {e}")

# Esempio di utilizzo
# file_pcap = "batch_ZIPF_2pkts_1flows.pcap"  # Sostituisci con il percorso del tuo file .pcap
# file_pcap = "batch_ZIPF_4pkts_1flows.pcap"  # Sostituisci con il percorso del tuo file .pcap
file_pcap= "/home/vladimiro/Pktgen-DPDK/pcap/non-batched/uniform1m100k.pcap"
# file_pcap= "UNIFORM_1pkts_1flows.pcap"
file_output = "ip_sorgenti.txt"
estrai_ip_sorgenti_da_pcap(file_pcap, file_output)
