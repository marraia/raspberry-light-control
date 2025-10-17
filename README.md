# Raspberry Light Control

This project allows you to control a light connected to a Raspberry Pi using either socket communication or RabbitMQ messaging. The application listens for incoming signals and turns the light on or off based on the received commands.

## Project Structure

```
raspberry-light-control
├── src
│   ├── main.py            # Entry point of the application
│   ├── socket_listener.py  # Socket listener for incoming connections
│   ├── rabbit_listener.py  # RabbitMQ listener for message processing
│   └── light_controller.py # Controls the light's state
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/raspberry-light-control.git
   cd raspberry-light-control
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your environment:**
   - Make sure your Raspberry Pi is powered on and running Raspberry Pi OS.
   - Connect your light (e.g., LED or relay) to a GPIO pin (e.g., GPIO17) and ground.
   - Enable GPIO access by installing the `RPi.GPIO` Python library:
     ```bash
     pip install RPi.GPIO
     ```
   - (Optional) Test your GPIO setup with a simple Python script to turn the light on