# Quantum Protocol & Algorithm Simulator

> **QtHack04 — Track 04: Quantum Systems, Problem #21**  
> SRMIST Kattankulatham | March 30–31, 2026

A professional-grade, interactive quantum computing simulator for students and researchers. Experiment with quantum protocols and algorithms through an intuitive circuit editor with real-time Bloch sphere and statevector visualization — no physical hardware required.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![React](https://img.shields.io/badge/react-19-purple)

## Features

### Quantum Algorithms
- **Deutsch–Jozsa** — Determines if a function is constant or balanced in one query
- **Grover's Search** — Finds marked items with quadratic speedup
- **QRNG** — Generates truly random numbers using quantum superposition

### Quantum Protocols
- **Quantum Teleportation** — Transfers quantum state via entanglement + classical bits
- **BB84 QKD** — Quantum key distribution with eavesdropping detection

### Visualization
- 🌐 **Bloch Sphere** — Three.js/WebGL with animated state vectors per qubit
- 📊 **Statevector Panel** — Complex amplitudes table + probability histogram
- ≡ **Circuit Editor** — SVG-based with click-to-place gates
- ⏯ **Step-by-Step** — Walk through circuits gate by gate with state diffs

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Simulation Engine | Python + NumPy (custom, no Qiskit) |
| Backend API | FastAPI + Socket.IO |
| Frontend | React 19 + TypeScript + Vite 8 |
| 3D Visualization | Three.js via @react-three/fiber |
| Charts | Recharts |
| State Management | Zustand |

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend
```bash
cd quantum-simulator
pip install -r requirements.txt
python -m api.simulation_api
```
Server starts on `http://localhost:8000`

### Frontend
```bash
cd quantum-simulator/frontend
npm install
npm run dev
```
App opens at `http://localhost:5173`

### Run Tests
```bash
cd quantum-simulator
python -m pytest tests/ -v
```

## Project Structure

```
quantum-simulator/
├── simulation_engine/        # Core quantum mechanics (NumPy)
│   ├── quantum_state.py      # Statevector management
│   ├── gates.py              # 17 unitary gate matrices
│   ├── measurement.py        # Multi-basis measurement & collapse
│   └── algorithms/           # DJ, Grover, Teleportation, BB84, QRNG
├── api/                      # FastAPI + Socket.IO backend
│   ├── simulation_api.py
│   └── models.py             # Pydantic schemas + gate validation
├── frontend/                 # React + TypeScript + Vite
│   └── src/
│       ├── components/       # 5 UI components
│       ├── store/            # Zustand global state
│       ├── hooks/            # Socket.IO hook
│       └── types/            # TypeScript interfaces
├── tests/                    # pytest (126 tests)
└── docs/
    └── architecture.md
```

## Mathematical Foundation

All gates are implemented as explicit matrix operations:

- **Qubit state**: |ψ⟩ = α|0⟩ + β|1⟩, where |α|² + |β|² = 1
- **Gate operation**: |ψ'⟩ = U|ψ⟩ (U is unitary: U†U = I)
- **Measurement**: P(i) = |⟨i|ψ⟩|²

## Extensibility

Designed for future expansion:
- 🔧 Noise models (depolarizing, bit-flip)
- 📈 Decoherence simulation
- 🛡 Quantum error correction hooks
- 🔌 Quantum hardware API integration

## License

MIT
