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
    fields = ["program"]
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
    with open(csv_path, "w",newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)

def _append_to_csv(csv_path: str, data: list) -> int:
    with open(csv_path, "a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def _compute_throughput(ioctlpath:str, time:int,cfg_fpga) -> int:
    #se fpga è true c = "" altrimenti c = ""
    if cfg_fpga:
        command = f"sudo {ioctlpath} -c 3 -w {time}"
    else:
        command = f"sudo {ioctlpath} 3 {time}"
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
        

def run_suite(suite_cfg:json, name:str) -> int:

    
    absolute_path = os.path.abspath(suite_cfg["exp-dir"])
    ifname = suite_cfg["ifname"]
    logpath = os.path.join(os.getcwd(),"suites", name, "log.txt")
    ioctlpath = os.path.join(os.path.abspath(suite_cfg["ioctl-dir"]), "ioctl")
    csvpath = os.path.join(os.getcwd(),"suites", name, "results.csv")
    time = suite_cfg["time"]
    cpu = suite_cfg["cpu"]
    repetitions = suite_cfg["repetitions"]

    cfg_fpga = suite_cfg.get("fpga", False)
    cfg_batched = suite_cfg.get("batched", False)
    
    
    #clear csv and sets up fiels
    _init_csv(csvpath, suite_cfg)
    #clear logfile
    _clear_file(logpath)

    #sets ioctl if batched mode else resets
    if cfg_fpga:
        # _batched_fpga(ioctlpath,batched)
        pass
    else:
        _batched(ioctlpath,cfg_batched)


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

        csvdata = [program_name]
        
        before_exp(suite_cfg)

        for repetition in range(repetitions):

            process = _load_program(program_path, ifname, logpath, vargs)


            _append_to_log(logpath, f"Repetition: {repetition+1}\n")
            print(f"Repetition: {repetition+1}")

            if suite_cfg["throughput"]:
                throughput = _compute_throughput(ioctlpath, time, cfg_fpga) // time 
                avg_throughput.append(throughput)
                _append_to_log(logpath, f"Throughput: {throughput} packets/s\n")
                print(f"Throughput: {throughput} packets/s")

            if suite_cfg["bandwidth"]:
                bandwidth = _compute_bandwidth(ioctlpath, time) // time 
                avg_bandwidth.append(bandwidth)
                _append_to_log(logpath, f"Bandwidth: {bandwidth} Mbits/s\n")
                print(f"Bandwidth: {bandwidth} Mbits/s")

            if suite_cfg["perfIPC"]:
                # ipc = _perf_ipc(cpu,time)
                ipc = _perf_ipc(time, program_name)
                avg_ipc.append(ipc)
                _append_to_log(logpath, f"IPC: {ipc}\n")
                print(f"IPC: {ipc}")
            
            if suite_cfg["perfCacheMisses"]:
                # cache_misses = _perf_cache_misses(cpu,time)
                cache_misses = _perf_cache_misses(time, program_name)
                avg_cache_misses.append(cache_misses)
                _append_to_log(logpath, f"Cache misses: {cache_misses}\n")
                print(f"Cache misses: {cache_misses}")

            if suite_cfg["perfIPP"]:
                # ipc = _perf_ipc(cpu,time)
                ipp = _perf_ipp(ioctlpath,cpu,time, cfg_fpga)
                avg_ipp.append(ipp)
                _append_to_log(logpath, f"IPP: {ipp}\n")
                print(f"IPP: {ipp}")
            
            if suite_cfg["perfBranchMisses"]:
                branch_misses = _perf_branch_misses(time, program_name)
                avg_branch_misses.append(branch_misses)
                _append_to_log(logpath, f"Branch misses: {branch_misses}\n")
                print(f"Branch misses: {branch_misses}")

            _term_program(process, logpath)
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

        _append_to_csv(csvpath, csvdata)

    return 0