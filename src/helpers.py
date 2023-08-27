import json


import logging
from src.log import get_handler

handler = get_handler()

log = logging.getLogger(__name__)
log.handlers[:] = []
log.addHandler(handler)
log.setLevel(logging.DEBUG)


def export_json(json_path, data, indent=4):
    with open(json_path, "w") as f:
        json.dump(data, f, indent=indent)

    log.info(f"Exported to {json_path}")
