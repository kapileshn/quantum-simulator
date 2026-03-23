"""
Unit Tests: API Endpoints
=========================
Tests for the FastAPI REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.simulation_api import app, ALGORITHMS
from simulation_engine.gates import GATE_REGISTRY

client = TestClient(app)

def test_root():
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_list_gates():
    """Test gate listing endpoint."""
    response = client.get("/api/gates")
    assert response.status_code == 200
    data = response.json()
    assert "gates" in data
    assert len(data["gates"]) == len(GATE_REGISTRY)
    
    # Check if a known gate is present
    gate_names = [g["name"] for g in data["gates"]]
    assert "H" in gate_names
    assert "CNOT" in gate_names

def test_list_algorithms():
    """Test algorithm listing endpoint."""
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    data = response.json()
    assert "algorithms" in data
    assert len(data["algorithms"]) == len(ALGORITHMS)
    
    # Check expected algorithms
    algo_names = [a["name"] for a in data["algorithms"]]
    assert "deutsch_jozsa" in algo_names
    assert "grover" in algo_names
    assert "teleportation" in algo_names
    assert "bb84" in algo_names
    assert "qrng" in algo_names

def test_simulate_valid_circuit():
    """Test circuit simulation with valid input."""
    request_data = {
        "n_qubits": 2,
        "operations": [
            {"gate": "H", "targets": [0]},
            {"gate": "CNOT", "targets": [0, 1]}
        ],
        "measure_all": True
    }
    
    response = client.post("/api/simulate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["n_qubits"] == 2
    assert "final_state" in data
    assert "state_history" in data
    assert len(data["state_history"]) == 3  # Initial + H + CNOT
    assert "measurement" in data

def test_simulate_invalid_gate():
    """Test circuit simulation with invalid gate placement."""
    request_data = {
        "n_qubits": 2,
        "operations": [
            {"gate": "H", "targets": [5]}  # Target out of bounds
        ]
    }
    
    response = client.post("/api/simulate", json=request_data)
    assert response.status_code == 400
    assert "out of bounds" in response.json()["detail"]

def test_run_algorithm_valid():
    """Test running a valid algorithm."""
    request_data = {
        "name": "deutsch_jozsa",
        "params": {
            "n_input": 2,
            "oracle_type": "balanced"
        }
    }
    
    response = client.post("/api/algorithms/deutsch_jozsa/run", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["algorithm"] == "deutsch_jozsa"
    assert "result" in data
    assert data["result"]["result"] == "balanced"

def test_run_algorithm_not_found():
    """Test running a non-existent algorithm."""
    request_data = {
        "name": "fake_algorithm",
        "params": {}
    }
    
    response = client.post("/api/algorithms/fake_algorithm/run", json=request_data)
    assert response.status_code == 404
