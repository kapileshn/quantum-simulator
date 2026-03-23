"""
Quantum Simulator Engine
========================
A custom NumPy-based quantum computing simulation engine.
Supports statevector simulation for up to 5 qubits with explicit
matrix operations for all standard quantum gates.
"""

from .quantum_state import QuantumState
from .gates import *
from .measurement import measure_qubit, measure_all, measure_in_basis

__version__ = "1.0.0"
