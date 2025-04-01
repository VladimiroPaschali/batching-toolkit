import csv
import json
import os
import re
import shlex
import signal
import subprocess as sp
import numpy as np
from time import sleep
from hooks import before_exp, after_exp
import psutil


def _load_program(program_path: str, ifname: str, logpath:str, vargs) -> sp.Popen:
    command = f"sudo {program_path} {ifname} {vargs}"
    print(command)
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

def _init_csv(csv_path: str, suite_cfg:str) -> int:
    fields = []
    if suite_cfg.get("budget", False):
        fields.append("budget")
        fields.append("rxqueue")
    fields.append("program")
    if "all_results.csv" in csv_path:
        fields.append("repetition")
    if suite_cfg["throughput"]:
        fields.append("throughput")
        fields.append("std")
    if suite_cfg["bandwidth"]:
        fields.append("bandwidth")
    if suite_cfg["perfIPC"]:
        fields.append("IPC")
    if suite_cfg["perfCacheMisses"]:
        fields.append("CacheMisses")
    if suite_cfg["perfIPP"]:
        fields.append("IPP")
    if suite_cfg["perfBranchMisses"]:
        fields.append("perfBranchMisses")
    if suite_cfg.get("perfTLBMisses", False):
        fields.append("perfTLBMisses")
    if suite_cfg.get("cpuUsage", False):
        fields.append("cpuUsage")
    if suite_cfg.get("perfL1Rateo", False):
        fields.append("perfL1Rateo")
    if suite_cfg.get("perfL3Rateo", False):
        fields.append("perfL3Rateo")
    if suite_cfg.get("perfTLBRateo", False):
        fields.append("perfTLBRateo")
    if suite_cfg.get("interrupt", False):
        fields.append("interrupt")
    with open(csv_path, "w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)

def _append_to_csv(csv_path: str, data: list) -> int:
    with open(csv_path, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def _get_dropped_ethtool(ifname:str) -> int:
    command = f"sudo ethtool -S {ifname}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
    except sp.CalledProcessError as e:
        print(f"Error {command}")
        return -1
    match = re.search(r'rx_xdp_drop:\s*(\d+)', result.stdout)
    return int(match.group(1))

def _compute_throughput(ifname:str, time:int) -> int:
    
    pre = _get_dropped_ethtool(ifname)
    sleep(time)
    post = _get_dropped_ethtool(ifname)
    return post - pre


def _compute_bandwidth(ioctlpath:str, time:int) -> int:
    command = f"sudo {ioctlpath} 4 {time}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error ./ioctl 4 {time} command")
        return -1
    
    return (int(result.stdout)*8)/(2**20)

def _bpftool_id(name):
    command = f"sudo bpftool prog show name {name}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error bpftool prog show command")
        return -1
        
    match = re.search(r'(\d+):\s*xdp', result.stdout)
    if match:
        return int(match.group(1))
    else:
        return -1

# def _perf_ipc(cpu,time) -> int:
def _perf_ipc(time, name) -> int:

    # command = f"sudo perf stat -e cycles:k,instructions:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command = f"sudo perf_bpf stat -b {bpftool_id} -e cycles,instructions --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
        # print(result.stderr)
    except sp.CalledProcessError as e:
        print("Error perf IPC command")
        return -1
    
    match = re.search(r'([\d.]+)\s+insn per cycle', result.stderr)
    if match:
        return float(match.group(1))
    else:
        print(result.stderr)
        return -1
    
def _perf_branch_misses(time, name) -> int:

    # command = f"sudo perf stat -e cycles:k,instructions:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command = f"sudo perf_bpf stat -b {bpftool_id} -e branch-misses --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
        # print(result.stderr)
    except sp.CalledProcessError as e:
        print("Error perf IPC command")
        return -1
    
    match = re.search(r'([\d.]+)\s+branch-misses', result.stderr)
    if match:
        return float(match.group(1))
    else:
        print(result.stderr)
        return -1
    
# def _perf_cache_misses(cpu, time) -> int:
def _perf_cache_misses(time, name) -> int:

    # command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e L1-dcache-load-misses --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1
    # print(result.stderr)

    match1 = re.search(r'([\d,]+)\s+L1-dcache-load-misses', result.stderr)
    cache_misses = int(match1.group(1).replace(",","")) if match1 else -1

    match2 = re.search(r'run:\s*(\d+)', result.stderr)
    run_count = int(match2.group(1)) if match2 else -1

    return cache_misses/run_count

def _perf_tlb_misses(time, name) -> int:

    # command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e dTLB-load-misses --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1
    # print(result.stderr)

    match1 = re.search(r'([\d,]+)\s+dTLB-load-misses', result.stderr)
    cache_misses = int(match1.group(1).replace(",","")) if match1 else -1

    match2 = re.search(r'run:\s*(\d+)', result.stderr)
    run_count = int(match2.group(1)) if match2 else -1

    return cache_misses/run_count

def _perf_l1_rateo(time, name) -> float:

    # command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e L1-dcache-load-misses,L1-dcache-load --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1

    match = re.search(r"#\s+([\d.]+)%", result.stderr)
    rateo = float(match.group(1)) if match else -1

    return rateo

def _perf_l3_rateo(time, name) -> float:

    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e LLC-load-misses,LLC-load --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1

    match = re.search(r"#\s+([\d.]+)%", result.stderr)
    rateo = float(match.group(1)) if match else -1

    return rateo

def _perf_tlb_rateo(time, name) -> float:

    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e dTLB-load-misses,dTLB-loads --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1
    # print(result.stderr)

    match = re.search(r"#\s+([\d.]+)%", result.stderr)
    rateo = float(match.group(1)) if match else -1

    return rateo


def _perf_ipp(ioctlpath:str,cpu, time, cfg_fpga:bool) -> int:

    pkts = _compute_throughput(ioctlpath, time, cfg_fpga)

    command = f"sudo perf stat -e instructions:k -C {cpu} --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
        # print(result.stderr)

    except sp.CalledProcessError as e:
        print("Error perf IPC command")
        return -1
    
    match = re.search(r'([\d,]+)\s+instructions', result.stderr)
    instructions = int(match.group(1).replace(",","")) if match else -1
    # print(f"Instructions: {instructions}")
    return instructions/pkts



def _budget(budgetIndex:int, ifname:str, rxqueue:list, txqueue:list) -> int:
    # rxqueue = [128, 256, 512, 1024, 2048, 4096, 8192]
    # txqueue = [2, 4, 8, 16, 32, 64, 128, 256, 512] #budget

    if budgetIndex >  len(rxqueue)*len(txqueue):
        print("Core out of range")
        return -1

    command = f"sudo ethtool -G {ifname} rx {rxqueue[(budgetIndex)%len(rxqueue)]} tx {txqueue[(budgetIndex)//len(rxqueue)]}"
    print(command)

    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
        # print(result.stderr)
    except sp.CalledProcessError as e:
        print("Error budget command")
        return -1

    sleep(1)
    return 0

def _cpu_usage(time:int, core:int) -> int:
    
    cpus = psutil.cpu_percent(interval=time, percpu=True)
    # print (cpus[core])
    return cpus[core]

def _read_interrupt():
    command = 'grep "^119:" /proc/interrupts'
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
    except sp.CalledProcessError as e:
        print("Error interrupt command")
        return -1
        
    match = re.search(r"\d+:\s+(\d+)", result.stdout)
    interrupt = int(match.group(1)) if match else -1
    return interrupt
    
def _interrupt(time:int) -> int:
    pre=_read_interrupt()
    sleep(time)
    post=_read_interrupt()
    return post-pre

    


def run_suite(suite_cfg:json, name:str) -> int:

    absolute_path = os.path.abspath(suite_cfg["exp-dir"])
    ifname = suite_cfg["ifname"]
    logpath = os.path.join(os.getcwd(),"suites", name, "log.txt")
    ioctlpath = os.path.join(os.path.abspath(suite_cfg["ioctl-dir"]), "ioctl")
    csvpath = os.path.join(os.getcwd(),"suites", name, "results.csv")
    allcsvpath = os.path.join(os.getcwd(),"suites", name, "all_results.csv")
    time = suite_cfg["time"]
    cpu = suite_cfg["cpu"]
    repetitions = suite_cfg["repetitions"]

    cfg_fpga = suite_cfg.get("fpga", False)
    # cfg_multicore = suite_cfg.get("multicore", 1)
    cfg_ethtool = suite_cfg.get("ethtool", False)
    cfg_budget = suite_cfg.get("budget", False)
    
    
    #clear csv and sets up fiels
    _init_csv(csvpath, suite_cfg)
    _init_csv(allcsvpath, suite_cfg)

    #clear logfile
    _clear_file(logpath)

    csvdata =[]
    allcsvdata = []

    rxqueue = [128, 256, 512, 1024, 2048, 4096, 8192]
    txqueue = [2, 4, 8, 16, 32, 64, 128, 256, 512] #budget

    repetition = 0
    change_budget = False

    budgetIndex = 0
    if cfg_budget:
        range_budget = len(rxqueue)*len(txqueue)
        if _budget(budgetIndex, ifname, rxqueue, txqueue) < 0:
            return -1
    else:
        range_budget = 1

                    

    # for budgetIndex in range(0,range_budget):

    for program in suite_cfg["progs"]:
        program_path=os.path.join(absolute_path, program["path"])
        program_name = program["name"]
        vargs = program.get("args", "")
        if vargs:
            vargs=vargs.replace("@", absolute_path)

        avg_throughput=[]
        avg_ipc=[]
        avg_ipp=[]
        avg_cache_misses=[]
        avg_bandwidth=[]
        avg_branch_misses=[]
        avg_tlb_misses=[]
        avg_core_usage=[]
        avg_l1_rateo=[]
        avg_l3_rateo=[]
        avg_tlb_rateo=[]
        avg_interrupt=[]


        # # csvdata = [program_name]
        # if cfg_budget:
        #     #budget
        #     csvdata.append(txqueue[(budgetIndex)//len(rxqueue)])
        #     #rxqueue
        #     csvdata.append(rxqueue[(budgetIndex)%len(rxqueue)])
        # csvdata.append(program_name)
        
        before_exp(suite_cfg)

        process = _load_program(program_path, ifname, logpath, vargs)

        while True:
            if cfg_budget:
                if budgetIndex >= range_budget:
                    break
                allcsvdata.append(txqueue[(budgetIndex)//len(rxqueue)]) #budget
                allcsvdata.append(rxqueue[(budgetIndex)%len(rxqueue)]) #rxqueue
            allcsvdata.append(program_name)

            repetition += 1
            allcsvdata.append(repetition)

            throughput = _compute_throughput(ifname,time= 1) // 1
            avg_throughput.append(throughput)
            allcsvdata.append(throughput)
            allcsvdata.append(0) # used for std
            _append_to_log(logpath, f"Throughput: {throughput} packets/s\n")
            print(f"Throughput: {throughput} packets/s")

            if suite_cfg.get("interrupt", False):
                    interrupt = _interrupt(time=1)
                    avg_interrupt.append(interrupt)
                    allcsvdata.append(interrupt)
                    _append_to_log(logpath, f"Interrupts: {interrupt}\n")
                    print(f"Interrupts: {interrupt}")

            _append_to_csv(allcsvpath, allcsvdata)
            allcsvdata = []


            if throughput < 100 and change_budget:
                change_budget = False
                print("Throughput < 100, changing budget")
                avg_std = np.std(avg_throughput)
                avg_throughput = np.mean(avg_throughput)

                if cfg_budget:
                    csvdata.append(txqueue[(budgetIndex)//len(rxqueue)]) #budget
                    csvdata.append(rxqueue[(budgetIndex)%len(rxqueue)]) #rxqueue
                csvdata.append(program_name)

                csvdata.append(avg_throughput)
                csvdata.append(avg_std)

                _append_to_log(logpath, f"Average throughput: {avg_throughput} packets/s std : {avg_std}\n")
                print(f"Average throughput: {avg_throughput} packets/s std : {avg_std}")

                if suite_cfg.get("interrupt", False):
                    avg_interrupt = sum(avg_interrupt) / repetitions
                    csvdata.append(avg_interrupt)
                    _append_to_log(logpath, f"Average Interrupts: {avg_interrupt}\n")

                _append_to_csv(csvpath, csvdata)
                #svuota tra ripetizioni
                csvdata = []
                avg_throughput=[]
                avg_interrupt=[]

                if cfg_budget:
                    if _budget(budgetIndex, ifname, rxqueue, txqueue) < 0:
                        break
                    else:
                        budgetIndex += 1
            if throughput > 100:
                change_budget = True


        _term_program(process, logpath)
        after_exp(suite_cfg)

           


    return 0