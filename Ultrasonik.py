import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json

# GPIO pins for HC-SR04
TRIG_PIN = 23
ECHO_PIN = 24

# GPIO pins for LEDs
RED_LED_PIN = 17
YELLOW_LED_PIN = 27
GREEN_LED_PIN = 22

# Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

# Configure ThingsBoard MQTT
THINGSVERSE_HOST = 'thingsboard.cloud' #
ACCESS_TOKEN = 'xxxxxxxxxxxxxxxxxxxx' #Ganti dengan acces token anda

# Initialize MQTT Client
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSVERSE_HOST, 1883, 60)
client.loop_start()

def read_distance():
    """Measure distance using HC-SR04."""
    # Send a short pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # 10 microseconds pulse
    GPIO.output(TRIG_PIN, False)

    # Wait for echo to start
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    # Wait for echo to end
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start

    # Convert to distance in cm
    distance = pulse_duration * 17150  # Speed of sound = 34300 cm/s, divide by 2 for round trip
    return round(distance, 2)

def blink_led(pin, duration=0.5):
    """Blink an LED for a short duration."""
    GPIO.output(pin, True)
    time.sleep(duration)
    GPIO.output(pin, False)
    time.sleep(duration)

try:
    while True:
        # Read distance from HC-SR04
        distance = read_distance()
        print(f"Distance: {distance} cm")

        # Determine which LED to blink based on distance
        if distance <= 3:
            print("Red LED blinking...")
            blink_led(RED_LED_PIN)
        elif 3 < distance <= 6:
            print("Yellow LED blinking...")
            blink_led(YELLOW_LED_PIN)
        elif distance > 6:
            print("Green LED blinking...")
            blink_led(GREEN_LED_PIN)

        # Publish data to ThingsBoard
        telemetry_data = {
            "distance": distance,
            "status": "RED" if distance <= 3 else "YELLOW" if distance <= 6 else "GREEN"
        }
        client.publish('v1/devices/me/telemetry', json.dumps(telemetry_data), qos=1)

        time.sleep(1)  # Delay before next reading

except KeyboardInterrupt:
    print("Program stopped.")
finally:
    GPIO.cleanup()  # Reset GPIO pins
    client.loop_stop()
    client.disconnect()
