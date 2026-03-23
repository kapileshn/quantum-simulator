"""
Pydantic Models for Quantum Simulator API
==========================================
Request/response schemas for all API endpoints.
Includes gate validation logic.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Request Models
# =============================================================================

class GateOperation(BaseModel):
    """A single gate operation in a circuit."""
    gate: str = Field(..., description="Gate name (e.g., 'H', 'CNOT', 'Rx')")
    targets: List[int] = Field(..., description="Target qubit indices")
    param: Optional[float] = Field(None, description="Gate parameter (for Rx, Ry, Rz, P)")

    @field_validator('targets')
    @classmethod
    def validate_targets(cls, v: List[int]) -> List[int]:
        if len(v) == 0:
            raise ValueError("At least one target qubit required")
        if len(set(v)) != len(v):
            raise ValueError(f"Duplicate qubit indices: {v}")
        for q in v:
            if q < 0:
                raise ValueError(f"Qubit index must be non-negative, got {q}")
        return v


class CircuitRequest(BaseModel):
    """Request to simulate a quantum circuit."""
    n_qubits: int = Field(..., ge=1, le=5, description="Number of qubits (1-5)")
    operations: List[GateOperation] = Field(..., description="List of gate operations")
    measure_all: bool = Field(False, description="Whether to measure all qubits at the end")
    n_shots: Optional[int] = Field(None, ge=1, le=10000, description="Number of measurement shots")


class AlgorithmRequest(BaseModel):
    """Request to run a specific algorithm."""
    name: str = Field(..., description="Algorithm name")
    params: Dict[str, Any] = Field(default_factory=dict, description="Algorithm-specific parameters")


class StepRequest(BaseModel):
    """Request for step-by-step execution."""
    session_id: str = Field(..., description="Session identifier")
    action: str = Field(..., description="'next', 'prev', 'reset', or 'run_all'")


# =============================================================================
# Response Models
# =============================================================================

class AmplitudeInfo(BaseModel):
    """Complex amplitude information for a single basis state."""
    index: int
    label: str
    real: float
    imag: float
    magnitude: float
    phase: float
    probability: float


class BlochCoords(BaseModel):
    """Bloch sphere coordinates for a single qubit."""
    x: float
    y: float
    z: float
    theta: float
    phi: float
    purity: float


class StateSnapshot(BaseModel):
    """Complete state information at a circuit step."""
    n_qubits: int
    amplitudes: List[AmplitudeInfo]
    probabilities: Dict[str, float]
    bloch_coords: List[BlochCoords]
    classical_bits: Dict[int, int] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    """Result of a circuit simulation."""
    success: bool = True
    n_qubits: int
    final_state: StateSnapshot
    measurement: Optional[str] = None
    measurement_counts: Optional[Dict[str, int]] = None
    state_history: Optional[List[StateSnapshot]] = None


class AlgorithmResult(BaseModel):
    """Result of running an algorithm."""
    success: bool = True
    algorithm: str
    result: Dict[str, Any]
    state_history: Optional[List[Dict]] = None


class AlgorithmInfo(BaseModel):
    """Metadata about an available algorithm."""
    name: str
    display_name: str
    description: str
    category: str  # "algorithm" or "protocol"
    parameters: List[Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Structured error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
