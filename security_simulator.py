import paho.mqtt.client as mqtt
import time
import json
import random
from datetime import datetime

# --- ThingsBoard Configuration ---
THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'RIuWcmI05V8kyFc4FUlg'

# --- MQTT Client Setup ---
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# --- Global state variables for more realistic simulation ---
home_state = {
    "occupancy_mode": "home",  # home, away, night, vacation
    "last_motion_time": {},
    "door_patterns": {},
    "temp_trend": 0.1
}

# --- Device Attributes (sent once after connection) ---
ATTRIBUTES = {
    "device_id": "home001",
    "device_type": "home_simulator",
    "firmware_version": "1.0",
    "rooms": ["living_room", "kitchen", "bedroom1", "bedroom2", "bathroom"],
    "location": {"lat": 37.7749, "lon": -122.4194}
}

# --- Customizable Reporting Interval ---
REPORT_INTERVAL = 10  # seconds

def get_realistic_home_data():
    """Generate realistic home security data as a flat dictionary for ThingsBoard telemetry"""
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    # Determine occupancy mode based on time
    if 23 <= current_hour or current_hour <= 6:
        home_state["occupancy_mode"] = "night"
    elif 8 <= current_hour <= 17 and random.random() < 0.3:
        home_state["occupancy_mode"] = "away"
    else:
        home_state["occupancy_mode"] = "home"
    
    # More realistic door patterns
    if home_state["occupancy_mode"] == "night":
        # At night, mostly closed doors
        main_door = 0  # Always closed at night
        kitchen_door = random.choice([0, 0, 0, 1])  # Mostly closed
        bedroom1_door = random.choice([0, 1])  # 50/50
        bedroom2_door = random.choice([0, 0, 1])  # Mostly closed
        bathroom_door = random.choice([0, 0, 0, 1])  # Mostly closed
    elif home_state["occupancy_mode"] == "away":
        # When away, all doors closed
        main_door = 0
        kitchen_door = 0
        bedroom1_door = 0
        bedroom2_door = 0
        bathroom_door = 0
    else:
        # When home, more door activity
        main_door = random.choice([0, 0, 0, 1])  # Mostly closed
        kitchen_door = random.choice([0, 1, 1])  # Often open
        bedroom1_door = random.choice([0, 1])
        bedroom2_door = random.choice([0, 1])
        bathroom_door = random.choice([0, 0, 1])  # Mostly closed
    
    # Motion patterns based on occupancy
    if home_state["occupancy_mode"] == "away":
        living_room_motion = 0
        kitchen_motion = 0
    elif home_state["occupancy_mode"] == "night":
        living_room_motion = random.choice([0, 0, 0, 0, 1])  # Rare motion
        kitchen_motion = random.choice([0, 0, 0, 1])  # Occasional
    else:
        living_room_motion = random.choice([0, 0, 1, 1])  # Active when home
        kitchen_motion = random.choice([0, 1, 1])  # Very active
    
    # Window patterns (more likely open during day)
    if 6 <= current_hour <= 20:
        living_room_window = random.choice([0, 0, 1, 1])  # Often open during day
    else:
        living_room_window = random.choice([0, 0, 0, 1])  # Mostly closed at night
    
    # Smoke detector (very rare activation)
    kitchen_smoke = 1 if random.random() < 0.02 else 0  # 2% chance
    
    # Realistic temperature with slight variations
    base_temp = 22.0  # Comfortable room temperature
    if home_state["occupancy_mode"] == "away":
        base_temp = 20.0  # Lower when away
    elif home_state["occupancy_mode"] == "night":
        base_temp = 21.0  # Slightly lower at night
    
    # Add small random variation
    temp_variation = random.uniform(-2.0, 2.0)
    internal_temperature = round(base_temp + temp_variation, 1)
    
    # Security system status
    system_status = "ARMED" if home_state["occupancy_mode"] == "away" else "DISARMED"

    # Intrusion alert: rare, only if motion detected in away mode
    intrusion_alert = 1 if home_state["occupancy_mode"] == "away" and (living_room_motion or kitchen_motion) else 0

    # Simulate more home security data for each room
    # Living Room
    living_room_temp = round(random.uniform(20.0, 25.0), 1)
    living_room_humidity = round(random.uniform(30.0, 60.0), 1)
    living_room_light = random.randint(100, 600)
    living_room_sound = round(random.uniform(30.0, 70.0), 1)
    living_room_co2 = random.randint(400, 1200)
    living_room_tv_on = random.choice([0, 1])
    # Kitchen
    kitchen_temp = round(random.uniform(19.0, 26.0), 1)
    kitchen_gas_leak = 1 if random.random() < 0.01 else 0
    kitchen_fridge_open = random.choice([0, 0, 1])
    # Bedroom1
    bedroom1_temp = round(random.uniform(18.0, 24.0), 1)
    bedroom1_humidity = round(random.uniform(30.0, 55.0), 1)
    bedroom1_light = random.randint(50, 400)
    bedroom1_occupancy = random.choice([0, 1])
    # Bedroom2
    bedroom2_temp = round(random.uniform(18.0, 24.0), 1)
    bedroom2_occupancy = random.choice([0, 1])
    # Bathroom
    bathroom_temp = round(random.uniform(19.0, 23.0), 1)
    bathroom_humidity = round(random.uniform(40.0, 80.0), 1)
    bathroom_water_leak = 1 if random.random() < 0.01 else 0
    bathroom_fan_on = random.choice([0, 1])
    # WiFi strength (dBm)
    wifi_strength = random.randint(-70, -40)

    data = {
        "device_id": ATTRIBUTES["device_id"],
        "timestamp": int(time.time() * 1000),
        "occupancy_mode": home_state["occupancy_mode"],
        "system_status": system_status,
        "internal_temperature": internal_temperature,
        "intrusion_alert": intrusion_alert,
        "main_door_status": main_door,
        "kitchen_door_status": kitchen_door,
        "bedroom1_door_status": bedroom1_door,
        "bedroom2_door_status": bedroom2_door,
        "bathroom_door_status": bathroom_door,
        "living_room_motion": living_room_motion,
        "living_room_window_status": living_room_window,
        "kitchen_motion": kitchen_motion,
        "kitchen_smoke_detector": kitchen_smoke,
        "location": ATTRIBUTES["location"],
        "living_room_temp": living_room_temp,
        "living_room_humidity": living_room_humidity,
        "living_room_light": living_room_light,
        "living_room_sound": living_room_sound,
        "living_room_co2": living_room_co2,
        "living_room_tv_on": living_room_tv_on,
        "kitchen_temp": kitchen_temp,
        "kitchen_gas_leak": kitchen_gas_leak,
        "kitchen_fridge_open": kitchen_fridge_open,
        "bedroom1_temp": bedroom1_temp,
        "bedroom1_humidity": bedroom1_humidity,
        "bedroom1_light": bedroom1_light,
        "bedroom1_occupancy": bedroom1_occupancy,
        "bedroom2_temp": bedroom2_temp,
        "bedroom2_occupancy": bedroom2_occupancy,
        "bathroom_temp": bathroom_temp,
        "bathroom_humidity": bathroom_humidity,
        "bathroom_water_leak": bathroom_water_leak,
        "bathroom_fan_on": bathroom_fan_on,
        "wifi_strength": wifi_strength
    }
    
    return data

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to ThingsBoard successfully!")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"📤 Data published successfully (Message ID: {mid})")

# Set callbacks
client.on_connect = on_connect
client.on_publish = on_publish

# --- Main Loop ---
try:
    print("🏠 Starting Enhanced Home Security Simulator...")
    print(f"🌐 Connecting to ThingsBoard: {THINGSBOARD_HOST}")
    print(f"🔑 Using token: {ACCESS_TOKEN[:8]}...")
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()

    # Send device attributes once after connection
    time.sleep(1)  # Give time for connection
    if client.is_connected():
        client.publish('v1/devices/me/attributes', json.dumps(ATTRIBUTES), qos=1)
        print(f"📦 Sent device attributes: {json.dumps(ATTRIBUTES)}")
    else:
        print("❌ MQTT client not connected. Could not send attributes.")

    print("🚀 Simulator started! Sending realistic home security data every", REPORT_INTERVAL, "seconds.")
    print("📊 Data includes: Doors, Motion, Window, Smoke, Temperature, and System Status")
    print("⏰ Simulation adapts based on time of day (Home/Away/Night modes)")
    print("Press Ctrl+C to stop.\n")

    while True:
        telemetry_data = get_realistic_home_data()
        # Add battery simulation HERE
        battery_level = round(random.uniform(30.0, 100.0), 1)
        telemetry_data["battery_level"] = battery_level
        payload = json.dumps(telemetry_data, indent=2)
        print(f"📤 Sending flat telemetry payload: {payload}")
        print("-" * 60)
        if client.is_connected():
            result = client.publish('v1/devices/me/telemetry', payload, qos=1)
            if result.rc != 0:
                print(f"❌ Failed to publish data, error code: {result.rc}")
        else:
            print("❌ MQTT client not connected. Skipping publish.")
        time.sleep(REPORT_INTERVAL)  # Use customizable interval

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped by user.")
except Exception as e:
    print(f"💥 An error occurred: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    print("👋 Disconnected from ThingsBoard. Goodbye!")