from enum import Enum


enum_data = {
    "Status": {
        "INIT": "init",
        "JOIN_WAIT": "join_wait",
        "READY": "ready",
        "FINISHED": "finished",
    }
}


Status = Enum("Status", enum_data["Status"])
