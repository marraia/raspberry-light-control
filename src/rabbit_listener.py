import os
import json
import pika
from light_controller import LightController

class RabbitListener:
    def __init__(self, queue_name=None, url=None, host=None, port=None, username=None, password=None, vhost=None):
        # queue and connection URL (default to the provided AMQPS URL if env not set)
        self.queue_name = queue_name or os.getenv('RABBIT_QUEUE', 'light_queue')
        self.url = url or os.getenv('RABBIT_URL', 'amqps://blmfmpod:iLIyEexy85xzkbX8KATYHwPEsvwz-OP4@toucan.lmq.cloudamqp.com/blmfmpod')

        # optional individual params (used only if URL not provided)
        self.host = host or os.getenv('RABBIT_HOST')
        self.port = int(port or os.getenv('RABBIT_PORT', '5672')) if (port or os.getenv('RABBIT_PORT')) else None
        self.username = username or os.getenv('RABBIT_USER')
        self.password = password or os.getenv('RABBIT_PASS')
        self.vhost = vhost or os.getenv('RABBIT_VHOST', '/')

        self.light_controller = LightController()
        self.connection = None
        self.channel = None

    def connect(self):
        if self.url:
            params = pika.URLParameters(self.url)
        else:
            if self.username and self.password:
                creds = pika.PlainCredentials(self.username, self.password)
                params = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost, credentials=creds)
            else:
                params = pika.ConnectionParameters(host=self.host, port=self.port, virtual_host=self.vhost)

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def callback(self, ch, method, properties, body):
        try:
            payload = body.decode() if isinstance(body, (bytes, bytearray)) else body
            message = json.loads(payload)
        except Exception:
            print("Invalid message payload:", body)
            return

        action = message.get('action') or message.get('cmd') or message.get('command')
        if action in ('turn_on', 'ON', 'on'):
            self.light_controller.turn_on()
        elif action in ('turn_off', 'OFF', 'off'):
            self.light_controller.turn_off()
        else:
            print("Unknown action:", action)

    def start_listening(self):
        self.connect()
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        print(f"Listening for messages in queue: {self.queue_name} via URL: {self.url}")
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