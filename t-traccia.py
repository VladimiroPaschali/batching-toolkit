from trex.stl.api import STLClient, STLStream, STLPcap, STLTXCont

import sys

argc = len(sys.argv) 
# Parametri di configurazione
pcap_file = sys.argv[1] 
mul = sys.argv[2] if sys.argv[1].startswith("-m") else 100
trex_server_ip = '0.0.0.0'          # Indirizzo IP del server TRex
interface_ports = [0]                    # Lista delle porte fisiche su cui inviare i pacchetti

# Crea il client TRex
client = STLClient(server=trex_server_ip)

try:
    # Connetti al server TRex
    client.connect()

    # Configura lo stream
    pcap = STLPcap(pcap_file)
    stream = STLStream(packet=pcap, mode=STLTXCont(percentage=mul))  # Configura per inviare in loop infinito

    # Carica lo stream sulla porta specificata
    client.add_streams(stream, ports=interface_ports)

    # Avvia il traffico
    print("Inizio dell'invio del traffico in loop infinito.")
    client.start(ports=interface_ports, force=True)

    # Mantieni il traffico in esecuzione
    client.wait_on_traffic(ports=interface_ports)

except Exception as e:
    print(f"Errore: {e}")
finally:
    # Disconnetti il client
    client.disconnect()
    print("Client disconnesso.")

