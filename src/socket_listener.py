class SocketListener:
    def __init__(self, host='localhost', port=65432):
        self.host = host
        self.port = port
        self.socket = None

    def setup_socket(self):
        import socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def listen(self):
        print(f"Listening for connections on {self.host}:{self.port}...")
        conn, addr = self.socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode()
                self.trigger_light_control(message)

    def trigger_light_control(self, message):
        from light_controller import LightController
        light_controller = LightController()
        if message == 'ON':
            light_controller.turn_on()
        elif message == 'OFF':
            light_controller.turn_off()