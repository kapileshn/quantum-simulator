"""
Quantum Simulator API
=====================
FastAPI backend with Socket.IO for real-time quantum simulation.

Endpoints:
    REST:
        POST /api/simulate        — Run a circuit
        GET  /api/algorithms      — List available algorithms
        POST /api/algorithms/{name}/run — Run a named algorithm
    
    Socket.IO:
        simulate:step — Step-by-step execution with real-time state push
"""

import os
import json
import uuid
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn

# Load environment configuration
load_dotenv()

# Import simulation engine
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation_engine.quantum_state import QuantumState
from simulation_engine.gates import GATE_REGISTRY, validate_gate_placement, get_gate_matrix
from simulation_engine.measurement import measure_qubit, measure_all, get_measurement_statistics
from simulation_engine.algorithms import deutsch_jozsa, grover, teleportation, bb84, qrng, bell_states
from api.models import (
    CircuitRequest, AlgorithmRequest, SimulationResult,
    AlgorithmResult, AlgorithmInfo, ErrorResponse, GateOperation
)


# =============================================================================
# App Setup
# =============================================================================

app = FastAPI(
    title="Quantum Protocol & Algorithm Simulator",
    description="Real-time quantum computing simulation API",
    version="1.0.0",
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO setup
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=cors_origins,
    logger=False,
)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

# Session storage for step-by-step execution
sessions: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# Algorithm Registry
# =============================================================================

ALGORITHMS = {
    'deutsch_jozsa': {
        'display_name': 'Deutsch-Jozsa Algorithm',
        'description': 'Determines if a function is constant or balanced in one query',
        'category': 'algorithm',
        'parameters': [
            {'name': 'n_input', 'type': 'int', 'default': 2, 'min': 1, 'max': 4,
             'description': 'Number of input qubits'},
            {'name': 'oracle_type', 'type': 'select', 'default': 'balanced',
             'options': ['constant_0', 'constant_1', 'balanced'],
             'description': 'Type of oracle function'},
        ],
        'module': deutsch_jozsa,
    },
    'grover': {
        'display_name': "Grover's Search Algorithm",
        'description': 'Searches unsorted database with quadratic speedup',
        'category': 'algorithm',
        'parameters': [
            {'name': 'n_qubits', 'type': 'int', 'default': 3, 'min': 2, 'max': 5,
             'description': 'Number of qubits'},
            {'name': 'target_states', 'type': 'int_list', 'default': [7],
             'description': 'Target state indices to search for'},
        ],
        'module': grover,
    },
    'teleportation': {
        'display_name': 'Quantum Teleportation',
        'description': 'Transfers quantum state using entanglement and classical communication',
        'category': 'protocol',
        'parameters': [
            {'name': 'theta', 'type': 'float', 'default': 1.5708, 'min': 0, 'max': 3.14159,
             'description': 'Bloch sphere polar angle (θ)'},
            {'name': 'phi', 'type': 'float', 'default': 0.0, 'min': 0, 'max': 6.28318,
             'description': 'Bloch sphere azimuthal angle (φ)'},
        ],
        'module': teleportation,
    },
    'bb84': {
        'display_name': 'BB84 Quantum Key Distribution',
        'description': 'Quantum key exchange protocol with eavesdropping detection',
        'category': 'protocol',
        'parameters': [
            {'name': 'n_bits', 'type': 'int', 'default': 16, 'min': 4, 'max': 64,
             'description': 'Number of qubits to exchange'},
            {'name': 'eve_present', 'type': 'bool', 'default': False,
             'description': 'Whether an eavesdropper is present'},
        ],
        'module': bb84,
    },
    'qrng': {
        'display_name': 'Quantum Random Number Generator',
        'description': 'Generates truly random numbers using quantum superposition',
        'category': 'algorithm',
        'parameters': [
            {'name': 'n_bits', 'type': 'int', 'default': 8, 'min': 1, 'max': 64,
             'description': 'Number of random bits to generate'},
        ],
        'module': qrng,
    },
    'bell_states': {
        'display_name': 'The Four Bell States',
        'description': 'Generates one of the four maximally entangled two-qubit Bell states.',
        'category': 'protocol',
        'parameters': [
            {'name': 'state_type', 'type': 'select', 'default': 'Phi+',
             'options': ['Phi+', 'Phi-', 'Psi+', 'Psi-'],
             'description': 'Identify which Bell state to generate'},
        ],
        'module': bell_states,
    },
}


# =============================================================================
# REST Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Quantum Protocol & Algorithm Simulator",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/gates")
async def list_gates():
    """List all available quantum gates with their metadata."""
    gates = []
    for name, info in GATE_REGISTRY.items():
        gates.append({
            'name': name,
            'label': info['label'],
            'description': info['desc'],
            'n_qubits': info['n_qubits'],
            'has_parameter': info['param'] is not None,
            'parameter_name': info['param'],
        })
    return {'gates': gates}


@app.get("/api/algorithms")
async def list_algorithms():
    """List all available algorithms with metadata."""
    algorithms = []
    for name, info in ALGORITHMS.items():
        algorithms.append(AlgorithmInfo(
            name=name,
            display_name=info['display_name'],
            description=info['description'],
            category=info['category'],
            parameters=info['parameters'],
        ))
    return {'algorithms': algorithms}


@app.post("/api/simulate")
async def simulate_circuit(request: CircuitRequest):
    """Run a quantum circuit and return the final state.

    Returns amplitudes, probabilities, Bloch sphere coords,
    and optionally measurement results.
    """
    try:
        state = QuantumState(request.n_qubits)
        state_history = [state.to_dict()]

        for op in request.operations:
            if op.gate == 'M':
                # Measurement gate from frontend — perform measurement
                for t in op.targets:
                    _, state = measure_qubit(state, t)
            else:
                # Validate gate placement
                is_valid, error = validate_gate_placement(
                    op.gate, op.targets, request.n_qubits
                )
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error)

                state.apply_gate(op.gate, op.targets, op.param)
            state_history.append(state.to_dict())

        result = {
            'success': True,
            'n_qubits': request.n_qubits,
            'final_state': state.to_dict(),
            'state_history': state_history,
        }

        # Measurement
        if request.measure_all:
            if request.n_shots and request.n_shots > 1:
                # Reload state from history (before measurement collapse)
                reload_state = QuantumState(request.n_qubits)
                reload_state.state_vector = state.state_vector.copy()
                counts = get_measurement_statistics(reload_state, request.n_shots)
                result['measurement_counts'] = counts
            else:
                bitstring, collapsed = measure_all(state)
                result['measurement'] = bitstring
                result['collapsed_state'] = collapsed.to_dict()

        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@app.post("/api/algorithms/{name}/run")
async def run_algorithm(name: str, request: AlgorithmRequest):
    """Run a named quantum algorithm with given parameters."""
    if name not in ALGORITHMS:
        raise HTTPException(
            status_code=404,
            detail=f"Algorithm '{name}' not found. Available: {list(ALGORITHMS.keys())}"
        )

    try:
        module = ALGORITHMS[name]['module']
        result = module.run(**request.params)
        return {
            'success': True,
            'algorithm': name,
            'result': result,
        }
    except HTTPException:
        raise
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Algorithm error: {str(e)}")


# =============================================================================
# Socket.IO Events (Step-by-Step Execution)
# =============================================================================

@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    print(f"[Socket.IO] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    """Handle client disconnection. Clean up any sessions."""
    # Clean up sessions belonging to this client
    to_remove = [k for k, v in sessions.items() if v.get('sid') == sid]
    for key in to_remove:
        del sessions[key]
    print(f"[Socket.IO] Client disconnected: {sid}")


@sio.on('start_session')
async def start_session(sid, data):
    """Start a new step-by-step simulation session.

    Args:
        data: {
            'algorithm': name,
            'params': {...},
        } or {
            'circuit': {
                'n_qubits': int,
                'operations': [...]
            }
        }
    """
    session_id = str(uuid.uuid4())

    try:
        if 'algorithm' in data:
            # Algorithm preset
            name = data['algorithm']
            if name not in ALGORITHMS:
                await sio.emit('error', {'error': f"Unknown algorithm: {name}"}, to=sid)
                return

            module = ALGORITHMS[name]['module']
            params = data.get('params', {})
            result = module.run(**params)

            sessions[session_id] = {
                'sid': sid,
                'type': 'algorithm',
                'algorithm': name,
                'state_history': result.get('state_history', []),
                'circuit': result.get('circuit', []),
                'current_step': 0,
                'result': result,
            }

        else:
            # Custom circuit
            circuit_data = data.get('circuit', {})
            n_qubits = circuit_data.get('n_qubits', 1)
            operations = circuit_data.get('operations', [])

            state = QuantumState(n_qubits)
            state_history = [state.to_dict()]

            for op_data in operations:
                gate = op_data['gate']
                targets = op_data['targets']
                param = op_data.get('param')
                if gate == 'M':
                    for t in targets:
                        _, state = measure_qubit(state, t)
                else:
                    state.apply_gate(gate, targets, param)
                state_history.append(state.to_dict())

            sessions[session_id] = {
                'sid': sid,
                'type': 'circuit',
                'n_qubits': n_qubits,
                'operations': operations,
                'state_history': state_history,
                'current_step': 0,
            }

        await sio.emit('session_started', {
            'session_id': session_id,
            'total_steps': len(sessions[session_id]['state_history']),
            'current_step': 0,
            'state': sessions[session_id]['state_history'][0],
        }, to=sid)

    except Exception as e:
        await sio.emit('error', {'error': str(e)}, to=sid)


@sio.on('step')
async def step(sid, data):
    """Navigate to a specific step in the simulation.

    Args:
        data: {
            'session_id': str,
            'action': 'next' | 'prev' | 'goto',
            'step': int (for 'goto')
        }
    """
    session_id = data.get('session_id')
    if session_id not in sessions:
        await sio.emit('error', {'error': 'Session not found'}, to=sid)
        return

    session = sessions[session_id]
    history = session['state_history']
    current = session['current_step']
    total = len(history)

    action = data.get('action', 'next')

    if action == 'next':
        new_step = min(current + 1, total - 1)
    elif action == 'prev':
        new_step = max(current - 1, 0)
    elif action == 'goto':
        new_step = max(0, min(data.get('step', 0), total - 1))
    elif action == 'reset':
        new_step = 0
    else:
        await sio.emit('error', {'error': f"Unknown action: {action}"}, to=sid)
        return

    session['current_step'] = new_step

    # Get step label from circuit if available
    circuit = session.get('circuit', session.get('operations', []))
    step_label = ''
    if new_step > 0 and new_step - 1 < len(circuit):
        step_info = circuit[new_step - 1]
        step_label = step_info.get('label', f"Step {new_step}")

    await sio.emit('step_update', {
        'session_id': session_id,
        'current_step': new_step,
        'total_steps': total,
        'state': history[new_step],
        'step_label': step_label,
        'is_first': new_step == 0,
        'is_last': new_step == total - 1,
    }, to=sid)


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")

    print(f"🚀 Quantum Simulator API starting on {host}:{port}")
    print(f"📡 CORS origins: {cors_origins}")
    print(f"🔧 Log level: {log_level}")

    uvicorn.run(
        socket_app,
        host=host,
        port=port,
        log_level=log_level,
    )
