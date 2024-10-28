import json
import os
import re
import shlex
import signal
import subprocess as sp
from time import sleep


# SUITE_PATH = "suites"
# def _load_config(suite_path: str) -> dict:
#     try:
#         with open(f"{suite_path}/conf.json", "r") as f:
#             config = json.load(f)
#     except FileNotFoundError:
#         print("Config not found")
#         return 1
#     return config

def _load_program(program_path: str, ifname: str, logpath:str) -> sp.Popen:
    command = f"sudo {program_path} {ifname}"
    #shell false permette di fare process.terminate()
    #pipare o out o err se no si rompe la shell
    process = sp.Popen(shlex.split(command),stdout=sp.PIPE,text=True)
    print(f"Running program: {os.path.basename(program_path)}")
    _append_to_log(logpath, f"Running program: {os.path.basename(program_path)}\n")
   
    return process

def _term_process(process: sp.Popen, logpath:str) -> int:

    process.terminate()
    print(f"Process terminated")
    _append_to_log(logpath, process.stdout.read())
    _append_to_log(logpath, "Process terminated\n")
    return 0

def _append_to_log(log_path: str, data: str) -> int:
    with open(log_path, "a") as f:
        f.write(data)
    return 0

def _clear_log(log_path: str) -> int:
    with open(log_path, "w") as f:
        pass
    return 0

def _compute_throughput(ioctlpath:str) -> int:
    command = f"sudo {ioctlpath} 2"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error ./ioctl 2 command")
        return -1
    
    return int(result.stdout)

def _perf_ipc(cpu, time) -> int:
    command = f"sudo perf stat -e cycles:k,instructions:k -C {cpu} --timeout {time*1000}"

    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf IPC command")
        return -1
    
    match = re.search(r'([\d.]+)\s+insn per cycle', result.stderr)
    if match:
        return float(match.group(1))
    else:
        return -1
    
def _perf_cache_misses(cpu, time) -> int:
    command= f"sudo perf_bpf stat -e L1-dcache-load-misses:k -C {cpu} --timeout {time*1000}"

    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print("Error perf IPC command")
        return -1
    # print(result.stderr)

    match1 = re.search(r'([\d,]+)\s+L1-dcache-load-misses', result.stderr)
    cache_misses = int(match1.group(1).replace(",","")) if match1 else -1

    # Trova il valore numerico a destra di "run:"
    match2 = re.search(r'run:\s*(\d+)', result.stderr)
    run_count = int(match2.group(1)) if match2 else -1

    return cache_misses/run_count


def run_suite(suite_cfg:json, name:str) -> int:

    # if os.geteuid() != 0:
    #     exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    
    absolute_path = os.path.abspath(suite_cfg["exp-dir"])
    ifname = suite_cfg["ifname"]
    logpath = os.path.join(os.getcwd(),"suites", name, "log.txt")
    ioctlpath = os.path.join(os.path.abspath(suite_cfg["ioctl-dir"]), "ioctl")
    time = suite_cfg["time"]
    cpu = suite_cfg["cpu"]

    #clear logfile
    _clear_log(logpath)



    for program in suite_cfg["progs"]:
        absolute_path=os.path.join(absolute_path, program["path"])

        process = _load_program(absolute_path, ifname, logpath)
        if suite_cfg["throughput"]:
            pre_throughput = _compute_throughput(ioctlpath)
            # print(f"Pre throughput: {pre_throughput} packets")

        sleep(time)

        if suite_cfg["throughput"]:
            post_throughput = _compute_throughput(ioctlpath)
            throughput = (post_throughput - pre_throughput) // time
            _append_to_log(logpath, f"Throughput: {throughput} packets/s\n")
            print(f"Throughput: {throughput} packets/s")

        if suite_cfg["perfIPC"]:
            ipc = _perf_ipc(cpu, time)
            _append_to_log(logpath, f"IPC: {ipc}\n")
            print(f"IPC: {ipc}")
        
        if suite_cfg["perfCacheMisses"]:
            cache_misses = _perf_cache_misses(cpu, time)
            _append_to_log(logpath, f"Cache misses: {cache_misses}\n")
            print(f"Cache misses: {cache_misses}")

        _term_process(process, logpath)      
    return 0