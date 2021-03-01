MessageType = {
    "Message_": 0,
    "Message_Request": 1,
    "Message_Response": 2
}

RecordType = {
    "Record_": 0,
    "RecordSend": 1,
    "RecordReceive": 2
}

Record = {
    "type": 0,
    "timestamp": 0,
    "message_name": "",
    "uuid": "",
    "service": ""
}

FaultType = {
    "Fault_": 0,
    "FaultCrash": 1,
    "FaultDelay": 2
}

RLFI = {
    "type": 0,
    "name": "",
    "delay": 0
}

TFIMeta = {
    "name": "",
    "times": 0,
    "already": 0
}

TFI = {
    "type": 0,
    "name": [],
    "delay": 0,
    "after": []
}