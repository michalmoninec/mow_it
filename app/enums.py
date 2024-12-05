import json
import os

from enum import Enum

file_path = os.path.join(os.path.dirname(__file__), "config/status_enum.json")


def load_status_enum() -> Enum:
    with open(file_path, "r") as f:
        enum_data = json.load(f)

        Status = Enum("Status", enum_data["Status"])
    return Status


Status = load_status_enum()
