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

# SUITE_PATH = "suites"
# def _load_config(suite_path: str) -> dict:
#     try:
#         with open(f"{suite_path}/conf.json", "r") as f:
#             config = json.load(f)
#     except FileNotFoundError:
#         print("Config not found")
#         return 1
#     return config

def _load_program(program_path: str, ifname: str, logpath:str, vargs) -> sp.Popen:
    command = f"sudo {program_path} {ifname} {vargs}"
    # command = f"sudo taskset -c 0 {program_path} {ifname} {vargs}"
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
    if suite_cfg.get("perfTLBStores", False):
        fields.append("perfTLBStores")
    if suite_cfg.get("perfTLBStoreMisses", False):
        fields.append("perfTLBStoreMisses")
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

def _get_rx_pkts_ethtool(ifname:str) -> int:
    command = f"sudo ethtool -S {ifname}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
    except sp.CalledProcessError as e:
        print(f"Error {command}")
        return -1
    match = re.search(r'rx_packets:\s*(\d+)', result.stdout)
    return int(match.group(1))

def _compute_throughput_rx(ifname:str, time:int) -> int:
    pre = _get_rx_pkts_ethtool(ifname)
    sleep(time)
    post = _get_rx_pkts_ethtool(ifname)
    return post - pre


def _get_redirect_ethtool(ifname:str) -> int:
    command = f"sudo ethtool -S {ifname}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)
    except sp.CalledProcessError as e:
        print(f"Error {command}")
        return -1
    match = re.search(r'rx_xsk_xdp_redirect:\s*(\d+)', result.stdout)
    return int(match.group(1))

def _compute_throughput_redirect(ifname:str, time:int) -> int:
    pre = _get_redirect_ethtool(ifname)
    sleep(time)
    post = _get_redirect_ethtool(ifname)
    return post - pre

def _compute_throughput_ethtool(ifname:str, time:int) -> int:
    
    pre = _get_dropped_ethtool(ifname)
    sleep(time)
    post = _get_dropped_ethtool(ifname)
    return post - pre

def _compute_throughput(ioctlpath:str, time:int, cfg_fpga:bool, cfg_ethtool:bool,cfg_xdp:bool, ifname:str) -> int:
    #se fpga è true c = "" altrimenti c = ""

    if cfg_ethtool and cfg_xdp=="afxdp":
        return _compute_throughput_redirect(ifname, time)
    elif cfg_ethtool and not cfg_xdp:
        return _compute_throughput_rx(ifname, time)
    elif cfg_ethtool and cfg_xdp:
        return _compute_throughput_ethtool(ifname, time)
    else:
        if cfg_fpga:
            command = f"sudo {ioctlpath} -c 3 -w {time}"
        else:
            command = f"sudo {ioctlpath} 3 {time}"
            print(command)
        try:
            result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

        except sp.CalledProcessError as e:
            print(f"Error ./ioctl 3 {time} command")
            return -1
        
        return int(result.stdout)

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


def _perf_tlb_stores(time, name) -> int:

    # command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e dTLB-stores --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1
    # print(result.stderr)

    match1 = re.search(r'([\d,]+)\s+dTLB-stores', result.stderr)
    cache_misses = int(match1.group(1).replace(",","")) if match1 else -1

    match2 = re.search(r'run:\s*(\d+)', result.stderr)
    run_count = int(match2.group(1)) if match2 else -1

    return cache_misses/run_count

def _perf_tlb_store_misses(time, name) -> int:

    # command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"
    bpftool_id = _bpftool_id(name)
    command= f"sudo perf_bpf stat -b {bpftool_id} -e dTLB-store-misses --timeout {time*1000}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf cache misses command")
        return -1
    # print(result.stderr)

    match1 = re.search(r'([\d,]+)\s+dTLB-store-misses', result.stderr)
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
    # command= f"sudo perf_bpf stat -b {bpftool_id} -e dTLB-load-misses,dTLB-loads --timeout {time*1000}"
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

def _batched(ioctlpath:str ,cfg_batch:bool) -> int:

    ioctlval = int(cfg_batch)
    command = f"sudo {ioctlpath} {ioctlval}"
    print(command)
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error ./ioctl {ioctlval} command")
        return -1
    
    return 0

def _batched_fpga(ioctlpath:str ,cfg_batch:bool) -> int:
    if cfg_batch:
        command = f"sudo {ioctlpath} -c 1"
        try:
            print(command)
            result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

        except sp.CalledProcessError as e:
            print(f"Error {command}")
            return -1
        
        command = f"sudo {ioctlpath} -c 4"
        
    else:
        command = f"sudo {ioctlpath} -c 0"
    try:
        print(command)
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error {command}")
        return -1


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
    cfg_batched = suite_cfg.get("batched", False)
    # cfg_multicore = suite_cfg.get("multicore", 1)
    cfg_ethtool = suite_cfg.get("ethtool", False)
    cfg_budget = suite_cfg.get("budget", False)
    cfg_xdp = suite_cfg.get("xdp", True)    
    
    #clear csv and sets up fiels
    _init_csv(csvpath, suite_cfg)
    _init_csv(allcsvpath, suite_cfg)

    #clear logfile
    _clear_file(logpath)

    #sets ioctl if batched mode else resets
    if cfg_fpga:
        # _batched_fpga(ioctlpath,batched)
        pass
    else:
        _batched(ioctlpath,cfg_batched)

    csvdata =[]
    allcsvdata = []

    # rxqueue = [128, 256, 512, 1024, 2048, 4096, 8192]
    # txqueue = [2, 4, 8, 16, 32, 64, 128, 256, 512] #budget
    rxqueue = [128, 256, 512, 1024, 2048, 4096, 8192]
    txqueue = [8,16,32, 64, 128, 256, 512] #budget

    if cfg_budget:
        range_budget = len(rxqueue)*len(txqueue)
    else:
        range_budget = 1

    for budgetIndex in range(0,range_budget):
        # if cfg_budget:
        #     if _budget(budgetIndex, ifname, rxqueue, txqueue) < 0:
        #         break
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
            avg_tlb_store=[]
            avg_tlb_store_misses=[]
            avg_core_usage=[]
            avg_l1_rateo=[]
            avg_l3_rateo=[]
            avg_tlb_rateo=[]
            avg_interrupt=[]


            # csvdata = [program_name]
            if cfg_budget:
                #budget
                csvdata.append(txqueue[(budgetIndex)//len(rxqueue)])
                #rxqueue
                csvdata.append(rxqueue[(budgetIndex)%len(rxqueue)])
            csvdata.append(program_name)
            
            before_exp(suite_cfg)

            for repetition in range(repetitions):

                # allcsvdata = [program_name]
                if cfg_budget:
                    allcsvdata.append(rxqueue[(budgetIndex)%len(rxqueue)])
                    allcsvdata.append(txqueue[(budgetIndex)//len(rxqueue)])
                allcsvdata.append(program_name)
                allcsvdata.append(repetition+1)

                process = _load_program(program_path, ifname, logpath, vargs)

                if cfg_budget:
                    if _budget(budgetIndex, ifname, rxqueue, txqueue) < 0:
                        break

                _append_to_log(logpath, f"Repetition: {repetition+1}\n")
                print(f"Repetition: {repetition+1}")

                if suite_cfg["throughput"]:
                    throughput = _compute_throughput(ioctlpath, time, cfg_fpga, cfg_ethtool,cfg_xdp, ifname) // time 
                    avg_throughput.append(throughput)
                    allcsvdata.append(throughput)
                    allcsvdata.append(0) # used for std
                    _append_to_log(logpath, f"Throughput: {throughput} packets/s\n")
                    print(f"Throughput: {throughput} packets/s")

                if suite_cfg["bandwidth"]:
                    bandwidth = _compute_bandwidth(ioctlpath, time) // time 
                    avg_bandwidth.append(bandwidth)
                    allcsvdata.append(bandwidth)
                    _append_to_log(logpath, f"Bandwidth: {bandwidth} Mbits/s\n")
                    print(f"Bandwidth: {bandwidth} Mbits/s")

                if suite_cfg["perfIPC"]:
                    # ipc = _perf_ipc(cpu,time)
                    ipc = _perf_ipc(time, program_name)
                    avg_ipc.append(ipc)
                    allcsvdata.append(ipc)
                    _append_to_log(logpath, f"IPC: {ipc}\n")
                    print(f"IPC: {ipc}")
                
                if suite_cfg["perfCacheMisses"]:
                    # cache_misses = _perf_cache_misses(cpu,time)
                    cache_misses = _perf_cache_misses(time, program_name)
                    avg_cache_misses.append(cache_misses)
                    allcsvdata.append(cache_misses)
                    _append_to_log(logpath, f"Cache misses: {cache_misses}\n")
                    print(f"Cache misses: {cache_misses}")

                if suite_cfg["perfIPP"]:
                    # ipc = _perf_ipc(cpu,time)
                    ipp = _perf_ipp(ioctlpath,cpu,time, cfg_fpga)
                    avg_ipp.append(ipp)
                    allcsvdata.append(ipp)
                    _append_to_log(logpath, f"IPP: {ipp}\n")
                    print(f"IPP: {ipp}")
                
                if suite_cfg["perfBranchMisses"]:
                    branch_misses = _perf_branch_misses(time, program_name)
                    avg_branch_misses.append(branch_misses)
                    allcsvdata.append(branch_misses)
                    _append_to_log(logpath, f"Branch misses: {branch_misses}\n")
                    print(f"Branch misses: {branch_misses}")

                if suite_cfg.get("perfTLBMisses", False):
                    tlb_misses = _perf_tlb_misses(time, program_name)
                    avg_tlb_misses.append(tlb_misses)
                    allcsvdata.append(tlb_misses)
                    _append_to_log(logpath, f"TLB misses: {tlb_misses}\n")
                    print(f"TLB misses: {tlb_misses}")
                
                if suite_cfg.get("perfTLBStores", False):
                    tlb_store = _perf_tlb_stores(time, program_name)
                    avg_tlb_store.append(tlb_store)
                    allcsvdata.append(tlb_store)
                    _append_to_log(logpath, f"TLB stores: {tlb_store}\n")
                    print(f"TLB stores: {tlb_store}")
                
                if suite_cfg.get("perfTLBStoreMisses", False):
                    tlb_store_misses = _perf_tlb_store_misses(time, program_name)
                    avg_tlb_store_misses.append(tlb_store_misses)
                    allcsvdata.append(tlb_store_misses)
                    _append_to_log(logpath, f"TLB store misses: {tlb_store_misses}\n")
                    print(f"TLB store misses: {tlb_store_misses}")


                if suite_cfg.get("cpuUsage", False):
                    cpu_usage = _cpu_usage(time=1,core=0)
                    avg_core_usage.append(cpu_usage)
                    allcsvdata.append(cpu_usage)
                    _append_to_log(logpath, f"Core usage: {cpu_usage}\n")
                    print(f"Core usage: {cpu_usage}")

                if suite_cfg.get("perfL1Rateo", False):
                    l1rateo = _perf_l1_rateo(time, program_name)
                    avg_l1_rateo.append(l1rateo)
                    allcsvdata.append(l1rateo)
                    _append_to_log(logpath, f"L1 rateo: {l1rateo}\n")
                    print(f"L1 rateo: {l1rateo}")
                
                if suite_cfg.get("perfL3Rateo", False):
                    l3rateo = _perf_l3_rateo(time, program_name)
                    avg_l3_rateo.append(l3rateo)
                    allcsvdata.append(l3rateo)
                    _append_to_log(logpath, f"L3 rateo: {l3rateo}\n")
                    print(f"L3 rateo: {l3rateo}")
                
                if suite_cfg.get("perfTLBRateo", False):
                    tlb_rateo = _perf_tlb_rateo(time, program_name)
                    avg_tlb_rateo.append(tlb_rateo)
                    allcsvdata.append(tlb_rateo)
                    _append_to_log(logpath, f"TLB rateo: {tlb_rateo}\n")
                    print(f"TLB rateo: {tlb_rateo}")

                if suite_cfg.get("interrupt", False):
                    interrupt = _interrupt(time)
                    avg_interrupt.append(interrupt)
                    allcsvdata.append(interrupt)
                    _append_to_log(logpath, f"Interrupts: {interrupt}\n")
                    print(f"Interrupts: {interrupt}")
                    

                _term_program(process, logpath)
                _append_to_csv(allcsvpath, allcsvdata)
                #svuita tra ripetizioni
                allcsvdata = []
                after_exp(suite_cfg)

            if suite_cfg["throughput"]:
                # avg_throughput = sum(avg_throughput) / repetitions
                avg_std = np.std(avg_throughput)
                avg_throughput = np.mean(avg_throughput)
                csvdata.append(avg_throughput)
                csvdata.append(avg_std)
                _append_to_log(logpath, f"Average throughput: {avg_throughput} packets/s std : {avg_std}\n")
                print(f"Average throughput: {avg_throughput} packets/s std : {avg_std}")

            if suite_cfg["bandwidth"]:
                avg_bandwidth = sum(avg_bandwidth) / repetitions
                csvdata.append(avg_bandwidth)
                _append_to_log(logpath, f"Average bandwidth: {avg_bandwidth} Mbits/s\n")
                print(f"Average bandwidth: {avg_bandwidth} Mbits/s")
                

            if suite_cfg["perfIPC"]:
                avg_ipc = sum(avg_ipc) / repetitions
                csvdata.append(avg_ipc)
                _append_to_log(logpath, f"Average IPC: {avg_ipc}\n")
                print(f"Average IPC: {avg_ipc}")

            if suite_cfg["perfCacheMisses"]:
                avg_cache_misses = sum(avg_cache_misses) / repetitions
                csvdata.append(avg_cache_misses)
                _append_to_log(logpath, f"Average Cache misses: {avg_cache_misses}\n")
                print(f"Average Cache misses: {avg_cache_misses}")

            if suite_cfg["perfIPP"]:
                avg_ipp = sum(avg_ipp) / repetitions
                csvdata.append(avg_ipp)
                _append_to_log(logpath, f"Average IPP: {avg_ipp}\n")
                print(f"Average IPP: {avg_ipp}")

            if suite_cfg["perfBranchMisses"]:
                avg_branch_misses = sum(avg_branch_misses) / repetitions
                csvdata.append(avg_branch_misses)
                _append_to_log(logpath, f"Average Branch misses: {avg_branch_misses}\n")
                print(f"Average Branch misses: {avg_branch_misses}")
            
            if suite_cfg.get("perfTLBMisses", False):
                avg_tlb_misses = sum(avg_tlb_misses) / repetitions
                csvdata.append(avg_tlb_misses)
                _append_to_log(logpath, f"Average TLB misses: {avg_tlb_misses}\n")
                print(f"Average TLB misses: {avg_tlb_misses}")
            
            if suite_cfg.get("perfTLBStores", False):
                avg_tlb_store = sum(avg_tlb_store) / repetitions
                csvdata.append(avg_tlb_store)
                _append_to_log(logpath, f"Average TLB stores: {avg_tlb_store}\n")
                print(f"Average TLB stores: {avg_tlb_store}")
            
            if suite_cfg.get("perfTLBStoreMisses", False):
                avg_tlb_store_misses = sum(avg_tlb_store_misses) / repetitions
                csvdata.append(avg_tlb_store_misses)
                _append_to_log(logpath, f"Average TLB store misses: {avg_tlb_store_misses}\n")
                print(f"Average TLB store misses: {avg_tlb_store_misses}")

            if suite_cfg.get("cpuUsage", False):
                avg_core_usage = sum(avg_core_usage) / repetitions
                csvdata.append(avg_core_usage)
                _append_to_log(logpath, f"Average Core usage: {avg_core_usage}\n")

            if suite_cfg.get("perfL1Rateo", False):
                avg_l1_rateo = sum(avg_l1_rateo) / repetitions
                csvdata.append(avg_l1_rateo)
                _append_to_log(logpath, f"Average L1 rateo: {avg_l1_rateo}\n")
            
            if suite_cfg.get("perfL3Rateo", False):
                avg_l3_rateo = sum(avg_l3_rateo) / repetitions
                csvdata.append(avg_l3_rateo)
                _append_to_log(logpath, f"Average L3 rateo: {avg_l3_rateo}\n")
            
            if suite_cfg.get("perfTLBRateo", False):
                avg_tlb_rateo = sum(avg_tlb_rateo) / repetitions
                csvdata.append(avg_tlb_rateo)
                _append_to_log(logpath, f"Average TLB rateo: {avg_tlb_rateo}\n")
            
            if suite_cfg.get("interrupt", False):
                avg_interrupt = sum(avg_interrupt) / repetitions
                csvdata.append(avg_interrupt)
                _append_to_log(logpath, f"Average Interrupts: {avg_interrupt}\n")

            _append_to_csv(csvpath, csvdata)
            #svuita tra ripetizioni
            csvdata = []


    return 0