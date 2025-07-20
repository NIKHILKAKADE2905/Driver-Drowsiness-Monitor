
import time
import pygame
import requests
import webbrowser
from dotenv import load_dotenv
import os
import sys



# =========================
# 🔧 Configuration
# =========================
def resource_path(relative_path):
    return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")), relative_path)

# Load .env from correct location
env_path = resource_path('.env')
load_dotenv(env_path)

# Now safely get the API key
API_KEY = os.getenv("API_KEY")

# =========================
# 🔔 Sound Playback
# =========================
def play_sound(sound_type):
    sound_map = {
        "strong_alarm": "sounds/emergency-alarm-with-reverb-29431.mp3",
        "alarm": "sounds/beep-beep-beep-beep-80262.mp3"
    }

    if sound_type in sound_map:
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path(sound_map[sound_type]))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

# =========================
# 🧠 Drowsiness Logic
# =========================
def evaluate_driver_state(blink_count, avg_blink_duration, total_eye_closure_duration, yawn_count, detected_classes):
    '''you can change the thresholds depending on your criteria for monitoring'''
    head_dropped = "head_dropped" in detected_classes

    if (total_eye_closure_duration >= 5 and head_dropped) or total_eye_closure_duration >= 5:
        return "STRONG", (f"\n🔴 Critical Drowsiness Detected!\nHead dropped or prolonged eye closure with {total_eye_closure_duration} seconds.\n🚨 Rerouting to rest stop...", "strong_alarm")

    elif  yawn_count >= 3:         #blink_count <= 20 and 1 <= avg_blink_duration <= 1.5 and
        return "MODERATE", ("\n🟠 Warning: Multiple drowsiness signs.\nLow blink rate + yawning.\n⚠️ Suggest break?", "alarm")

    else:
        return "NORMAL", ("🟢 Driver appears alert. Monitoring...", "none")

# =========================
# 📍 Rerouting Logic
# =========================
def get_user_coordinates():
    # try:
    #     response = requests.get("https://ipinfo.io/json")
    #     data = response.json()
    #     loc = data.get("loc")  # Format: "latitude,longitude"
    #     print(f"[INFO] Location fetched: {loc}")
    #     return loc
    # except Exception as e:
    #     print(f"[ERROR] Unable to get location: {e}")

    return "19.107094,73.066216"  # this is for testong purpose, Replace with dynamic GPS later

def find_nearest_refreshment_stops(origin_loc, types=("gas_station", "restaurant"), limit=4):
    all_results = []
    for place_type in types:
        url = "https://maps.gomaps.pro/maps/api/place/nearbysearch/json"
        params = {
            "location": origin_loc,
            "rankby": "distance",
            "type": place_type,
            "key": API_KEY
        }
        res = requests.get(url, params=params).json()
        results = res.get("results", [])[:limit]
        for place in results:
            place["place_type"] = place_type
        all_results.extend(results)
    return all_results

def get_route(origin_loc, dest_latlng):
    url = "https://maps.gomaps.pro/maps/api/directions/json"
    params = {
        "origin": origin_loc,
        "destination": f"{dest_latlng['lat']},{dest_latlng['lng']}",
        "mode": "driving",
        "key": API_KEY
    }
    res = requests.get(url, params=params).json()
    if "routes" in res and res["routes"]:
        return res["routes"][0]["legs"][0]
    return None

def reroute_to_nearest_stop():
    origin = get_user_coordinates()
    stops = find_nearest_refreshment_stops(origin)
    nearest = None
    min_dist = float("inf")
    for stop in stops:
        route = get_route(origin, stop["geometry"]["location"])
        if route and route["distance"]["value"] < min_dist:
            min_dist = route["distance"]["value"]
            nearest = {"stop": stop, "route": route}

    if nearest:
        stop = nearest["stop"]
        print(f"\nNearest Stop: {stop['name']} ({stop['place_type']})")
        print(f"Distance: {nearest['route']['distance']['text']} | ETA: {nearest['route']['duration']['text']}")
        url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={stop['geometry']['location']['lat']},{stop['geometry']['location']['lng']}&travelmode=driving"
        webbrowser.open(url)


# =========================
# 👁️ Blink and Yawn Trackers
# =========================
class BlinkTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.prev = "eye_open"
        self.blinks = []
        self.blink_durations = []
        self.start = None
        self.total_eye_closure_duration = 0
        self.closure_start = None


    def update(self, classes):
        eye_closed = "eye_closed" in classes

        if eye_closed:
            if self.prev == "eye_open":
                self.start = time.time()  # start of blink
                self.closure_start = time.time()  # start of prolonged closure
            elif self.closure_start:
                self.total_eye_closure_duration = time.time() - self.closure_start

        elif not eye_closed and self.prev == "eye_closed":
            if self.start:
                blink_duration = time.time() - self.start
                self.blink_durations.append(blink_duration)
                self.blinks.append(self.start)
                self.start = None
                self.closure_start = None
                self.total_eye_closure_duration = 0


        self.prev = "eye_closed" if eye_closed else "eye_open"
        self.cleanup()

    def cleanup(self):
        # keep only recent 2 mins of data
        self.blinks = [t for t in self.blinks if time.time() - t <= 120]
        self.blink_durations = self.blink_durations[-len(self.blinks):]

    def get_stats(self):
        blink_count = len(self.blinks)
        avg_duration = sum(self.blink_durations) / blink_count if blink_count else 0
        return blink_count, avg_duration, self.total_eye_closure_duration


class YawnTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.prev = "no_yawn"
        self.timestamps = []
        self.start = None

    def update(self, classes):
        if "yawn" in classes:
            if self.prev == "no_yawn":
                self.start = time.time()
        elif "no_yawn" in classes and self.prev == "yawn" and self.start:
            duration = time.time() - self.start
            if 2 <= duration <= 10:
                self.timestamps.append(self.start)
            self.start = None

        self.prev = "yawn" if "yawn" in classes else "no_yawn"
        self.cleanup()

    def cleanup(self):
        self.timestamps = [t for t in self.timestamps if time.time() - t <= 120]

    def get_stats(self):
        return len(self.timestamps)

# =========================
# 🎥 Thread Functions (optional)
# =========================
def blink_thread(tracker, detected_classes):
    tracker.update(detected_classes)

def yawn_thread(tracker, detected_classes):
    tracker.update(detected_classes)





