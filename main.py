from fastapi import FastAPI
from typing import List
import serial
import board
import adafruit_dht
from gpiozero import MCP3008

app = FastAPI()

# Define the serial port name for the PM sensor
serial_port = '/dev/ttyUSB0'  # Adjust this based on your Raspberry Pi's configuration
# Define the baud rate
baud_rate = 9600  # Nova PM sensor typically uses 9600 baud rate
# Initialize serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=2)

# Initialize the DHT device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D16)

# Initialize the MCP3008 ADC object
adc = MCP3008(channel=0)  # Assuming the MQ7 sensor is connected to CH0

def read_pm_data() -> List[float]:
    """
    Function to read PM data from the Nova PM sensor.
    Returns a list of PM2.5 data points (up to 10).
    """
    pm_data = []
    try:
        # Send command to request data
        ser.write(b'\xAA\xB4\x04\x13\x00\x01\xE1')
        # Read and parse up to 10 responses
        for _ in range(10):
            data = ser.read(10)
            pm25 = int.from_bytes(data[2:4], byteorder='little') / 10.0
            pm_data.append(pm25)
    except Exception as e:
        print("Error reading PM data:", e)
    return pm_data[:10]  # Return up to 10 data points

def read_dht_data() -> dict:
    """
    Function to read temperature and humidity data from DHT22 sensor.
    Returns a dictionary containing the first 10 temperature (Celsius), temperature (Fahrenheit), and humidity data points.
    """
    dht_data = []
    try:
        # Read up to 10 data points
        for _ in range(10):
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            dht_data.append({"temperature_c": temperature_c, "temperature_f": temperature_f, "humidity": humidity})
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
    return dht_data[:10]  # Return up to 10 data points

def read_mq7_data() -> List[float]:
    """
    Function to read analog data from MQ7 sensor.
    Returns a list of analog voltage data points (up to 10).
    """
    mq7_data = []
    try:
        # Read up to 10 data points
        for _ in range(10):
            analog_value = adc.value
            mq7_data.append(analog_value)
    except Exception as e:
        print("Error reading MQ7 data:", e)
    return mq7_data[:10]  # Return up to 10 data points

@app.get("/pm_data")
def get_pm_data() -> List[float]:
    """
    Endpoint to get up to 10 PM2.5 data points from the Nova PM sensor.
    """
    return read_pm_data()

@app.get("/dht_data")
def get_dht_data() -> List[dict]:
    """
    Endpoint to get up to 10 temperature and humidity data points from DHT22 sensor.
    """
    return read_dht_data()

@app.get("/mq7_data")
def get_mq7_data() -> List[float]:
    """
    Endpoint to get up to 10 analog voltage data points from MQ7 sensor.
    """
    return read_mq7_data()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
