import subprocess as sp
from datetime import datetime
import re
import csv

"""
TODO:
- finish the output csv impl, I have to choose how manage output path
- how I should perform throughput measurment?
"""

def perf(suite_cfg : dict, bpf_prog : dict):
    """
    Executes the performance test suite.

    Args:
        suite_cfg (dict): The configuration dictionary containing suite definitions.
    """
    if not suite_cfg.get("perf", None):
        return
    
    perf_cfg = _load_cfg(suite_cfg)
    bpf_prog_id = _bpf_id_from_name(bpf_prog["name"])

    csv_data = []
    for event in perf_cfg["events"]:
        avg = _exec_perf(perf_cfg, event, bpf_prog_id)
        csv_data.append({"event": event["name"], "avg": avg})
    
    
    # Write results to file
    headers = ["event"] + [item["event"] for item in csv_data]  
    values = ["avg"] + [item["avg"] for item in csv_data]      

    with open(suite_cfg["output"], mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers) 
        writer.writerow(values)   

    pass

def _exec_perf(perf_cfg : dict, event : dict, bpf_prog_id : int):
    """
    """
    
    if perf_cfg["verbose"]:
        print(f"{event['name']}: ...", end="r")
            
    metric_count, run_count = _measure_event(perf_cfg, event, bpf_prog_id)
    
    if perf_cfg["verbose"]:
        print(f"{event['name']}: {metric_count / run_count}")
        
    return metric_count / run_count

def _measure_event(perf_cfg : dict, event : dict, bpf_prog_id : int) -> tuple:
    """
    """
    perf = perf_cfg["command"]
    event_name = event["name"]
    
    cmd = f"{perf} stat -e {event_name} -b {bpf_prog_id} --timeout {perf_cfg['timeout']*1000}"
    
    result = sp.run(cmd, capture_output=True,shell=True, text=True, check=True)

    match = re.search(rf'([\d.]+)\s+{event_name}', result.stderr)
    if not match:
        raise ValueError(f"Event {event_name} not found in perf output")
    
    metric_count = match.group(1)
    
    run_count = 1
    if perf == "perf_bpf":
        match = re.search(r'run:\s*(\d+)', result.stderr)
        if not match:
            raise ValueError(f"Run count not found in perf output")
        run_count = match.group(1)
        
    return metric_count, run_count

def _load_cfg(suite_cfg : dict):
    """
    Loads the configuration for the performance test suite.
    For not defined fields, default values are used.

    Args:
        suite_cfg (dict): The configuration dictionary containing suite definitions.
    """
    
    perf_cfg = {
        "command": "perf_bpf", # path to the executable
        "timeout": 10, # seconds
        "warmup": 0, # seconds
        "verbose": False, # print on stdout
        "events": []   # list of events to monitor
    }
    
    return perf_cfg.update({k: v for k, v in suite_cfg["perf"].items() if k in perf_cfg})

def _bpf_id_from_name(name : str):
    """
    Returns the BPF event ID from the event name.
    
    Args:
        name (str): The name of the event.
    
    Returns:
        int: The BPF event ID.
    """
    
    cmd = f"sudo bpftool prog show name {name} | grep -o "^[0-9]*""
    cmd_result = sp.run(cmd, shell=True, capture_output=True, text=True)
    
    if len(cmd_result.stdout.split("\n")) == 0:
        raise ValueError(f"No BPF program found with name {name}")
    
    if len(cmd_result.stdout.split("\n")) > 1:
        raise ValueError(f"Multiple BPF programs found with name {name}")
    
    return int(cmd_result.stdout)