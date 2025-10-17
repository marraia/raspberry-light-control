import pika
import json
import os
from light_controller import LightController

class RabbitListener:
    def __init__(self, queue_name=None, host=None, port=None, username=None, password=None):
        self.queue_name = queue_name or os.getenv('RABBIT_QUEUE', 'light_queue')
        self.host = host or os.getenv('RABBIT_HOST', 'localhost')
        self.port = int(port or os.getenv('RABBIT_PORT', '5672'))
        self.username = username or os.getenv('RABBIT_USER')
        self.password = password or os.getenv('RABBIT_PASS')

        self.light_controller = LightController()
        self.connection = None
        self.channel = None

    def connect(self):
        if self.username and self.password:
            creds = pika.PlainCredentials(self.username, self.password)
            params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=creds)
        else:
            params = pika.ConnectionParameters(host=self.host, port=self.port)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        try:
            message = json.loads(body)
        except Exception:
            print("Invalid message payload:", body)
            return

        action = message.get('action')
        if action == 'turn_on':
            self.light_controller.turn_on()
        elif action == 'turn_off':
            self.light_controller.turn_off()
        else:
            print("Unknown action:", action)

    def start_listening(self):
        self.connect()
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        print(f"Listening for messages in queue: {self.queue_name} on {self.host}:{self.port}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            pass

    def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except Exception:
            pass
        try:
            if self.light_controller:
                self.light_controller.cleanup()
        except Exception:
            pass