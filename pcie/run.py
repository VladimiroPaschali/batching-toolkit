import csv
import os
import shlex
from time import sleep
import subprocess as sp
import json
import pandas as pd

def _load_program(program_path: str, ifname: str, logpath:str) -> sp.Popen:
    command = f"sudo {program_path} {ifname}"
    #shell false permette di fare process.terminate()
    #pipare o out o err se no si rompe la shell
    process = sp.Popen(shlex.split(command),stdout=sp.PIPE,text=True)
    print(f"Running program: {os.path.basename(program_path)}")
    _append_to_log(logpath, f"Running program: {os.path.basename(program_path)}\n")

    sleep(1)
   
    return process

def _term_program(process: sp.Popen, logpath:str) -> int:

    process.terminate()
    print(f"program terminated")
    _append_to_log(logpath, process.stdout.read())
    _append_to_log(logpath, "program terminated\n")
    return 0

def _append_to_log(log_path: str, data: str) -> int:
    with open(log_path, "a") as f:
        f.write(data)
    return 0

def _clear_file(log_path: str) -> int:
    with open(log_path, "w") as f:
        pass
    return 0

def _load_config(configpath) -> dict:
    try:
        with open(configpath, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config not found")
        return -1
    return config

def _pmc_pci(csvpath: str,logpath:str, pmciterations:int) -> int:
    command = f"sudo pcm-pcie -e -i={pmciterations} -csv={csvpath}"
    _append_to_log(logpath, f"Running command: {command}\n")
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
    except sp.CalledProcessError as e:
        print(f"Error {command}")
        _append_to_log(logpath, f"Error {command}\n")
        return -1
    
def _parse_pmc_csv(csvpath: str, logpath :str, progam_name: str, pmciterations:int, throughput) -> int:
    
    df = pd.read_csv(csvpath, header=None, dtype=str)  # Leggi tutti i dati come stringhe

    total_rows = df[df[7].str.contains(r'\(Total\)', na=False)].iloc[:, :7]    
    total_rows = total_rows.apply(pd.to_numeric, errors='coerce')
    total_grouped = [total_rows.iloc[i:i + pmciterations] for i in range(0, len(total_rows), pmciterations)]
    total_avg = [group.mean(skipna=True).round().astype(int) for group in total_grouped]
    # total_avg = [group.max(skipna=True).round().astype(int) for group in total_grouped]
    total_avg = [total_avg[0][i] for i in range(len(total_avg[0]))]
    total_avg = [progam_name, throughput, "Total"] + total_avg
    

    hit_rows = df[df[7].str.contains(r'\(Hit\)', na=False)].iloc[:, :7]
    hit_rows = hit_rows.apply(pd.to_numeric, errors='coerce')
    hit_grouped = [hit_rows.iloc[i:i + pmciterations] for i in range(0, len(hit_rows), pmciterations)]
    hit_avg = [group.mean(skipna=True).round().astype(int) for group in hit_grouped]
    # hit_avg = [group.max(skipna=True).round().astype(int) for group in hit_grouped]
    hit_avg = [hit_avg[0][i] for i in range(len(hit_avg[0]))]
    hit_avg = [progam_name, throughput, "Hit"] + hit_avg



    miss_rows = df[df[7].str.contains(r'\(Miss\)', na=False)].iloc[:, :7]
    miss_rows = miss_rows.apply(pd.to_numeric, errors='coerce')
    miss_grouped = [miss_rows.iloc[i:i + pmciterations] for i in range(0, len(miss_rows), pmciterations)]
    miss_avg = [group.mean(skipna=True).round().astype(int) for group in miss_grouped]
    # miss_avg = [group.max(skipna=True).round().astype(int) for group in miss_grouped]
    miss_avg = [miss_avg[0][i] for i in range(len(miss_avg[0]))]
    miss_avg = [progam_name, throughput, "Miss"] + miss_avg


    _avg_csv(total_avg, hit_avg, miss_avg)

    print(f"Program {progam_name} added to result.csv")
    _append_to_log(logpath, f"Program {progam_name} added to result.csv\n")
    
    return

def _avg_csv(total_avg, hit_avg, miss_avg):
    resultpath = "result.csv"
    with open(resultpath, "a",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(total_avg)
        writer.writerow(hit_avg)
        writer.writerow(miss_avg)
    return

def _init_csv() -> int:
    rows = ["Program", "Throughput","Type","Skt", "PCIRdCur", "ItoM", "ItoMCacheNear", "UCRdF", "WiL", "WCiL"]
    resultpath = "result.csv"
    with open(resultpath, "w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(rows)
    return

def _compute_throughput(ioctlpath:str, time:int) -> int:
    command = f"sudo {ioctlpath} 3 {time}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error ./ioctl 3 {time} command")
        return -1
    
    return int(result.stdout)

def _batched(ioctlpath ,batch) -> int:

    ioctlval = int(batch)
    command = f"sudo {ioctlpath} {ioctlval}"
    print(command)
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error ./ioctl {ioctlval} command")
        return -1
    
    return 0



def main():

    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    
    configpath = "config.json"
    # configpath = "configBatched.json"

    config = _load_config(configpath)
    logpath = "log.txt"
    csvpath = "pcm.csv"
    ioctlpath = os.path.join(os.path.abspath(config["ioctl-dir"]), "ioctl")
    ifname = config["ifname"]
    absolute_path = os.path.abspath(config["exp-dir"])
    pmciterations = config["pmc-iterations"]

    #sets ioctl if batched mode else resets
    _batched(ioctlpath,config["batched"])

    _clear_file(logpath)
    _init_csv()
    for program in config["progs"]:

        program_path=os.path.join(absolute_path, program["path"])
        program_name = program["name"]

        process = _load_program(program_path, ifname, logpath)

        _pmc_pci(csvpath,logpath, pmciterations)

        throughput = _compute_throughput(ioctlpath, time=1)

        _parse_pmc_csv(csvpath, logpath, program_name, pmciterations , throughput)

        _term_program(process, logpath)


if __name__ == "__main__":
    main()


