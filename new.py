import serial
import pynmea2

def get_gps_data() -> dict:
    """
    Function to get location data from Neo 6M GPS antenna module.
    Returns a dictionary containing latitude and longitude.
    """
    gps_data = {}
    try:
        # Initialize serial connection
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=5)
        while True:
            # Read GPS data
            data = ser.readline().decode('utf-8')
            if data.startswith('$GNGGA'):
                msg = pynmea2.parse(data)
                # Extract latitude and longitude
                latitude = msg.latitude
                longitude = msg.longitude
                # Check if latitude and longitude are valid
                if latitude and longitude:
                    gps_data['latitude'] = latitude
                    gps_data['longitude'] = longitude
                    break
    except Exception as e:
        print("Error reading GPS data:", e)
    return gps_data

# Example usage:
# location = get_gps_data()
# print(location)
