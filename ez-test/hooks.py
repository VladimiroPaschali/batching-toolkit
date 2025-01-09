"""
This module defines methods for managing and executing a sequence of hooks during the lifecycle of a suite process. 
Hooks are defined as specific execution points (`before_start`, `before_exp`, `after_exp`, `after_finish`) 
where user-defined commands can be executed conditionally. 
"""

import subprocess as sp
from colors import *
import re 

# List of valid hook types
HOOKS = ["before_start", "before_exp", "after_exp", "after_finish"]

def before_start(suite_cfg):
    """
    Executes the 'before_start' hook if defined in the suite configuration.
    
    Args:
        suite_cfg (dict): The configuration dictionary containing hook definitions.
    """
    if not suite_cfg.get("before_start", None):
        return
    
    _hook_exec("before_start", suite_cfg)

def before_exp(suite_cfg):
    """
    Executes the 'before_exp' hook if defined in the suite configuration.
    
    Args:
        suite_cfg (dict): The configuration dictionary containing hook definitions.
    """
    if not suite_cfg.get("before_exp", None):
        return
    
    _hook_exec("before_exp", suite_cfg)

def after_exp(suite_cfg):
    """
    Executes the 'after_exp' hook if defined in the suite configuration.
    
    Args:
        suite_cfg (dict): The configuration dictionary containing hook definitions.
    """
    if not suite_cfg.get("after_exp", None):
        return
    
    _hook_exec("after_exp", suite_cfg)

def after_finish(suite_cfg):
    """
    Executes the 'after_finish' hook if defined in the suite configuration.
    
    Args:
        suite_cfg (dict): The configuration dictionary containing hook definitions.
    """
    if not suite_cfg.get("after_finish", None):
        return
    
    _hook_exec("after_finish", suite_cfg)

def _is_hook(hook_type):
    """
    Validates if the given hook type is one of the defined hooks.
    
    Args:
        hook_type (str): The type of the hook to validate.
    
    Returns:
        bool: True if the hook type is valid, False otherwise.
    """
    return hook_type in HOOKS

def _cmd_condition(cmd: dict) -> bool:
    """
    Evaluates the 'condition' field of a command. The command executes only if the condition evaluates to True.
    
    Args:
        cmd (dict): A dictionary representing the command configuration.
    
    Returns:
        bool: True if the condition passes or is not defined, False otherwise.
    """
    condition = cmd.get("condition", None) 
    if condition:
        condition_result = sp.run(cmd["condition"], shell=True, capture_output=True, text=True, check=True)
        if condition_result.stdout == "0":
            return False
    return True

def _cmd_expected(cmd: dict, result: str, panic: bool) -> bool:
    """
    Validates the command's output against the 'expected' regex.
    
    Args:
        cmd (dict): A dictionary representing the command configuration.
        result (str): The output of the executed command.
        panic (bool): If True, raises a ValueError on validation failure.
    
    Returns:
        bool: True if the validation passes or is not defined, False otherwise.
    
    Raises:
        ValueError: If validation fails and panic is enabled.
    """
    expected = cmd.get("expected", None) 
    if expected:
        is_match = bool(re.search(expected, result.stdout))
        if not is_match and panic:
            raise ValueError(f"Expected {expected} but got {result.stdout} during {cmd['name']} execution")
        return is_match
    return True

def _hook_exec(hook_type: str, suite_cfg):
    """
    Executes all commands defined in the specified hook type.
    
    Args:
        hook_type (str): The type of the hook to execute (e.g., 'before_start', 'after_finish').
        suite_cfg (dict): The configuration dictionary containing hook definitions.
    
    Raises:
        ValueError: If the hook type is invalid.
    """
    if not _is_hook(hook_type):
        raise ValueError(f"Invalid hook type: {hook_type}")
    
    for cmd in suite_cfg[hook_type]:
        if not _cmd_condition(cmd):
            continue
        color = ""
        cmd_result = sp.run(cmd["cmd"], shell=True, capture_output=True, text=True, check=True)
        
        if _cmd_expected(cmd, cmd_result, cmd.get("panic", False)):
            color = OKGREEN
        else:
            color = FAIL
                
        print(f"{cmd['name']}: {color}{cmd_result.stdout}{RESET}")
