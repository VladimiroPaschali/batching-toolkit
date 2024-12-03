import click
import json
import os, glob, shutil
import subprocess as sp
import re
import shlex
from run_suite import run_suite
SUITES_PATH = "suites"
DEFAULT_RESULTS_PATH = "results"


HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[00m'

def show_suite_info(name):
    try:
        with open(f"{SUITES_PATH}/{name}/conf.json", "r") as f:
            suite_cfg = json.load(f)
            print(json.dumps(suite_cfg, indent=2))
    except FileNotFoundError:
        print(f"Suite {name} config not found")
        return 1
    return 0

def check_before_start(suite_cfg):
    
    if not suite_cfg.get("before_start", None):
        return
    for check in suite_cfg["before_start"]:
        color = ""
        result = sp.run(check["cmd"], shell=True, capture_output=True, text=True, check=True)
        expected = check.get("expected", None) 
        
        if expected:
            if re.search(expected, result.stdout):
                color = OKGREEN
            else:
                color = FAIL
                
        print(f"{check["name"]}: {color}{result.stdout}{RESET}")    
    pass

@click.group()
def cli():
    return 0


@click.command()
@click.option("--name", default=None, help="Name of the suite to run")
def show(name):
    if name:
        return show_suite_info(name)
    for i, suite in enumerate(os.listdir(SUITES_PATH)):
        print(f"{i+1}.  {suite}")
    return 0


def __last_suite_id():
    return int(sorted(glob.glob(f"{SUITES_PATH}/test*"))[-1].split("/")[-1][-3:])


@click.command()
@click.option("--name", default=None, help="Name of the suite to run")
def create(name):
    if not name:
        name = f"test{__last_suite_id() + 1:03}"
    try:
        os.mkdir(f"{SUITES_PATH}/{name}")
        shutil.copy("default_conf.json", f"{SUITES_PATH}/{name}/conf.json")
        os.mkdir(f"{SUITES_PATH}/{name}/results")
    except FileExistsError:
        print(f"Suite {name} already exists")
        return 1
    except FileNotFoundError:
        print("default_conf.json not found")
        os.remove(f"{SUITES_PATH}/{name}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    print(f"Suite {name} created, edit {SUITES_PATH}/{name}/conf.json to configure")
    return 0


@click.command()
@click.option("--name", help="Name of the suite to run")
def run(name):
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    if not name:
        print("Please specify a suite to run")
        return 1
    try:
        with open(f"{SUITES_PATH}/{name}/conf.json", "r") as f:
            suite_cfg = json.load(f)
    except FileNotFoundError:
        print(f"Suite {name} config not found")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    print(f"Running suite {name}")
    check_before_start(suite_cfg)
    print(f"{OKCYAN}{'-'*20}{RESET}")
    print(run_suite(suite_cfg, name))
    return 0


if __name__ == "__main__":
    cli.add_command(show)
    cli.add_command(create)
    cli.add_command(run)
    cli()
