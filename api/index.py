from fastapi import FastAPI, HTTPException
import httpx
import requests
from api.ml.ml import fetch_decision

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Smart Home Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://datasets-frontend-teal.vercel.app",
        "http://localhost:5173",  # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



SMART_HOME_STATE_URL = "https://smart-home-agent.onrender.com/state"


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/state")
async def state():
    data = fetch_decision()
    return data


@app.get("/energy-usage")
async def get_energy_usage():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(SMART_HOME_STATE_URL)
            response.raise_for_status()
            data = response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Smart home service unreachable")
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Invalid response from smart home service")

    energy_by_type = {}
    total_energy = 0.0

    for device in data.values():
        device_type = device.get("device_type", "unknown")
        energy = device.get("cumulative_energy", 0.0) * 1000  # assuming kWh → Wh

        energy_by_type[device_type] = energy_by_type.get(device_type, 0.0) + energy
        total_energy += energy

    return {
        "energy_by_type": energy_by_type,
        "total_energy": total_energy
    }


@app.get("/switch-states")
async def get_switch_states():
    data = fetch_decision()
    switch_by_type = {}

    for device in data.values():
        device_type = device.get("device_type", "unknown")
        power_state = device.get("power", 0)

        switch_by_type[device_type] = power_state

    return switch_by_type


@app.get("/automation")
async def get_automation_decisions():
    response = requests.get("https://smart-home-agent.onrender.com/automation-events", timeout=10)
    return response.json()

