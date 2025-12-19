from fastapi import FastAPI, HTTPException
import requests


#GETTING JSON from ML model

EXTERNAL_API_URL = "https://smart-home-agent.onrender.com/state"

def fetch_decision():
        response = requests.get(EXTERNAL_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()