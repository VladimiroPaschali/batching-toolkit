def unisci_file_in_insieme(file1, file2, file3, file4, file_output):
    try:
        # Insieme per raccogliere righe senza duplicati
        righe_uniche = set()

        # Leggi le righe da ciascun file
        for file_name in [file1, file2, file3, file4]:
            print(f"Lettura del file: {file_name}")
            with open(file_name, "r") as f:
                for linea in f:
                    righe_uniche.add(linea.strip())  # Rimuove spazi bianchi e duplicati

        # Scrivi le righe uniche nel file di output
        with open(file_output, "w") as f:
            for riga in sorted(righe_uniche):  # Ordina le righe (opzionale)
                f.write(riga + "\n")

        print(f"Righe uniche scritte nel file: {file_output}")
    except Exception as e:
        print(f"Errore: {e}")

# Esempio di utilizzo
file1 = "ip_sorgenti1.txt"
file2 = "ip_sorgenti2.txt"
file3 = "ip_sorgenti3.txt"
file4 = "ip_sorgenti4.txt"
file_output = "output_unificato.txt"

unisci_file_in_insieme(file1, file2, file3, file4, file_output)
