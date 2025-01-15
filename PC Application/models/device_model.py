class DeviceModel:
    def __init__(self, name, ip, control_port, telemetry_port):
        self.name = name
        self.ip = ip
        self.control_port = control_port
        self.telemetry_port = telemetry_port

    def __eq__(self, other):
        return self.ip == other.ip and self.control_port == other.control_port

    def __hash__(self):
        return hash((self.ip, self.control_port))
