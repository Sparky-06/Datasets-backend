# from fastapi import FastAPI, HTTPException
# import httpx
# import requests
# from api.ml.ml import fetch_decision

# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI(title="Smart Home Backend")


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://datasets-frontend-teal.vercel.app",
#         "http://localhost:5173",  # for local dev
#     ],
#     allow_credentials=True,
#     allow_origin =["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# SMART_HOME_STATE_URL = "https://smart-home-agent.onrender.com/state"


# @app.get("/")
# async def health_check():
#     return {"status": "ok"}


# @app.get("/state")
# async def state():
#     data = fetch_decision()
#     return data


# @app.get("/energy-usage")
# async def get_energy_usage():
#     try:
#         async with httpx.AsyncClient(timeout=10) as client:
#             response = await client.get(SMART_HOME_STATE_URL)
#             response.raise_for_status()
#             data = response.json()
#     except httpx.RequestError:
#         raise HTTPException(status_code=503, detail="Smart home service unreachable")
#     except httpx.HTTPStatusError:
#         raise HTTPException(status_code=502, detail="Invalid response from smart home service")

#     energy_by_type = {}
#     total_energy = 0.0

#     for device in data.values():
#         device_type = device.get("device_type", "unknown")
#         energy = device.get("cumulative_energy", 0.0) * 1000  # assuming kWh → Wh

#         energy_by_type[device_type] = energy_by_type.get(device_type, 0.0) + energy
#         total_energy += energy

#     return {
#         "energy_by_type": energy_by_type,
#         "total_energy": total_energy
#     }


# @app.get("/switch-states")
# async def get_switch_states():
#     data = fetch_decision()
#     switch_by_type = {}

#     for device in data.values():
#         device_type = device.get("device_type", "unknown")
#         power_state = device.get("power", 0)

#         switch_by_type[device_type] = power_state

#     return switch_by_type


# @app.get("/automation")
# async def get_automation_decisions():
#     response = requests.get("https://smart-home-agent.onrender.com/automation-events", timeout=10)
#     return response.json()


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from datetime import datetime
import httpx
import random

app = FastAPI(title="Smart Home Backend")

# ──────────────────────────────────────
# CORS
# ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SMART_HOME_STATE_URL = "https://smart-home-agent.onrender.com/state"

# ──────────────────────────────────────
# Helpers
# ──────────────────────────────────────
async def fetch_state() -> Dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(SMART_HOME_STATE_URL)
        response.raise_for_status()
        return response.json()


def map_device(raw: Dict) -> Dict:
    device_type = raw.get("device_type", "").lower()

    device = {
        "id": raw["device_id"],
        "name": raw["device_id"].replace("_", " ").title(),
        "type": device_type,
        "status": "on" if raw.get("power") == "ON" else "off",
        "location": raw.get("room", "unknown").replace("_", " ").title(),
        "powerUsage": raw.get("current_watts", 0),
    }

    if device_type == "light":
        device["brightness"] = 80 if device["status"] == "on" else 0
    elif device_type == "fan":
        device["speed"] = raw.get("speed", 1)
    elif device_type == "ac":
        device["temperature"] = raw.get("set_temperature", 24)

    return device


def map_sensors(raw: Dict) -> List[Dict]:
    sensors = []

    if "ambient_temperature" in raw:
        sensors.append({
            "id": f"{raw['device_id']}_temp",
            "type": "temperature",
            "location": raw.get("room", "unknown").title(),
            "value": raw["ambient_temperature"],
            "unit": "°C",
            "lastUpdated": raw["timestamp"],
            "status": "warning" if raw["ambient_temperature"] > 26 else "normal",
        })

    sensors.append({
        "id": f"{raw['device_id']}_occupancy",
        "type": "occupancy",
        "location": raw.get("room", "unknown").title(),
        "value": 1 if raw.get("occupancy") else 0,
        "unit": "person",
        "lastUpdated": raw["timestamp"],
        "status": "normal",
    })

    return sensors


# ──────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────

@app.get("/api/devices")
async def get_devices():
    state = await fetch_state()
    return [map_device(device) for device in state.values()]


@app.post("/api/devices/{device_id}/toggle")
async def toggle_device(device_id: str):
    # This API is read-only, so we fake the toggle for frontend continuity
    state = await fetch_state()
    device = next((d for d in state.values() if d["device_id"] == device_id), None)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    mapped = map_device(device)
    mapped["status"] = "off" if mapped["status"] == "on" else "on"
    mapped["powerUsage"] = 0 if mapped["status"] == "off" else mapped["powerUsage"]

    return mapped


@app.patch("/api/devices/{device_id}")
async def update_device(device_id: str, updates: Dict):
    state = await fetch_state()
    device = next((d for d in state.values() if d["device_id"] == device_id), None)

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    mapped = map_device(device)
    mapped.update(updates)
    return mapped


@app.get("/api/sensors")
async def get_sensors():
    state = await fetch_state()
    sensors: List[Dict] = []

    for device in state.values():
        sensors.extend(map_sensors(device))

    return sensors


@app.get("/api/energy")
async def get_energy():
    now = datetime.utcnow()
    data = []

    for i in range(24):
        consumption = random.uniform(1.0, 4.0)
        forecast = consumption + random.uniform(-0.5, 0.5) if i > 18 else None

        data.append({
            "timestamp": now.isoformat(),
            "consumption": consumption,
            "forecast": forecast,
        })

    return data


@app.get("/api/automation/rules")
async def get_automation_rules():
    return [
        {
            "id": "r1",
            "name": "Night Mode",
            "enabled": True,
            "trigger": {"type": "time", "condition": "After 10:00 PM"},
            "action": {"deviceId": "light_1", "command": "Turn off all lights"},
            "mode": "rule-based",
        },
        {
            "id": "r2",
            "name": "Climate Control",
            "enabled": True,
            "trigger": {"type": "sensor", "condition": "Temperature > 26°C"},
            "action": {"deviceId": "ac_1", "command": "Turn on AC"},
            "mode": "ml-assisted",
        },
    ]


@app.post("/api/automation/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str):
    return {"id": rule_id, "enabled": True}


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    state = await fetch_state()

    devices = [map_device(d) for d in state.values()]
    active = len([d for d in devices if d["status"] == "on"])
    total_energy = sum(d["powerUsage"] for d in devices) / 1000

    return {
        "totalDevices": len(devices),
        "activeDevices": active,
        "totalEnergy": total_energy,
        "estimatedCost": total_energy * 0.12,
    }
