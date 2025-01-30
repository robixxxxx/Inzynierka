class DeviceModel:
    def __init__(self, name, ip, control_port, telemetry_port):
        self.name = name
        self.ip = ip
        self.control_port = control_port
        self.telemetry_port = telemetry_port

    def set_name(self, name):
        self.name = name

    def set_ip(self, ip):
        self.ip = ip

    def set_control_port(self, control_port):
        self.control_port = control_port

    def set_telemetry_port(self, telemetry_port):
        self.telemetry_port = telemetry_port

    def get_name(self):
        return self.name
    
    def get_ip(self):
        return self.ip
    
    def get_control_port(self):
        return self.control_port

    def get_telemetry_port(self):
        return self.telemetry_port