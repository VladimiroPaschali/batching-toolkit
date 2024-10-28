import json

SUITE_PATH = "suites"


def __load_config(suite_path: str) -> dict:
    try:
        with open(f"{suite_path}/conf.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config not found")
        return 1
    return config
