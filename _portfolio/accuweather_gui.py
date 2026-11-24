"""
AccuWeather Pulse - Modern Weather Dashboard (CustomTkinter)
============================================================
Upgraded AccuWeather GUI featuring:
1. Dynamic Weather Icon System (AccuWeather Codes 1-44 -> local `icons/{code}.png` with Emoji fallback)
2. Expanded Weather Data (Search bar, Refresh, Timestamp, °C/°F toggle, 6-metric Current Weather Grid,
   12-Hour Horizontal Scrollable Forecast, and 5-Day Daily Forecast)
3. Dynamic Day/Night Theme based on API's `IsDayTime` boolean
4. `MOCK_MODE` support using local JSON files in `mock_data/` to preserve the 50 calls/day quota
5. Robust error handling for invalid city names, network timeouts, and HTTP 401/429/503 quota limits
"""

import os
import sys
import json
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

# ==============================================================================
# TOP-LEVEL CONFIGURATION (Edit API_KEY and MOCK_MODE here)
# ==============================================================================
API_KEY = "YOUR_ACCUWEATHER_API_KEY_HERE"  # <-- Paste your AccuWeather API Key here
MOCK_MODE = True                           # <-- Set False to use live AccuWeather API
DEFAULT_CITY = "Bangkok"                   # <-- Default city loaded on startup
REQUEST_TIMEOUT_SECONDS = 10               # <-- Network timeout for API requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")
MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")

# Ensure CustomTkinter is importable across standard and Conda Python environments on Windows
try:
    import customtkinter as ctk
except ImportError:
    _conda_site = os.path.expanduser("~/anaconda3/Lib/site-packages")
    if os.path.isdir(_conda_site) and _conda_site not in sys.path:
        sys.path.append(_conda_site)
    import customtkinter as ctk

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ==============================================================================
# ACCUWEATHER ICON CODE MAPPING (1 - 44)
# ==============================================================================
# Maps AccuWeather's "WeatherIcon" integer (1-44) to (Unicode Emoji, Description)
ACCUWEATHER_ICON_MAP = {
    1:  ("☀️", "Sunny"),
    2:  ("🌤️", "Mostly Sunny"),
    3:  ("⛅", "Partly Sunny"),
    4:  ("⛅", "Intermittent Clouds"),
    5:  ("🌤️", "Hazy Sunshine"),
    6:  ("🌥️", "Mostly Cloudy"),
    7:  ("☁️", "Cloudy"),
    8:  ("☁️", "Dreary (Overcast)"),
    9:  ("🌫️", "Foggy"),
    10: ("🌫️", "Mist"),
    11: ("🌫️", "Fog"),
    12: ("🌦️", "Showers"),
    13: ("🌦️", "Mostly Cloudy w/ Showers"),
    14: ("🌦️", "Partly Sunny w/ Showers"),
    15: ("⛈️", "Thunderstorms"),
    16: ("⛈️", "Mostly Cloudy w/ T-Storms"),
    17: ("⛈️", "Partly Sunny w/ T-Storms"),
    18: ("🌧️", "Rain"),
    19: ("🌨️", "Flurries"),
    20: ("🌨️", "Mostly Cloudy w/ Flurries"),
    21: ("🌨️", "Partly Sunny w/ Flurries"),
    22: ("❄️", "Snow"),
    23: ("❄️", "Mostly Cloudy w/ Snow"),
    24: ("🧊", "Ice"),
    25: ("🌨️", "Sleet"),
    26: ("🌧️", "Freezing Rain"),
    27: ("🌨️", "Freezing Drizzle"),
    28: ("🌧️", "Heavy Rain"),
    29: ("🌨️", "Rain and Snow"),
    30: ("🌡️", "Hot"),
    31: ("🥶", "Cold"),
    32: ("💨", "Windy"),
    33: ("🌙", "Clear (Night)"),
    34: ("🌙", "Mostly Clear (Night)"),
    35: ("☁️", "Partly Cloudy (Night)"),
    36: ("☁️", "Intermittent Clouds (Night)"),
    37: ("🌕", "Hazy Moonlight"),
    38: ("☁️", "Mostly Cloudy (Night)"),
    39: ("🌧️", "Partly Cloudy w/ Showers (Night)"),
    40: ("🌧️", "Mostly Cloudy w/ Showers (Night)"),
    41: ("⛈️", "Partly Cloudy w/ T-Storms (Night)"),
    42: ("⛈️", "Mostly Cloudy w/ T-Storms (Night)"),
    43: ("🌨️", "Mostly Cloudy w/ Flurries (Night)"),
    44: ("❄️", "Mostly Cloudy w/ Snow (Night)"),
}


# ==============================================================================
# DYNAMIC DAY / NIGHT THEME PALETTES
# ==============================================================================
THEMES = {
    "day": {
        "appearance": "Light",
        "window_bg": "#EAF2FB",
        "header_bg": "#FFFFFF",
        "card_bg": "#FFFFFF",
        "card_alt_bg": "#F3F8FE",
        "card_border": "#D5E3F3",
        "accent": "#F97316",
        "accent_hover": "#EA580C",
        "accent_soft": "#FFF0E5",
        "secondary_btn": "#E2ECF8",
        "secondary_hover": "#D0E0F3",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "rain_text": "#0284C7",
        "badge_bg": "#FEF3C7",
        "badge_text": "#B45309",
        "progress_track": "#E2E8F0",
        "temp_bar_fill": "#F97316",
    },
    "night": {
        "appearance": "Dark",
        "window_bg": "#0B1329",
        "header_bg": "#141E38",
        "card_bg": "#15203B",
        "card_alt_bg": "#1C294A",
        "card_border": "#26365E",
        "accent": "#FF7A1A",
        "accent_hover": "#F97316",
        "accent_soft": "#282238",
        "secondary_btn": "#223156",
        "secondary_hover": "#2E406E",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "rain_text": "#38BDF8",
        "badge_bg": "#1E293B",
        "badge_text": "#FBBF24",
        "progress_track": "#253458",
        "temp_bar_fill": "#FB923C",
    },
}


# ==============================================================================
# MOCK DATA GENERATOR / LOADER
# ==============================================================================
MOCK_CITY_PRESETS = {
    "bangkok": {
        "Key": "318849",
        "EnglishName": "Bangkok",
        "AdminArea": "Bangkok",
        "Country": "Thailand",
        "IsDayTime": True,
        "WeatherIcon": 3,
        "WeatherText": "Partly Sunny",
        "TempC": 32.4,
        "RealFeelC": 36.8,
        "RealFeelPhrase": "Very Warm",
        "Humidity": 62,
        "UVIndex": 6,
        "UVIndexText": "High",
        "WindKmh": 14.8,
        "WindDir": "SSW",
        "PrecipProb": 25,
    },
    "chiang mai": {
        "Key": "317505",
        "EnglishName": "Chiang Mai",
        "AdminArea": "Chiang Mai",
        "Country": "Thailand",
        "IsDayTime": True,
        "WeatherIcon": 2,
        "WeatherText": "Mostly Sunny",
        "TempC": 28.5,
        "RealFeelC": 30.2,
        "RealFeelPhrase": "Pleasant",
        "Humidity": 52,
        "UVIndex": 7,
        "UVIndexText": "High",
        "WindKmh": 11.2,
        "WindDir": "NW",
        "PrecipProb": 15,
    },
    "phuket": {
        "Key": "320075",
        "EnglishName": "Phuket",
        "AdminArea": "Phuket",
        "Country": "Thailand",
        "IsDayTime": True,
        "WeatherIcon": 14,
        "WeatherText": "Partly Sunny w/ Showers",
        "TempC": 30.8,
        "RealFeelC": 35.6,
        "RealFeelPhrase": "Humid",
        "Humidity": 76,
        "UVIndex": 8,
        "UVIndexText": "Very High",
        "WindKmh": 19.4,
        "WindDir": "WSW",
        "PrecipProb": 65,
    },
    "tokyo": {
        "Key": "226396",
        "EnglishName": "Tokyo",
        "AdminArea": "Tokyo",
        "Country": "Japan",
        "IsDayTime": False,
        "WeatherIcon": 34,
        "WeatherText": "Mostly Clear",
        "TempC": 14.2,
        "RealFeelC": 13.0,
        "RealFeelPhrase": "Cool",
        "Humidity": 48,
        "UVIndex": 0,
        "UVIndexText": "Low",
        "WindKmh": 16.5,
        "WindDir": "NNE",
        "PrecipProb": 10,
    },
    "london": {
        "Key": "328328",
        "EnglishName": "London",
        "AdminArea": "England",
        "Country": "United Kingdom",
        "IsDayTime": False,
        "WeatherIcon": 40,
        "WeatherText": "Mostly Cloudy w/ Showers",
        "TempC": 9.4,
        "RealFeelC": 6.8,
        "RealFeelPhrase": "Chilly",
        "Humidity": 84,
        "UVIndex": 0,
        "UVIndexText": "Low",
        "WindKmh": 24.0,
        "WindDir": "W",
        "PrecipProb": 75,
    },
}


def ensure_mock_files_exist():
    """Creates default sample JSON files in `mock_data/` and `icons/` directory if missing."""
    try:
        os.makedirs(ICONS_DIR, exist_ok=True)
        os.makedirs(MOCK_DATA_DIR, exist_ok=True)
    except OSError:
        return

    loc_path = os.path.join(MOCK_DATA_DIR, "location.json")
    cur_path = os.path.join(MOCK_DATA_DIR, "current_conditions.json")
    hr_path = os.path.join(MOCK_DATA_DIR, "hourly_12hour.json")
    day_path = os.path.join(MOCK_DATA_DIR, "daily_5day.json")

    if not os.path.exists(loc_path):
        with open(loc_path, "w", encoding="utf-8") as f:
            json.dump([{
                "Version": 1,
                "Key": "318849",
                "Type": "City",
                "LocalizedName": "Bangkok",
                "EnglishName": "Bangkok",
                "Country": {"ID": "TH", "EnglishName": "Thailand"},
                "AdministrativeArea": {"ID": "10", "EnglishName": "Bangkok"},
            }], f, indent=2)

    if not os.path.exists(cur_path):
        with open(cur_path, "w", encoding="utf-8") as f:
            json.dump([{
                "LocalObservationDateTime": datetime.now().isoformat(),
                "WeatherText": "Partly Sunny",
                "WeatherIcon": 3,
                "HasPrecipitation": False,
                "IsDayTime": True,
                "Temperature": {
                    "Metric": {"Value": 32.4, "Unit": "C"},
                    "Imperial": {"Value": 90.3, "Unit": "F"},
                },
                "RealFeelTemperature": {
                    "Metric": {"Value": 36.8, "Unit": "C", "Phrase": "Very Warm"},
                    "Imperial": {"Value": 98.2, "Unit": "F", "Phrase": "Very Warm"},
                },
                "RelativeHumidity": 62,
                "UVIndex": 6,
                "UVIndexText": "High",
                "Wind": {
                    "Direction": {"Degrees": 205, "Localized": "SSW", "English": "SSW"},
                    "Speed": {
                        "Metric": {"Value": 14.8, "Unit": "km/h"},
                        "Imperial": {"Value": 9.2, "Unit": "mi/h"},
                    },
                },
                "PrecipitationProbability": 25,
            }], f, indent=2)

    if not os.path.exists(hr_path):
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        hours = []
        icons = [3, 4, 35, 39, 38, 35, 34, 33, 33, 34, 35, 2]
        temps = [32.4, 31.2, 29.8, 28.6, 27.9, 27.3, 26.8, 26.4, 26.0, 25.7, 25.4, 26.1]
        probs = [25, 30, 35, 60, 40, 25, 15, 10, 10, 10, 15, 20]
        for i in range(12):
            dt = now + timedelta(hours=i)
            code = icons[i]
            hours.append({
                "DateTime": dt.isoformat(),
                "WeatherIcon": code,
                "IconPhrase": ACCUWEATHER_ICON_MAP.get(code, ("⛅", "Partly Cloudy"))[1],
                "IsDaylight": 6 <= dt.hour < 18,
                "Temperature": {"Value": temps[i], "Unit": "C"},
                "PrecipitationProbability": probs[i],
            })
        with open(hr_path, "w", encoding="utf-8") as f:
            json.dump(hours, f, indent=2)

    if not os.path.exists(day_path):
        today = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        days = []
        day_specs = [
            (3, "Partly sunny", 39, 25.2, 33.4, 25),
            (2, "Mostly sunny", 34, 25.5, 34.0, 20),
            (14, "Partly sunny w/ showers", 40, 24.8, 32.1, 65),
            (15, "Thunderstorms", 38, 24.2, 31.0, 80),
            (1, "Sunny", 33, 24.9, 33.2, 10),
        ]
        for idx, (d_icon, d_phrase, n_icon, t_min, t_max, prob) in enumerate(day_specs):
            dt = today + timedelta(days=idx)
            days.append({
                "Date": dt.isoformat(),
                "Temperature": {
                    "Minimum": {"Value": t_min, "Unit": "C"},
                    "Maximum": {"Value": t_max, "Unit": "C"},
                },
                "Day": {
                    "Icon": d_icon,
                    "IconPhrase": d_phrase,
                    "PrecipitationProbability": prob,
                },
                "Night": {
                    "Icon": n_icon,
                    "IconPhrase": ACCUWEATHER_ICON_MAP.get(n_icon, ("🌙", "Clear"))[1],
                    "PrecipitationProbability": max(5, prob - 10),
                },
            })
        with open(day_path, "w", encoding="utf-8") as f:
            json.dump({
                "Headline": {
                    "Text": "Warm and humid this week with isolated afternoon showers midweek"
                },
                "DailyForecasts": days,
            }, f, indent=2)


# ==============================================================================
# CUSTOM ERROR EXCEPTION
# ==============================================================================
class WeatherServiceError(Exception):
    """Custom exception carrying user-friendly title, message, and error category."""
    def __init__(self, title: str, message: str, category: str = "error"):
        super().__init__(message)
        self.title = title
        self.message = message
        self.category = category


# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class AccuWeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ensure_mock_files_exist()

        # Window Setup
        self.title("AccuWeather Pulse — Modern Weather Dashboard")
        self.geometry("1120x840")
        self.minsize(960, 740)

        # Runtime State
        self.api_key = API_KEY.strip()
        self.mock_mode = MOCK_MODE
        self.unit = "C"  # "C" or "F"
        self.is_daytime = True
        self.theme = THEMES["day"]
        self.current_city_query = DEFAULT_CITY
        self.last_updated_str = "Never"
        self.is_fetching = False

        # Cached Weather Payload
        self.location_info = None
        self.current_data = None
        self.hourly_data = []
        self.daily_data = {}

        # Image Cache: (icon_code, size) -> CTkImage | None
        self.icon_cache = {}

        # Build Layout & Load Initial Data
        self._build_ui()
        self._apply_theme(self.is_daytime)
        self.after(150, lambda: self.fetch_weather(DEFAULT_CITY))

    # --------------------------------------------------------------------------
    # ICON SYSTEM (1-44 -> Local PNG in `icons/` or Unicode Emoji Fallback)
    # --------------------------------------------------------------------------
    def get_icon_visual(self, icon_code: int, size: int = 48):
        """
        Maps AccuWeather WeatherIcon integer (1-44) to a local PNG image in `icons/`
        if present (e.g., `icons/1.png` or `icons/01.png`), with automatic fallback
        to a Unicode weather emoji and descriptive text.

        Returns:
            dict: {"ctk_image": CTkImage | None, "emoji": str, "label": str, "code": int}
        """
        try:
            code = int(icon_code)
        except (TypeError, ValueError):
            code = 1

        emoji, description = ACCUWEATHER_ICON_MAP.get(code, ("⛅", f"Weather #{code}"))
        cache_key = (code, size)

        if cache_key not in self.icon_cache:
            ctk_img = None
            if PIL_AVAILABLE and os.path.isdir(ICONS_DIR):
                candidate_files = [
                    os.path.join(ICONS_DIR, f"{code}.png"),
                    os.path.join(ICONS_DIR, f"{code:02d}.png"),
                ]
                for file_path in candidate_files:
                    if os.path.isfile(file_path):
                        try:
                            pil_img = Image.open(file_path).convert("RGBA")
                            ctk_img = ctk.CTkImage(
                                light_image=pil_img,
                                dark_image=pil_img,
                                size=(size, size),
                            )
                            break
                        except Exception:
                            ctk_img = None
            self.icon_cache[cache_key] = ctk_img

        return {
            "ctk_image": self.icon_cache[cache_key],
            "emoji": emoji,
            "label": description,
            "code": code,
        }

    def _configure_icon_label(self, label_widget: ctk.CTkLabel, icon_code: int, img_size: int, emoji_font_size: int):
        """Applies either the loaded transparent PNG CTkImage or the Unicode emoji fallback to a CTkLabel."""
        vis = self.get_icon_visual(icon_code, size=img_size)
        if vis["ctk_image"] is not None:
            label_widget.configure(image=vis["ctk_image"], text="")
        else:
            label_widget.configure(
                image=None,
                text=vis["emoji"],
                font=ctk.CTkFont(family="Segoe UI Emoji", size=emoji_font_size),
            )

    # --------------------------------------------------------------------------
    # TEMPERATURE, SPEED & UV HELPERS
    # --------------------------------------------------------------------------
    def format_temp_from_c(self, temp_c, include_unit: bool = True, decimals: int = 1) -> str:
        if temp_c is None:
            return "--"
        val = float(temp_c)
        if self.unit == "F":
            val = (val * 9.0 / 5.0) + 32.0
        fmt = f"{val:.{decimals}f}" if decimals > 0 else f"{round(val)}"
        return f"{fmt}°{self.unit}" if include_unit else f"{fmt}°"

    def extract_temp_c(self, temp_obj) -> float:
        """Extracts Celsius value from either a Metric/Imperial dict or single Value/Unit dict."""
        if not isinstance(temp_obj, dict):
            return 0.0
        if "Metric" in temp_obj and isinstance(temp_obj["Metric"], dict):
            return float(temp_obj["Metric"].get("Value", 0.0))
        val = float(temp_obj.get("Value", 0.0))
        unit = str(temp_obj.get("Unit", "C")).upper()
        if unit == "F":
            return (val - 32.0) * 5.0 / 9.0
        return val

    def format_wind_speed(self, wind_obj) -> str:
        """Formats wind speed in km/h (when °C) or mph (when °F)."""
        if not isinstance(wind_obj, dict):
            return "-- km/h"
        speed_obj = wind_obj.get("Speed", {})
        kmh = 0.0
        if "Metric" in speed_obj:
            kmh = float(speed_obj["Metric"].get("Value", 0.0))
        elif "Value" in speed_obj:
            val = float(speed_obj.get("Value", 0.0))
            unit = str(speed_obj.get("Unit", "km/h")).lower()
            kmh = val * 1.60934 if "mi" in unit else val

        if self.unit == "F":
            mph = kmh / 1.60934
            return f"{mph:.1f} mph"
        return f"{kmh:.1f} km/h"

    @staticmethod
    def get_uv_risk_info(uv_index: int, api_uv_text: str = ""):
        """Returns (risk_label, hex_color, normalized_0_to_1)."""
        try:
            uv = int(uv_index)
        except (TypeError, ValueError):
            uv = 0

        if uv <= 2:
            level, color = "Low", "#22C55E"
        elif uv <= 5:
            level, color = "Moderate", "#EAB308"
        elif uv <= 7:
            level, color = "High", "#F97316"
        elif uv <= 10:
            level, color = "Very High", "#EF4444"
        else:
            level, color = "Extreme", "#A855F7"

        label = api_uv_text.strip() if api_uv_text and api_uv_text.strip() else level
        progress = min(max(uv / 11.0, 0.06), 1.0)
        return label, color, progress

    # --------------------------------------------------------------------------
    # UI CONSTRUCTION
    # --------------------------------------------------------------------------
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. HEADER & SEARCH BAR
        self.header_frame = ctk.CTkFrame(self, corner_radius=18, border_width=1)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 6))
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Left Brand & Theme Mode Badge
        brand_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_box.grid(row=0, column=0, padx=(16, 10), pady=(12, 6), sticky="w")

        self.brand_title = ctk.CTkLabel(
            brand_box,
            text="☀️ AccuWeather Pulse",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        self.brand_title.grid(row=0, column=0, sticky="w")

        self.theme_badge = ctk.CTkLabel(
            brand_box,
            text="DAY MODE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            corner_radius=8,
            padx=8,
            pady=2,
        )
        self.theme_badge.grid(row=0, column=1, padx=(10, 0))

        # Center Search Bar
        search_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        search_box.grid(row=0, column=1, padx=8, pady=(12, 6), sticky="ew")
        search_box.grid_columnconfigure(0, weight=1)

        self.city_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Search city (e.g., Bangkok, Chiang Mai, Phuket, Tokyo, London)...",
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self.city_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.city_entry.insert(0, DEFAULT_CITY)
        self.city_entry.bind("<Return>", lambda _e: self.on_search())

        self.search_btn = ctk.CTkButton(
            search_box,
            text="🔍 Search",
            width=96,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.on_search,
        )
        self.search_btn.grid(row=0, column=1, padx=(0, 6))

        self.refresh_btn = ctk.CTkButton(
            search_box,
            text="⟳ Refresh",
            width=94,
            height=38,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.on_refresh,
        )
        self.refresh_btn.grid(row=0, column=2)

        # Right Controls (°C/°F Toggle, Mock Mode Switch, Day/Night Preview, API Key)
        controls_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        controls_box.grid(row=0, column=2, padx=(8, 16), pady=(12, 6), sticky="e")

        self.unit_toggle = ctk.CTkSegmentedButton(
            controls_box,
            values=["°C", "°F"],
            width=84,
            height=34,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.on_unit_change,
        )
        self.unit_toggle.set("°C")
        self.unit_toggle.grid(row=0, column=0, padx=(0, 10))

        self.mock_switch = ctk.CTkSwitch(
            controls_box,
            text="Mock JSON",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.on_toggle_mock_mode,
        )
        if self.mock_mode:
            self.mock_switch.select()
        else:
            self.mock_switch.deselect()
        self.mock_switch.grid(row=0, column=1, padx=(0, 10))

        self.theme_preview_btn = ctk.CTkButton(
            controls_box,
            text="🌓 Day/Night",
            width=96,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self.on_toggle_day_night_preview,
        )
        self.theme_preview_btn.grid(row=0, column=2, padx=(0, 6))

        self.api_key_btn = ctk.CTkButton(
            controls_box,
            text="🔑 API Key",
            width=86,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self.on_open_api_key_dialog,
        )
        self.api_key_btn.grid(row=0, column=3)

        # Sub-Header Bar: Quick Cities, Status Message & Last-Updated Timestamp
        sub_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        sub_header.grid(row=1, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 10))
        sub_header.grid_columnconfigure(1, weight=1)

        quick_box = ctk.CTkFrame(sub_header, fg_color="transparent")
        quick_box.grid(row=0, column=0, sticky="w")

        self.quick_label = ctk.CTkLabel(
            quick_box,
            text="Quick Cities:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
        )
        self.quick_label.pack(side="left", padx=(0, 6))

        self.quick_city_buttons = []
        for city_name in ["Bangkok", "Chiang Mai", "Phuket", "Tokyo", "London"]:
            btn = ctk.CTkButton(
                quick_box,
                text=city_name,
                height=24,
                width=74,
                corner_radius=6,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                command=lambda c=city_name: self.select_quick_city(c),
            )
            btn.pack(side="left", padx=3)
            self.quick_city_buttons.append(btn)

        self.status_label = ctk.CTkLabel(
            sub_header,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.status_label.grid(row=0, column=1, padx=12)

        self.timestamp_label = ctk.CTkLabel(
            sub_header,
            text="Last updated: --",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        )
        self.timestamp_label.grid(row=0, column=2, sticky="e")

        # 2. MAIN SCROLLABLE DASHBOARD BODY
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(2, 12))
        self.main_scroll.grid_columnconfigure(0, weight=1)

        # Error / Notification Banner (Hidden unless an error occurs)
        self.banner_frame = ctk.CTkFrame(self.main_scroll, corner_radius=12, border_width=1)
        self.banner_frame.grid_columnconfigure(0, weight=1)
        self.banner_label = ctk.CTkLabel(
            self.banner_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=920,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        )
        self.banner_label.grid(row=0, column=0, sticky="ew", padx=14, pady=10)
        self.banner_close_btn = ctk.CTkButton(
            self.banner_frame,
            text="Dismiss",
            width=70,
            height=26,
            corner_radius=6,
            command=self.hide_banner,
        )
        self.banner_close_btn.grid(row=0, column=1, padx=(6, 12), pady=10)

        # TOP SECTION: Hero Current Weather Card (Left) + 6-Metric Grid (Right)
        self.top_section = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.top_section.grid(row=1, column=0, sticky="ew", padx=6, pady=6)
        self.top_section.grid_columnconfigure(0, weight=5)
        self.top_section.grid_columnconfigure(1, weight=7)
        self.top_section.grid_rowconfigure(0, weight=1)

        # Left Hero Card
        self.hero_card = ctk.CTkFrame(self.top_section, corner_radius=18, border_width=1)
        self.hero_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=2)
        self.hero_card.grid_columnconfigure(0, weight=1)

        self.hero_city_label = ctk.CTkLabel(
            self.hero_card,
            text="Bangkok",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            anchor="w",
        )
        self.hero_city_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))

        self.hero_region_label = ctk.CTkLabel(
            self.hero_card,
            text="Bangkok, Thailand",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
        )
        self.hero_region_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(2, 8))

        # Hero Center Row: Weather Icon + Big Temperature
        hero_center = ctk.CTkFrame(self.hero_card, fg_color="transparent")
        hero_center.grid(row=2, column=0, sticky="ew", padx=20, pady=6)

        self.hero_icon_label = ctk.CTkLabel(
            hero_center,
            text="⛅",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=64),
        )
        self.hero_icon_label.pack(side="left", padx=(0, 18))

        hero_temp_box = ctk.CTkFrame(hero_center, fg_color="transparent")
        hero_temp_box.pack(side="left", fill="x", expand=True)

        self.hero_temp_label = ctk.CTkLabel(
            hero_temp_box,
            text="32.4°C",
            font=ctk.CTkFont(family="Segoe UI", size=44, weight="bold"),
            anchor="w",
        )
        self.hero_temp_label.pack(anchor="w")

        self.hero_condition_label = ctk.CTkLabel(
            hero_temp_box,
            text="Partly Sunny (Icon #3)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            anchor="w",
        )
        self.hero_condition_label.pack(anchor="w", pady=(2, 0))

        self.hero_hi_lo_label = ctk.CTkLabel(
            self.hero_card,
            text="RealFeel® 36.8°C • High 33.4°C / Low 25.2°C",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
        )
        self.hero_hi_lo_label.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 4))

        self.hero_headline_label = ctk.CTkLabel(
            self.hero_card,
            text="Warm and humid this week with isolated afternoon showers midweek",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            anchor="w",
            justify="left",
            wraplength=360,
        )
        self.hero_headline_label.grid(row=4, column=0, sticky="ew", padx=20, pady=(2, 16))

        # Right 6-Metric Current Weather Grid (2 rows x 3 columns)
        self.metrics_grid = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.metrics_grid.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=2)
        for col in range(3):
            self.metrics_grid.grid_columnconfigure(col, weight=1, uniform="metric_col")
        for row in range(2):
            self.metrics_grid.grid_rowconfigure(row, weight=1, uniform="metric_row")

        self.metric_cards = {}
        metric_specs = [
            ("actual_temp", "🌡️ Actual Temperature", "32.4°C", "High 33.4°C / Low 25.2°C", False),
            ("realfeel", "🤗 RealFeel® Temp", "36.8°C", "Phrase: Very Warm", False),
            ("uv_index", "☀️ UV Index", "6 (High)", "Sun protection recommended", True),
            ("humidity", "💧 Humidity", "62%", "Dew Point: 24.1°C", True),
            ("wind", "💨 Wind Speed & Dir", "14.8 km/h SSW", "Direction: 205° • Gusts 22.4 km/h", False),
            ("precip", "🌧️ Precipitation Prob.", "25%", "Current: No active precipitation", True),
        ]

        for idx, (key, title, default_val, default_sub, has_bar) in enumerate(metric_specs):
            r, c = divmod(idx, 3)
            card = ctk.CTkFrame(self.metrics_grid, corner_radius=16, border_width=1)
            card.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)
            card.grid_columnconfigure(0, weight=1)

            lbl_title = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                anchor="w",
            )
            lbl_title.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 2))

            lbl_value = ctk.CTkLabel(
                card,
                text=default_val,
                font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                anchor="w",
            )
            lbl_value.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 2))

            bar = None
            if has_bar:
                bar = ctk.CTkProgressBar(card, height=7, corner_radius=4)
                bar.set(0.5)
                bar.grid(row=2, column=0, sticky="ew", padx=14, pady=(4, 2))

            lbl_sub = ctk.CTkLabel(
                card,
                text=default_sub,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                anchor="w",
            )
            lbl_sub.grid(row=3 if has_bar else 2, column=0, sticky="ew", padx=14, pady=(2, 12))

            self.metric_cards[key] = {
                "frame": card,
                "title": lbl_title,
                "value": lbl_value,
                "sub": lbl_sub,
                "bar": bar,
            }

        # 3. 12-HOUR HOURLY FORECAST (Horizontal Scrollable Row)
        self.hourly_section = ctk.CTkFrame(self.main_scroll, corner_radius=18, border_width=1)
        self.hourly_section.grid(row=2, column=0, sticky="ew", padx=6, pady=(8, 6))
        self.hourly_section.grid_columnconfigure(0, weight=1)

        hourly_header = ctk.CTkFrame(self.hourly_section, fg_color="transparent")
        hourly_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(12, 2))
        hourly_header.grid_columnconfigure(0, weight=1)

        self.hourly_title_label = ctk.CTkLabel(
            hourly_header,
            text="🕒 12-Hour Hourly Forecast",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        )
        self.hourly_title_label.grid(row=0, column=0, sticky="w")

        self.hourly_hint_label = ctk.CTkLabel(
            hourly_header,
            text="Time • Weather Icon • Temperature • Rain Probability (%)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            anchor="e",
        )
        self.hourly_hint_label.grid(row=0, column=1, sticky="e")

        self.hourly_scroll = ctk.CTkScrollableFrame(
            self.hourly_section,
            orientation="horizontal",
            height=152,
            corner_radius=12,
            fg_color="transparent",
        )
        self.hourly_scroll.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 12))

        self.hourly_item_widgets = []

        # 4. 5-DAY DAILY FORECAST (Clean Structured Cards)
        self.daily_section = ctk.CTkFrame(self.main_scroll, corner_radius=18, border_width=1)
        self.daily_section.grid(row=3, column=0, sticky="ew", padx=6, pady=(6, 10))
        self.daily_section.grid_columnconfigure(0, weight=1)

        daily_header = ctk.CTkFrame(self.daily_section, fg_color="transparent")
        daily_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(12, 6))
        daily_header.grid_columnconfigure(0, weight=1)

        self.daily_title_label = ctk.CTkLabel(
            daily_header,
            text="📅 5-Day Daily Forecast",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
        )
        self.daily_title_label.grid(row=0, column=0, sticky="w")

        self.daily_subtitle_label = ctk.CTkLabel(
            daily_header,
            text="Day • Weather Icon & Condition • Rain % • Min / Max Temperature Range",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            anchor="e",
        )
        self.daily_subtitle_label.grid(row=0, column=1, sticky="e")

        self.daily_rows_container = ctk.CTkFrame(self.daily_section, fg_color="transparent")
        self.daily_rows_container.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        self.daily_rows_container.grid_columnconfigure(0, weight=1)

        self.daily_row_widgets = []

    # --------------------------------------------------------------------------
    # DYNAMIC DAY / NIGHT THEME ENGINE
    # --------------------------------------------------------------------------
    def _apply_theme(self, is_daytime: bool):
        """
        Switches the entire UI palette between Light/Day mode and Dark/Night mode
        based on the AccuWeather API's `IsDayTime` boolean.
        """
        self.is_daytime = bool(is_daytime)
        t = THEMES["day"] if self.is_daytime else THEMES["night"]
        self.theme = t

        ctk.set_appearance_mode(t["appearance"])
        self.configure(fg_color=t["window_bg"])

        # Header styling
        self.header_frame.configure(fg_color=t["header_bg"], border_color=t["card_border"])
        self.brand_title.configure(
            text="☀️ AccuWeather Pulse" if self.is_daytime else "🌙 AccuWeather Pulse",
            text_color=t["text_primary"],
        )
        self.theme_badge.configure(
            text="☀️ DAY THEME (IsDayTime=True)" if self.is_daytime else "🌙 NIGHT THEME (IsDayTime=False)",
            fg_color=t["badge_bg"],
            text_color=t["badge_text"],
        )

        self.city_entry.configure(
            fg_color=t["card_alt_bg"],
            border_color=t["card_border"],
            text_color=t["text_primary"],
        )
        self.search_btn.configure(fg_color=t["accent"], hover_color=t["accent_hover"], text_color="#FFFFFF")
        self.refresh_btn.configure(
            fg_color=t["secondary_btn"],
            hover_color=t["secondary_hover"],
            text_color=t["text_primary"],
        )
        self.theme_preview_btn.configure(
            fg_color=t["secondary_btn"],
            hover_color=t["secondary_hover"],
            text_color=t["text_primary"],
        )
        self.api_key_btn.configure(
            fg_color=t["secondary_btn"],
            hover_color=t["secondary_hover"],
            text_color=t["text_primary"],
        )
        self.unit_toggle.configure(
            fg_color=t["secondary_btn"],
            selected_color=t["accent"],
            selected_hover_color=t["accent_hover"],
            unselected_color=t["secondary_btn"],
            unselected_hover_color=t["secondary_hover"],
            text_color=t["text_primary"],
        )
        self.mock_switch.configure(
            progress_color=t["accent"],
            text_color=t["text_primary"],
        )

        self.quick_label.configure(text_color=t["text_secondary"])
        for btn in self.quick_city_buttons:
            btn.configure(
                fg_color=t["card_alt_bg"],
                hover_color=t["secondary_hover"],
                text_color=t["text_primary"],
            )

        self.status_label.configure(text_color=t["text_secondary"])
        self.timestamp_label.configure(text_color=t["text_secondary"])

        # Hero Card
        self.hero_card.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        self.hero_city_label.configure(text_color=t["text_primary"])
        self.hero_region_label.configure(text_color=t["text_secondary"])
        self.hero_temp_label.configure(text_color=t["text_primary"])
        self.hero_condition_label.configure(text_color=t["accent"])
        self.hero_hi_lo_label.configure(text_color=t["text_secondary"])
        self.hero_headline_label.configure(text_color=t["text_muted"])

        # 6 Metric Cards
        for key, item in self.metric_cards.items():
            item["frame"].configure(fg_color=t["card_bg"], border_color=t["card_border"])
            item["title"].configure(text_color=t["text_secondary"])
            item["value"].configure(text_color=t["text_primary"])
            item["sub"].configure(text_color=t["text_muted"])
            if item["bar"] is not None and key != "uv_index":
                item["bar"].configure(
                    fg_color=t["progress_track"],
                    progress_color=t["rain_text"] if key in ("humidity", "precip") else t["accent"],
                )

        # Hourly Section
        self.hourly_section.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        self.hourly_title_label.configure(text_color=t["text_primary"])
        self.hourly_hint_label.configure(text_color=t["text_muted"])
        for hw in self.hourly_item_widgets:
            is_first = hw.get("is_first", False)
            hw["card"].configure(
                fg_color=t["accent_soft"] if is_first else t["card_alt_bg"],
                border_color=t["accent"] if is_first else t["card_border"],
            )
            hw["time"].configure(text_color=t["accent"] if is_first else t["text_secondary"])
            hw["temp"].configure(text_color=t["text_primary"])
            hw["rain"].configure(text_color=t["rain_text"])

        # Daily Section
        self.daily_section.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        self.daily_title_label.configure(text_color=t["text_primary"])
        self.daily_subtitle_label.configure(text_color=t["text_muted"])
        for dw in self.daily_row_widgets:
            dw["row"].configure(fg_color=t["card_alt_bg"], border_color=t["card_border"])
            dw["day"].configure(text_color=t["text_primary"])
            dw["phrase"].configure(text_color=t["text_secondary"])
            dw["rain"].configure(text_color=t["rain_text"])
            dw["min"].configure(text_color=t["text_secondary"])
            dw["max"].configure(text_color=t["text_primary"])
            dw["bar"].configure(fg_color=t["progress_track"], progress_color=t["temp_bar_fill"])

    # --------------------------------------------------------------------------
    # ERROR BANNER HELPERS
    # --------------------------------------------------------------------------
    def show_banner(self, title: str, message: str, category: str = "error"):
        palette = {
            "error": ("#FEE2E2", "#EF4444", "#991B1B") if self.is_daytime else ("#3B1822", "#EF4444", "#FCA5A5"),
            "warning": ("#FEF3C7", "#F59E0B", "#92400E") if self.is_daytime else ("#382B14", "#F59E0B", "#FDE68A"),
            "info": ("#E0F2FE", "#0284C7", "#075985") if self.is_daytime else ("#132C44", "#38BDF8", "#BAE6FD"),
        }
        bg, border, fg = palette.get(category, palette["error"])
        self.banner_frame.configure(fg_color=bg, border_color=border)
        self.banner_label.configure(text=f"⚠️ {title}: {message}", text_color=fg)
        self.banner_close_btn.configure(fg_color=border, text_color="#FFFFFF")
        self.banner_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 4))

    def hide_banner(self):
        self.banner_frame.grid_forget()

    # --------------------------------------------------------------------------
    # USER ACTIONS & EVENT HANDLERS
    # --------------------------------------------------------------------------
    def on_search(self):
        city = self.city_entry.get().strip()
        if not city:
            self.show_banner("Missing City Name", "Please enter a valid city name to search.", "warning")
            return
        self.fetch_weather(city)

    def on_refresh(self):
        city = self.city_entry.get().strip() or self.current_city_query or DEFAULT_CITY
        self.fetch_weather(city)

    def select_quick_city(self, city_name: str):
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city_name)
        self.fetch_weather(city_name)

    def on_unit_change(self, selected_value: str):
        self.unit = "F" if "F" in selected_value else "C"
        if self.current_data:
            self._render_all_weather()

    def on_toggle_mock_mode(self):
        self.mock_mode = bool(self.mock_switch.get())
        mode_name = "MOCK_MODE (Local JSON)" if self.mock_mode else "LIVE API MODE"
        self.status_label.configure(text=f"Switched to {mode_name}")
        self.on_refresh()

    def on_toggle_day_night_preview(self):
        """Toggles Day/Night theme so the user can preview both palettes anytime."""
        new_state = not self.is_daytime
        if self.current_data and isinstance(self.current_data, list) and len(self.current_data) > 0:
            self.current_data[0]["IsDayTime"] = new_state
        self._apply_theme(new_state)
        if self.current_data:
            self._render_all_weather()

    def on_open_api_key_dialog(self):
        dialog = ctk.CTkInputDialog(
            text=(
                "Enter your AccuWeather API Key below.\n"
                "(You can also set API_KEY at the top of accuweather_gui.py):"
            ),
            title="AccuWeather API Key Configuration",
        )
        entered = dialog.get_input()
        if entered is not None and entered.strip():
            self.api_key = entered.strip()
            self.mock_mode = False
            self.mock_switch.deselect()
            self.show_banner(
                "API Key Updated",
                "Switched to Live API Mode using your newly entered AccuWeather API key.",
                "info",
            )
            self.on_refresh()

    # --------------------------------------------------------------------------
    # DATA FETCHING (THREADED FOR RESPONSIVE UI)
    # --------------------------------------------------------------------------
    def fetch_weather(self, city_query: str):
        if self.is_fetching:
            return
        self.is_fetching = True
        self.current_city_query = city_query
        self.hide_banner()

        source_tag = "Mock JSON" if self.mock_mode else "AccuWeather API"
        self.status_label.configure(text=f"⏳ Fetching '{city_query}' from {source_tag}...")
        self.search_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")

        worker = threading.Thread(
            target=self._fetch_weather_worker,
            args=(city_query, self.mock_mode, self.api_key),
            daemon=True,
        )
        worker.start()

    def _safe_ui_dispatch(self, callback):
        """Safely schedules a UI callback on the Tkinter main loop if the window still exists."""
        try:
            if self.winfo_exists():
                self.after(0, callback)
        except (RuntimeError, tk.TclError):
            pass

    def _fetch_weather_worker(self, city_query: str, use_mock: bool, api_key: str):
        try:
            if use_mock:
                loc, cur, hourly, daily = self._load_mock_weather(city_query)
            else:
                loc, cur, hourly, daily = self._load_live_weather(city_query, api_key)
            self._safe_ui_dispatch(lambda: self._on_fetch_success(loc, cur, hourly, daily, use_mock))
        except WeatherServiceError as wse:
            self._safe_ui_dispatch(lambda: self._on_fetch_error(wse))
        except Exception as exc:
            err = WeatherServiceError(
                "Unexpected Error",
                f"An unexpected error occurred while loading weather data: {exc}",
                "error",
            )
            self._safe_ui_dispatch(lambda: self._on_fetch_error(err))

    def _load_mock_weather(self, city_query: str):
        """
        Loads sample weather data from `mock_data/*.json` files and adapts values
        for searched cities (while validating obviously invalid city strings).
        """
        cleaned = city_query.strip()
        if not cleaned or any(ch.isdigit() for ch in cleaned) or cleaned.lower() in {"invalid", "unknown", "none", "xyz", "asdf"}:
            raise WeatherServiceError(
                "City Not Found",
                f"Could not find any location matching '{city_query}'. Please check the city spelling and try again.",
                "warning",
            )

        ensure_mock_files_exist()
        loc_path = os.path.join(MOCK_DATA_DIR, "location.json")
        cur_path = os.path.join(MOCK_DATA_DIR, "current_conditions.json")
        hr_path = os.path.join(MOCK_DATA_DIR, "hourly_12hour.json")
        day_path = os.path.join(MOCK_DATA_DIR, "daily_5day.json")

        with open(loc_path, "r", encoding="utf-8") as f:
            loc_list = json.load(f)
        with open(cur_path, "r", encoding="utf-8") as f:
            cur_list = json.load(f)
        with open(hr_path, "r", encoding="utf-8") as f:
            hourly_list = json.load(f)
        with open(day_path, "r", encoding="utf-8") as f:
            daily_dict = json.load(f)

        loc = loc_list[0] if loc_list else {}
        cur = cur_list[0] if cur_list else {}

        # Apply preset city customization if available, or update city title
        preset = MOCK_CITY_PRESETS.get(cleaned.lower())
        if preset:
            loc["Key"] = preset["Key"]
            loc["EnglishName"] = preset["EnglishName"]
            loc["AdministrativeArea"] = {"EnglishName": preset["AdminArea"]}
            loc["Country"] = {"EnglishName": preset["Country"]}

            cur["IsDayTime"] = preset["IsDayTime"]
            cur["WeatherIcon"] = preset["WeatherIcon"]
            cur["WeatherText"] = preset["WeatherText"]
            cur["Temperature"]["Metric"]["Value"] = preset["TempC"]
            cur["Temperature"]["Imperial"]["Value"] = round(preset["TempC"] * 9.0 / 5.0 + 32.0, 1)
            cur["RealFeelTemperature"]["Metric"]["Value"] = preset["RealFeelC"]
            cur["RealFeelTemperature"]["Metric"]["Phrase"] = preset["RealFeelPhrase"]
            cur["RealFeelTemperature"]["Imperial"]["Value"] = round(preset["RealFeelC"] * 9.0 / 5.0 + 32.0, 1)
            cur["RealFeelTemperature"]["Imperial"]["Phrase"] = preset["RealFeelPhrase"]
            cur["RelativeHumidity"] = preset["Humidity"]
            cur["UVIndex"] = preset["UVIndex"]
            cur["UVIndexText"] = preset["UVIndexText"]
            cur["Wind"]["Speed"]["Metric"]["Value"] = preset["WindKmh"]
            cur["Wind"]["Speed"]["Imperial"]["Value"] = round(preset["WindKmh"] / 1.60934, 1)
            cur["Wind"]["Direction"]["Localized"] = preset["WindDir"]
            cur["Wind"]["Direction"]["English"] = preset["WindDir"]
            cur["PrecipitationProbability"] = preset["PrecipProb"]

            # Shift hourly & daily temperatures proportionally to match preset city
            delta_c = preset["TempC"] - 32.4
            for idx, hr in enumerate(hourly_list[:12]):
                base_val = float(hr.get("Temperature", {}).get("Value", 30.0))
                hr["Temperature"]["Value"] = round(base_val + delta_c, 1)
                hr["Temperature"]["Unit"] = "C"
                if idx == 0:
                    hr["WeatherIcon"] = preset["WeatherIcon"]
                    hr["IconPhrase"] = preset["WeatherText"]
                    hr["PrecipitationProbability"] = preset["PrecipProb"]

            for idx, d in enumerate(daily_dict.get("DailyForecasts", [])[:5]):
                min_v = float(d["Temperature"]["Minimum"]["Value"])
                max_v = float(d["Temperature"]["Maximum"]["Value"])
                d["Temperature"]["Minimum"]["Value"] = round(min_v + delta_c, 1)
                d["Temperature"]["Maximum"]["Value"] = round(max_v + delta_c, 1)
                if idx == 0:
                    d["Day"]["PrecipitationProbability"] = preset["PrecipProb"]
        else:
            # Custom city name searched in mock mode
            loc["EnglishName"] = cleaned.title()
            loc["AdministrativeArea"] = {"EnglishName": cleaned.title()}

        return loc, [cur], hourly_list[:12], daily_dict

    def _http_get_json(self, url: str):
        """Performs an HTTP GET request to AccuWeather API with structured error handling."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "AccuWeatherPulseGUI/2.0 (Python CustomTkinter)",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise WeatherServiceError(
                    f"Unauthorized API Key (HTTP {e.code})",
                    "Your AccuWeather API Key was rejected. Please set a valid API_KEY at the top of "
                    "accuweather_gui.py (or click '🔑 API Key'), or enable 'Mock JSON' mode for UI testing.",
                    "error",
                )
            elif e.code in (429, 503):
                raise WeatherServiceError(
                    f"API Quota Limit Exceeded (HTTP {e.code})",
                    "Your AccuWeather Free Tier quota (50 calls/day) has been reached. "
                    "Enable 'Mock JSON' mode in the top right to continue testing with local JSON data.",
                    "warning",
                )
            elif e.code == 400:
                raise WeatherServiceError(
                    "Bad Request (HTTP 400)",
                    "The search query or request parameters were invalid. Please verify the city name.",
                    "warning",
                )
            else:
                raise WeatherServiceError(
                    f"AccuWeather HTTP Error {e.code}",
                    f"Server returned HTTP {e.code} ({e.reason}). Please try again later.",
                    "error",
                )
        except (urllib.error.URLError, socket.timeout, TimeoutError) as e:
            reason = getattr(e, "reason", str(e))
            raise WeatherServiceError(
                "Network Timeout / Connection Error",
                f"Unable to reach dataservice.accuweather.com ({reason}). "
                "Please check your internet connection or toggle 'Mock JSON' mode.",
                "error",
            )
        except json.JSONDecodeError:
            raise WeatherServiceError(
                "Invalid API Response",
                "Received malformed JSON data from the AccuWeather server.",
                "error",
            )

    def _load_live_weather(self, city_query: str, api_key: str):
        """Fetches Location Key, Current Conditions (details=true), 12-Hour Forecast, and 5-Day Forecast."""
        if not api_key or api_key == "YOUR_ACCUWEATHER_API_KEY_HERE":
            raise WeatherServiceError(
                "API Key Not Configured",
                "Please replace API_KEY at the top of accuweather_gui.py (or click '🔑 API Key'), "
                "or turn ON 'Mock JSON' mode to test with local sample data.",
                "warning",
            )

        encoded_city = urllib.parse.quote(city_query.strip())

        # 1. Location Search API
        loc_url = (
            f"http://dataservice.accuweather.com/locations/v1/cities/search"
            f"?apikey={urllib.parse.quote(api_key)}&q={encoded_city}"
        )
        location_list = self._http_get_json(loc_url)
        if not location_list or not isinstance(location_list, list):
            raise WeatherServiceError(
                "City Not Found",
                f"No matching city found for '{city_query}'. Please check the spelling and try again.",
                "warning",
            )

        loc = location_list[0]
        location_key = loc["Key"]

        # 2. Current Conditions API (with details=true for RealFeel, UV, Humidity, Wind)
        cur_url = (
            f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
            f"?apikey={urllib.parse.quote(api_key)}&details=true"
        )
        current_list = self._http_get_json(cur_url)
        if not current_list:
            raise WeatherServiceError(
                "No Weather Data",
                f"Current weather conditions are unavailable for '{city_query}'.",
                "warning",
            )

        # 3. 12-Hour Hourly Forecast API (with details=true & metric=true)
        hourly_url = (
            f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}"
            f"?apikey={urllib.parse.quote(api_key)}&details=true&metric=true"
        )
        hourly_list = self._http_get_json(hourly_url)

        # 4. 5-Day Daily Forecast API (with details=true & metric=true)
        daily_url = (
            f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
            f"?apikey={urllib.parse.quote(api_key)}&details=true&metric=true"
        )
        daily_dict = self._http_get_json(daily_url)

        return loc, current_list, hourly_list or [], daily_dict or {}

    def _on_fetch_success(self, loc, cur, hourly, daily, used_mock: bool):
        self.is_fetching = False
        self.search_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")

        self.location_info = loc
        self.current_data = cur
        self.hourly_data = hourly
        self.daily_data = daily

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_updated_str = now_str
        src_badge = "Mock JSON" if used_mock else "Live API"
        self.timestamp_label.configure(text=f"🕒 Last updated: {now_str} ({src_badge})")
        self.status_label.configure(
            text=f"Loaded {loc.get('EnglishName', self.current_city_query)} [{src_badge}]"
        )

        # Determine Day/Night mode from API's IsDayTime boolean
        condition = cur[0] if cur else {}
        is_day = bool(condition.get("IsDayTime", True))
        self._apply_theme(is_day)
        self._render_all_weather()

    def _on_fetch_error(self, err: WeatherServiceError):
        self.is_fetching = False
        self.search_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text=f"⚠️ {err.title}")
        self.show_banner(err.title, err.message, err.category)

    # --------------------------------------------------------------------------
    # UI RENDERING
    # --------------------------------------------------------------------------
    def _render_all_weather(self):
        if not self.current_data:
            return

        loc = self.location_info or {}
        condition = self.current_data[0]
        hourly = self.hourly_data or []
        daily_forecasts = (self.daily_data or {}).get("DailyForecasts", [])
        headline = (self.daily_data or {}).get("Headline", {}).get("Text", "")

        # 1. Hero Section
        city_name = loc.get("EnglishName") or loc.get("LocalizedName") or self.current_city_query
        admin_name = (loc.get("AdministrativeArea") or {}).get("EnglishName", "")
        country_name = (loc.get("Country") or {}).get("EnglishName", "Thailand")
        region_parts = [p for p in [admin_name, country_name] if p]

        self.hero_city_label.configure(text=city_name)
        self.hero_region_label.configure(
            text=f"📍 {', '.join(region_parts)}  •  Key #{loc.get('Key', '--')}"
        )

        icon_code = int(condition.get("WeatherIcon", 1))
        weather_text = condition.get("WeatherText") or ACCUWEATHER_ICON_MAP.get(icon_code, ("☀️", "Clear"))[1]
        self._configure_icon_label(self.hero_icon_label, icon_code, img_size=84, emoji_font_size=64)

        temp_c = self.extract_temp_c(condition.get("Temperature", {}))
        realfeel_obj = condition.get("RealFeelTemperature", {})
        realfeel_c = self.extract_temp_c(realfeel_obj)
        realfeel_phrase = ""
        if isinstance(realfeel_obj.get("Metric"), dict):
            realfeel_phrase = realfeel_obj["Metric"].get("Phrase", "")
        if not realfeel_phrase:
            realfeel_phrase = realfeel_obj.get("Phrase", "Comfortable")

        self.hero_temp_label.configure(text=self.format_temp_from_c(temp_c))
        self.hero_condition_label.configure(text=f"{weather_text}  (Icon #{icon_code})")

        if daily_forecasts:
            d0_temp = daily_forecasts[0].get("Temperature", {})
            d0_min_c = self.extract_temp_c(d0_temp.get("Minimum", {}))
            d0_max_c = self.extract_temp_c(d0_temp.get("Maximum", {}))
            hi_lo_str = (
                f"High {self.format_temp_from_c(d0_max_c)} / Low {self.format_temp_from_c(d0_min_c)}"
            )
        else:
            hi_lo_str = "High -- / Low --"

        self.hero_hi_lo_label.configure(
            text=f"RealFeel® {self.format_temp_from_c(realfeel_c)}  •  {hi_lo_str}"
        )
        self.hero_headline_label.configure(
            text=f"💬 {headline}" if headline else "💬 AccuWeather Current & Forecast Conditions"
        )

        # 2. Current Weather 6-Metric Grid
        # (a) Actual Temperature
        self.metric_cards["actual_temp"]["value"].configure(text=self.format_temp_from_c(temp_c))
        self.metric_cards["actual_temp"]["sub"].configure(text=hi_lo_str)

        # (b) RealFeel Temperature
        self.metric_cards["realfeel"]["value"].configure(text=self.format_temp_from_c(realfeel_c))
        self.metric_cards["realfeel"]["sub"].configure(
            text=f"Feels like: {realfeel_phrase or 'Standard'}"
        )

        # (c) UV Index (with risk level text)
        uv_val = condition.get("UVIndex", 0)
        uv_api_text = condition.get("UVIndexText", "")
        uv_label, uv_color, uv_prog = self.get_uv_risk_info(uv_val, uv_api_text)
        self.metric_cards["uv_index"]["value"].configure(text=f"{uv_val} ({uv_label})")
        self.metric_cards["uv_index"]["bar"].configure(
            fg_color=self.theme["progress_track"],
            progress_color=uv_color,
        )
        self.metric_cards["uv_index"]["bar"].set(uv_prog)
        uv_advice = (
            "Minimal sun risk" if int(uv_val or 0) <= 2
            else "Wear sunglasses & SPF 30+" if int(uv_val or 0) <= 5
            else "High UV — seek shade midday"
        )
        self.metric_cards["uv_index"]["sub"].configure(text=f"Risk Level: {uv_label} • {uv_advice}")

        # (d) Humidity (%)
        humidity = int(condition.get("RelativeHumidity") or 0)
        dew_c = self.extract_temp_c(condition.get("DewPoint", {"Metric": {"Value": temp_c - (100 - humidity) / 5.0}}))
        self.metric_cards["humidity"]["value"].configure(text=f"{humidity}%")
        self.metric_cards["humidity"]["bar"].set(min(max(humidity / 100.0, 0.04), 1.0))
        self.metric_cards["humidity"]["sub"].configure(
            text=f"Dew Point: {self.format_temp_from_c(dew_c)}"
        )

        # (e) Wind Speed & Direction
        wind_obj = condition.get("Wind", {})
        dir_obj = wind_obj.get("Direction", {})
        wind_dir = dir_obj.get("Localized") or dir_obj.get("English") or "N"
        wind_deg = dir_obj.get("Degrees", 0)
        wind_speed_str = self.format_wind_speed(wind_obj)
        gust_obj = condition.get("WindGust", {})
        gust_str = self.format_wind_speed(gust_obj) if gust_obj else "--"
        self.metric_cards["wind"]["value"].configure(text=f"{wind_speed_str} {wind_dir}")
        self.metric_cards["wind"]["sub"].configure(
            text=f"Bearing: {wind_deg}° ({wind_dir}) • Gust: {gust_str}"
        )

        # (f) Precipitation Probability (%)
        precip_prob = condition.get("PrecipitationProbability")
        if precip_prob is None:
            if hourly and "PrecipitationProbability" in hourly[0]:
                precip_prob = hourly[0].get("PrecipitationProbability", 0)
            elif daily_forecasts:
                precip_prob = (daily_forecasts[0].get("Day") or {}).get("PrecipitationProbability", 0)
            else:
                precip_prob = 0
        precip_prob = int(precip_prob or 0)
        has_precip = bool(condition.get("HasPrecipitation", False))
        precip_type = condition.get("PrecipitationType") or ("Rain" if has_precip else "None")

        self.metric_cards["precip"]["value"].configure(text=f"{precip_prob}%")
        self.metric_cards["precip"]["bar"].set(min(max(precip_prob / 100.0, 0.04), 1.0))
        self.metric_cards["precip"]["sub"].configure(
            text=f"Active Precip: {'Yes (' + str(precip_type) + ')' if has_precip else 'No'}"
        )

        # 3. Render 12-Hour Hourly Forecast
        self._render_hourly_forecast(hourly)

        # 4. Render 5-Day Daily Forecast
        self._render_daily_forecast(daily_forecasts)

    def _render_hourly_forecast(self, hourly_list: list):
        for w in self.hourly_item_widgets:
            w["card"].destroy()
        self.hourly_item_widgets.clear()

        t = self.theme
        items = hourly_list[:12]

        for idx, hr in enumerate(items):
            is_first = idx == 0
            dt_str = hr.get("DateTime", "")
            try:
                dt = datetime.fromisoformat(dt_str)
                time_label = "Now" if is_first else dt.strftime("%H:%M")
            except Exception:
                time_label = "Now" if is_first else f"+{idx}h"

            icon_code = int(hr.get("WeatherIcon", 1))
            hr_temp_c = self.extract_temp_c(hr.get("Temperature", {}))
            rain_prob = int(hr.get("PrecipitationProbability", 0))

            card = ctk.CTkFrame(
                self.hourly_scroll,
                width=94,
                height=136,
                corner_radius=14,
                border_width=2 if is_first else 1,
                fg_color=t["accent_soft"] if is_first else t["card_alt_bg"],
                border_color=t["accent"] if is_first else t["card_border"],
            )
            card.pack(side="left", padx=5, pady=4)
            card.pack_propagate(False)

            lbl_time = ctk.CTkLabel(
                card,
                text=time_label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=t["accent"] if is_first else t["text_secondary"],
            )
            lbl_time.pack(pady=(10, 2))

            lbl_icon = ctk.CTkLabel(card, text="")
            self._configure_icon_label(lbl_icon, icon_code, img_size=34, emoji_font_size=26)
            lbl_icon.pack(pady=2)

            lbl_temp = ctk.CTkLabel(
                card,
                text=self.format_temp_from_c(hr_temp_c, include_unit=False, decimals=0),
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=t["text_primary"],
            )
            lbl_temp.pack(pady=(2, 2))

            lbl_rain = ctk.CTkLabel(
                card,
                text=f"💧 {rain_prob}%",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=t["rain_text"],
            )
            lbl_rain.pack(pady=(0, 8))

            self.hourly_item_widgets.append({
                "card": card,
                "time": lbl_time,
                "icon": lbl_icon,
                "temp": lbl_temp,
                "rain": lbl_rain,
                "is_first": is_first,
            })

    def _render_daily_forecast(self, daily_list: list):
        for w in self.daily_row_widgets:
            w["row"].destroy()
        self.daily_row_widgets.clear()

        t = self.theme
        days = daily_list[:5]
        if not days:
            return

        # Compute overall 5-day temperature span for visual bar scaling
        all_mins = [self.extract_temp_c(d.get("Temperature", {}).get("Minimum", {})) for d in days]
        all_maxs = [self.extract_temp_c(d.get("Temperature", {}).get("Maximum", {})) for d in days]
        week_min = min(all_mins) if all_mins else 20.0
        week_max = max(all_maxs) if all_maxs else 35.0
        week_span = max(week_max - week_min, 1.0)

        for idx, day_item in enumerate(days):
            date_str = day_item.get("Date", "")
            try:
                dt = datetime.fromisoformat(date_str)
                day_title = f"Today ({dt.strftime('%a, %b %d')})" if idx == 0 else dt.strftime("%A, %b %d")
            except Exception:
                day_title = "Today" if idx == 0 else f"Day +{idx}"

            day_part = day_item.get("Day") or {}
            night_part = day_item.get("Night") or {}
            active_part = day_part if self.is_daytime or not night_part else day_part
            icon_code = int(active_part.get("Icon", 1))
            phrase = active_part.get("IconPhrase") or ACCUWEATHER_ICON_MAP.get(icon_code, ("☀️", "Clear"))[1]
            rain_prob = int(day_part.get("PrecipitationProbability", 0))

            t_min_c = self.extract_temp_c(day_item.get("Temperature", {}).get("Minimum", {}))
            t_max_c = self.extract_temp_c(day_item.get("Temperature", {}).get("Maximum", {}))

            row = ctk.CTkFrame(
                self.daily_rows_container,
                corner_radius=12,
                border_width=1,
                fg_color=t["card_alt_bg"],
                border_color=t["card_border"],
                height=54,
            )
            row.grid(row=idx, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=4)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=4)

            # Column 0: Day Name
            lbl_day = ctk.CTkLabel(
                row,
                text=day_title,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=t["text_primary"],
                anchor="w",
            )
            lbl_day.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=10)

            # Column 1: Icon + Weather Phrase
            cond_box = ctk.CTkFrame(row, fg_color="transparent")
            cond_box.grid(row=0, column=1, sticky="w", padx=6, pady=6)

            lbl_icon = ctk.CTkLabel(cond_box, text="")
            self._configure_icon_label(lbl_icon, icon_code, img_size=30, emoji_font_size=22)
            lbl_icon.pack(side="left", padx=(0, 10))

            lbl_phrase = ctk.CTkLabel(
                cond_box,
                text=f"{phrase} (#{icon_code})",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=t["text_secondary"],
                anchor="w",
            )
            lbl_phrase.pack(side="left")

            # Column 2: Rain Probability
            lbl_rain = ctk.CTkLabel(
                row,
                text=f"💧 {rain_prob}%",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=t["rain_text"],
            )
            lbl_rain.grid(row=0, column=2, padx=8, pady=10)

            # Column 3: Min / Max Temperatures + Visual Range Bar
            temp_box = ctk.CTkFrame(row, fg_color="transparent")
            temp_box.grid(row=0, column=3, sticky="e", padx=(8, 16), pady=8)

            lbl_min = ctk.CTkLabel(
                temp_box,
                text=f"Min {self.format_temp_from_c(t_min_c, decimals=1)}",
                width=78,
                anchor="e",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=t["text_secondary"],
            )
            lbl_min.pack(side="left", padx=(0, 8))

            bar = ctk.CTkProgressBar(
                temp_box,
                width=100,
                height=8,
                corner_radius=4,
                fg_color=t["progress_track"],
                progress_color=t["temp_bar_fill"],
            )
            rel_progress = min(max((t_max_c - week_min) / week_span, 0.15), 1.0)
            bar.set(rel_progress)
            bar.pack(side="left", padx=4)

            lbl_max = ctk.CTkLabel(
                temp_box,
                text=f"Max {self.format_temp_from_c(t_max_c, decimals=1)}",
                width=82,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=t["text_primary"],
            )
            lbl_max.pack(side="left", padx=(8, 0))

            self.daily_row_widgets.append({
                "row": row,
                "day": lbl_day,
                "icon": lbl_icon,
                "phrase": lbl_phrase,
                "rain": lbl_rain,
                "min": lbl_min,
                "max": lbl_max,
                "bar": bar,
            })


if __name__ == "__main__":
    app = AccuWeatherApp()
    app.mainloop()
