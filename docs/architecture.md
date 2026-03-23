# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Algorithm │  │ Circuit  │  │  Bloch   │  │ Statevector│ │
│  │ Selector │  │  Editor  │  │  Sphere  │  │   Panel    │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘ │
│       └──────────────┴──────────────┴──────────────┘        │
│                        Zustand Store                        │
│                     Socket.IO Client                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ WebSocket / REST
┌──────────────────────────┴──────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │  REST Endpoints  │  │  Socket.IO (step-by-step)      │  │
│  └────────┬────────┘  └───────────────┬─────────────────┘  │
│           └───────────────────────────┘                     │
│                    Simulation Engine                         │
│  ┌────────────┐  ┌──────────┐  ┌─────────────┐            │
│  │QuantumState│  │  Gates   │  │ Measurement │            │
│  └─────┬──────┘  └────┬─────┘  └──────┬──────┘            │
│        └───────────────┴───────────────┘                    │
│                   Algorithms                                │
│  ┌─────────┐ ┌───────┐ ┌──────┐ ┌─────┐ ┌──────┐         │
│  │ D-Jozsa │ │Grover │ │Telep.│ │BB84 │ │ QRNG │         │
│  └─────────┘ └───────┘ └──────┘ └─────┘ └──────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User selects algorithm** → AlgorithmSelector sends `POST /api/algorithms/{name}/run`
2. **Backend executes** → Simulation engine runs algorithm, records state at each step
3. **State history returned** → Zustand store receives `state_history[]`
4. **Per-step visualization** → StepController navigates; BlochSphere, StatevectorPanel update
5. **Real-time mode** → Socket.IO provides live state push during step-by-step execution

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/gates` | List all quantum gates |
| GET | `/api/algorithms` | List available algorithms |
| POST | `/api/simulate` | Run a custom circuit |
| POST | `/api/algorithms/{name}/run` | Run a named algorithm |

### Socket.IO Events

| Event | Direction | Data |
|-------|-----------|------|
| `start_session` | Client → Server | `{ algorithm, params }` |
| `session_started` | Server → Client | `{ session_id, total_steps, state }` |
| `step` | Client → Server | `{ session_id, action }` |
| `step_update` | Server → Client | `{ current_step, state, step_label }` |

## Gate Library

17 gates implemented as explicit NumPy matrices:

**Single-qubit**: I, X, Y, Z, H, S, S†, T, T†, P(φ), Rx(θ), Ry(θ), Rz(θ)  
**Two-qubit**: CNOT, CZ, SWAP  
**Three-qubit**: Toffoli (CCX)
