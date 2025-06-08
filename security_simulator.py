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
    """Generate realistic home security data based on time and patterns"""
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

    data = {
        "main_door_status": main_door,
        "kitchen_door_status": kitchen_door,
        "bedroom1_door_status": bedroom1_door,
        "bedroom2_door_status": bedroom2_door,
        "bathroom_door_status": bathroom_door,
        "living_room_motion": living_room_motion,
        "kitchen_motion": kitchen_motion,
        "living_room_window_status": living_room_window,
        "kitchen_smoke_detector": kitchen_smoke,
        "internal_temperature": internal_temperature,
        "occupancy_mode": home_state["occupancy_mode"],
        "system_status": system_status,
        "timestamp": int(time.time() * 1000),
        "room": "all",  # Added for possible filtering
        "intrusion_alert": intrusion_alert
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

        # Add battery simulation
        battery_level = round(random.uniform(30.0, 100.0), 1)

        # Build and send a well-structured payload for ThingsBoard visualization
        home_payload = {
            "device_id": ATTRIBUTES["device_id"],
            "timestamp": telemetry_data["timestamp"],
            "occupancy_mode": telemetry_data["occupancy_mode"],
            "system_status": telemetry_data["system_status"],
            "internal_temperature": telemetry_data["internal_temperature"],
            "intrusion_alert": telemetry_data["intrusion_alert"],
            "battery_level": battery_level,
            "doors": {
                "main": telemetry_data["main_door_status"],
                "kitchen": telemetry_data["kitchen_door_status"],
                "bedroom1": telemetry_data["bedroom1_door_status"],
                "bedroom2": telemetry_data["bedroom2_door_status"],
                "bathroom": telemetry_data["bathroom_door_status"]
            },
            "rooms": [
                {
                    "name": "living_room",
                    "motion": telemetry_data["living_room_motion"],
                    "window": telemetry_data["living_room_window_status"]
                },
                {
                    "name": "kitchen",
                    "motion": telemetry_data["kitchen_motion"],
                    "smoke": telemetry_data["kitchen_smoke_detector"],
                    "door": telemetry_data["kitchen_door_status"]
                },
                {
                    "name": "bedroom1",
                    "door": telemetry_data["bedroom1_door_status"]
                },
                {
                    "name": "bedroom2",
                    "door": telemetry_data["bedroom2_door_status"]
                },
                {
                    "name": "bathroom",
                    "door": telemetry_data["bathroom_door_status"]
                }
            ],
            "location": ATTRIBUTES["location"]
        }
        payload = json.dumps(home_payload, indent=2)
        print(f"📤 Sending structured home payload: {payload}")
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