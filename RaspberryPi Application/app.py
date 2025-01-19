import threading
from src.server.server import RaspberryPiServer

if __name__ == "__main__":
    server = RaspberryPiServer()
    threading.Thread(target=server.start_broadcasting, daemon=True).start()
    threading.Thread(target=server.handle_control_connection, daemon=True).start()
    threading.Thread(target=server.handle_telemetry_connection, daemon=True).start()
    threading.Thread(target=server.monitor_network, daemon=True).start()

    try:
        server.app.run(host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        server.stop()