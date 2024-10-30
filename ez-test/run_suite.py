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

def _clear_log(log_path: str) -> int:
    with open(log_path, "w") as f:
        pass
    return 0

def _compute_throughput(ioctlpath:str, time:int) -> int:
    command = f"sudo {ioctlpath} 3 {time}"
    try:
        result = sp.run(shlex.split(command),capture_output=True,text=True, check=True)

    except sp.CalledProcessError as e:
        print(f"Error ./ioctl 3 {time} command")
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
    repetitions = suite_cfg["repetitions"]

    #clear logfile
    _clear_log(logpath)


    for program in suite_cfg["progs"]:
        program_path=os.path.join(absolute_path, program["path"])


        avg_throughput=[]
        avg_ipc=[]
        avg_cache_misses=[]

        for repetition in range(repetitions):

            process = _load_program(program_path, ifname, logpath)


            _append_to_log(logpath, f"Repetition: {repetition+1}\n")
            print(f"Repetition: {repetition+1}")

            if suite_cfg["throughput"]:
                throughput = _compute_throughput(ioctlpath, time) // time 
                avg_throughput.append(throughput)
                _append_to_log(logpath, f"Throughput: {throughput} packets/s\n")
                print(f"Throughput: {throughput} packets/s")


            if suite_cfg["perfIPC"]:
                ipc = _perf_ipc(cpu, time)
                avg_ipc.append(ipc)
                _append_to_log(logpath, f"IPC: {ipc}\n")
                print(f"IPC: {ipc}")
            
            if suite_cfg["perfCacheMisses"]:
                cache_misses = _perf_cache_misses(cpu, time)
                avg_cache_misses.append(cache_misses)
                _append_to_log(logpath, f"Cache misses: {cache_misses}\n")
                print(f"Cache misses: {cache_misses}")

            _term_program(process, logpath)

        if suite_cfg["throughput"]:
            avg_throughput = sum(avg_throughput) / repetitions
            _append_to_log(logpath, f"Average throughput: {avg_throughput} packets/s\n")
            print(f"Average throughput: {avg_throughput} packets/s")

        if suite_cfg["perfIPC"]:
            avg_ipc = sum(avg_ipc) / repetitions
            _append_to_log(logpath, f"Average IPC: {avg_ipc}\n")
            print(f"Average IPC: {avg_ipc}")

        if suite_cfg["perfCacheMisses"]:
            avg_cache_misses = sum(avg_cache_misses) / repetitions
            _append_to_log(logpath, f"Average Cache misses: {avg_cache_misses}\n")
            print(f"Average Cache misses: {avg_cache_misses}")


    return 0