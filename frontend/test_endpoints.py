# Optional: Test script to verify your endpoints
import requests
import json

BASE_URL = "http://localhost:8080"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_leaderboard():
    response = requests.get(f"{BASE_URL}/v1/leaderboard")
    print("Leaderboard:", response.json())

def test_add_manual_entry():
    entry = {
        "username": "Test User",
        "score": 95.5,
        "job_title": "Software Engineer"
    }
    response = requests.post(f"{BASE_URL}/v1/leaderboard", json=entry)
    print("Manual Entry:", response.json())

def test_stats():
    response = requests.get(f"{BASE_URL}/leaderboard/stats")
    print("Stats:", response.json())

if __name__ == "__main__":
    test_health()
    test_add_manual_entry()
    test_leaderboard()
    test_stats()
