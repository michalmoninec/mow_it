import json
from enum import Enum


# Load the enum definition from JSON
def load_status_enum():
    with open("config/status_enum.json", "r") as f:
        enum_data = json.load(f)

        Status = Enum("Status", enum_data["Status"])
    return Status


Status = load_status_enum()
