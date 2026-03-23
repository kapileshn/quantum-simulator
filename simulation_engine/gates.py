"""
Quantum Gate Definitions
========================
All quantum gates implemented as explicit NumPy matrices.
Every gate is verified to be unitary: U†U = I.

Mathematical foundation:
    Gate operation: |ψ'⟩ = U|ψ⟩  where U is unitary (U†U = I)

Supported gates:
    Single-qubit: I, X, Y, Z, H, S, S†, T, T†, P(φ), Rx(θ), Ry(θ), Rz(θ)
    Two-qubit:    CNOT, CZ, SWAP
    Three-qubit:  Toffoli (CCX)
"""

from typing import List, Tuple, Optional
import numpy as np


# =============================================================================
# Single-Qubit Gates
# =============================================================================

def identity() -> np.ndarray:
    """Identity gate (I).

    Matrix:
        [[1, 0],
         [0, 1]]

    Returns:
        2x2 complex identity matrix.
    """
    return np.eye(2, dtype=complex)


def pauli_x() -> np.ndarray:
    """Pauli-X gate (NOT gate / bit-flip).

    Matrix:
        [[0, 1],
         [1, 0]]

    Action: |0⟩ → |1⟩, |1⟩ → |0⟩

    Returns:
        2x2 complex Pauli-X matrix.
    """
    return np.array([[0, 1],
                     [1, 0]], dtype=complex)


def pauli_y() -> np.ndarray:
    """Pauli-Y gate.

    Matrix:
        [[0, -i],
         [i,  0]]

    Action: |0⟩ → i|1⟩, |1⟩ → -i|0⟩

    Returns:
        2x2 complex Pauli-Y matrix.
    """
    return np.array([[0, -1j],
                     [1j, 0]], dtype=complex)


def pauli_z() -> np.ndarray:
    """Pauli-Z gate (phase-flip).

    Matrix:
        [[1,  0],
         [0, -1]]

    Action: |0⟩ → |0⟩, |1⟩ → -|1⟩

    Returns:
        2x2 complex Pauli-Z matrix.
    """
    return np.array([[1, 0],
                     [0, -1]], dtype=complex)


def hadamard() -> np.ndarray:
    """Hadamard gate (H).

    Matrix:
        (1/√2) [[1,  1],
                 [1, -1]]

    Action: |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2
            |1⟩ → |−⟩ = (|0⟩−|1⟩)/√2

    Returns:
        2x2 complex Hadamard matrix.
    """
    return np.array([[1, 1],
                     [1, -1]], dtype=complex) / np.sqrt(2)


def phase_gate(phi: float) -> np.ndarray:
    """General phase gate P(φ).

    Matrix:
        [[1, 0       ],
         [0, e^(iφ)  ]]

    Args:
        phi: Phase angle in radians.

    Returns:
        2x2 complex phase gate matrix.
    """
    return np.array([[1, 0],
                     [0, np.exp(1j * phi)]], dtype=complex)


def s_gate() -> np.ndarray:
    """S gate (Phase gate with φ = π/2, √Z).

    Matrix:
        [[1, 0],
         [0, i]]

    Equivalent to P(π/2).

    Returns:
        2x2 complex S gate matrix.
    """
    return phase_gate(np.pi / 2)


def s_dagger() -> np.ndarray:
    """S† gate (conjugate transpose of S gate).

    Matrix:
        [[1,  0],
         [0, -i]]

    Equivalent to P(-π/2).

    Returns:
        2x2 complex S† gate matrix.
    """
    return phase_gate(-np.pi / 2)


def t_gate() -> np.ndarray:
    """T gate (π/8 gate, √S).

    Matrix:
        [[1, 0         ],
         [0, e^(iπ/4)  ]]

    Equivalent to P(π/4).

    Returns:
        2x2 complex T gate matrix.
    """
    return phase_gate(np.pi / 4)


def t_dagger() -> np.ndarray:
    """T† gate (conjugate transpose of T gate).

    Matrix:
        [[1, 0          ],
         [0, e^(-iπ/4)  ]]

    Equivalent to P(-π/4).

    Returns:
        2x2 complex T† gate matrix.
    """
    return phase_gate(-np.pi / 4)


def rx(theta: float) -> np.ndarray:
    """Rotation around X-axis by angle θ.

    Matrix:
        [[cos(θ/2),    -i·sin(θ/2)],
         [-i·sin(θ/2),  cos(θ/2)  ]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex Rx rotation matrix.
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -1j * s],
                     [-1j * s, c]], dtype=complex)


def ry(theta: float) -> np.ndarray:
    """Rotation around Y-axis by angle θ.

    Matrix:
        [[cos(θ/2), -sin(θ/2)],
         [sin(θ/2),  cos(θ/2)]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex Ry rotation matrix.
    """
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -s],
                     [s, c]], dtype=complex)


def rz(theta: float) -> np.ndarray:
    """Rotation around Z-axis by angle θ.

    Matrix:
        [[e^(-iθ/2), 0        ],
         [0,          e^(iθ/2)]]

    Args:
        theta: Rotation angle in radians.

    Returns:
        2x2 complex Rz rotation matrix.
    """
    return np.array([[np.exp(-1j * theta / 2), 0],
                     [0, np.exp(1j * theta / 2)]], dtype=complex)


# =============================================================================
# Multi-Qubit Gates
# =============================================================================

def cnot() -> np.ndarray:
    """Controlled-NOT (CNOT / CX) gate.

    Matrix (control=0, target=1):
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1],
         [0, 0, 1, 0]]

    Action: |00⟩ → |00⟩, |01⟩ → |01⟩, |10⟩ → |11⟩, |11⟩ → |10⟩

    Returns:
        4x4 complex CNOT matrix.
    """
    return np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1],
                     [0, 0, 1, 0]], dtype=complex)


def cz() -> np.ndarray:
    """Controlled-Z (CZ) gate.

    Matrix:
        [[1, 0, 0,  0],
         [0, 1, 0,  0],
         [0, 0, 1,  0],
         [0, 0, 0, -1]]

    Action: Applies Z to target when control is |1⟩.

    Returns:
        4x4 complex CZ matrix.
    """
    return np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, -1]], dtype=complex)


def swap() -> np.ndarray:
    """SWAP gate.

    Matrix:
        [[1, 0, 0, 0],
         [0, 0, 1, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1]]

    Action: |01⟩ → |10⟩, |10⟩ → |01⟩

    Returns:
        4x4 complex SWAP matrix.
    """
    return np.array([[1, 0, 0, 0],
                     [0, 0, 1, 0],
                     [0, 1, 0, 0],
                     [0, 0, 0, 1]], dtype=complex)


def toffoli() -> np.ndarray:
    """Toffoli (CCX / CCNOT) gate.

    8x8 matrix that flips the target qubit only when both
    control qubits are |1⟩. Acts as identity on all other states.

    Action: |110⟩ → |111⟩, |111⟩ → |110⟩ (all others unchanged)

    Returns:
        8x8 complex Toffoli matrix.
    """
    gate = np.eye(8, dtype=complex)
    # Swap |110⟩ (index 6) and |111⟩ (index 7)
    gate[6, 6] = 0
    gate[7, 7] = 0
    gate[6, 7] = 1
    gate[7, 6] = 1
    return gate


# =============================================================================
# Gate Metadata Registry
# =============================================================================

# Maps gate names to (factory_function, n_qubits, has_parameter)
GATE_REGISTRY: dict = {
    # Single-qubit gates (no parameter)
    "I": {"func": identity, "n_qubits": 1, "param": None, "label": "I", "desc": "Identity"},
    "X": {"func": pauli_x, "n_qubits": 1, "param": None, "label": "X", "desc": "Pauli-X (NOT)"},
    "Y": {"func": pauli_y, "n_qubits": 1, "param": None, "label": "Y", "desc": "Pauli-Y"},
    "Z": {"func": pauli_z, "n_qubits": 1, "param": None, "label": "Z", "desc": "Pauli-Z"},
    "H": {"func": hadamard, "n_qubits": 1, "param": None, "label": "H", "desc": "Hadamard"},
    "S": {"func": s_gate, "n_qubits": 1, "param": None, "label": "S", "desc": "S (√Z)"},
    "S†": {"func": s_dagger, "n_qubits": 1, "param": None, "label": "S†", "desc": "S-dagger"},
    "T": {"func": t_gate, "n_qubits": 1, "param": None, "label": "T", "desc": "T (π/8)"},
    "T†": {"func": t_dagger, "n_qubits": 1, "param": None, "label": "T†", "desc": "T-dagger"},
    # Single-qubit gates (parameterized)
    "P": {"func": phase_gate, "n_qubits": 1, "param": "phi", "label": "P", "desc": "Phase(φ)"},
    "Rx": {"func": rx, "n_qubits": 1, "param": "theta", "label": "Rx", "desc": "Rx(θ)"},
    "Ry": {"func": ry, "n_qubits": 1, "param": "theta", "label": "Ry", "desc": "Ry(θ)"},
    "Rz": {"func": rz, "n_qubits": 1, "param": "theta", "label": "Rz", "desc": "Rz(θ)"},
    # Multi-qubit gates
    "CNOT": {"func": cnot, "n_qubits": 2, "param": None, "label": "CX", "desc": "Controlled-NOT"},
    "CZ": {"func": cz, "n_qubits": 2, "param": None, "label": "CZ", "desc": "Controlled-Z"},
    "SWAP": {"func": swap, "n_qubits": 2, "param": None, "label": "SW", "desc": "SWAP"},
    "CCX": {"func": toffoli, "n_qubits": 3, "param": None, "label": "CCX", "desc": "Toffoli"},
}


# =============================================================================
# Gate Utility Functions
# =============================================================================

def get_gate_matrix(name: str, param: Optional[float] = None) -> np.ndarray:
    """Get the matrix for a named gate, optionally with a parameter.

    Args:
        name: Gate identifier (must be in GATE_REGISTRY).
        param: Parameter value for parameterized gates (P, Rx, Ry, Rz).

    Returns:
        The unitary matrix for the gate.

    Raises:
        ValueError: If gate name is unknown or parameter is missing/unexpected.
    """
    if name not in GATE_REGISTRY:
        raise ValueError(f"Unknown gate: '{name}'. Available: {list(GATE_REGISTRY.keys())}")

    info = GATE_REGISTRY[name]
    if info["param"] is not None:
        if param is None:
            raise ValueError(f"Gate '{name}' requires parameter '{info['param']}'.")
        return info["func"](param)
    else:
        if param is not None:
            raise ValueError(f"Gate '{name}' does not accept parameters.")
        return info["func"]()


def validate_gate_placement(
    gate_name: str,
    target_qubits: List[int],
    n_qubits: int
) -> Tuple[bool, str]:
    """Validate that a gate placement is legal.

    Checks:
        1. Gate name exists in registry
        2. Number of target qubits matches gate requirements
        3. All target qubits are within bounds [0, n_qubits)
        4. No duplicate target qubits

    Args:
        gate_name: Name of the gate.
        target_qubits: List of qubit indices the gate targets.
        n_qubits: Total number of qubits in the circuit.

    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
    """
    if gate_name not in GATE_REGISTRY:
        return False, f"Unknown gate: '{gate_name}'"

    info = GATE_REGISTRY[gate_name]
    expected_qubits = info["n_qubits"]

    if len(target_qubits) != expected_qubits:
        return False, (
            f"Gate '{gate_name}' requires {expected_qubits} qubit(s), "
            f"but {len(target_qubits)} provided."
        )

    for q in target_qubits:
        if q < 0 or q >= n_qubits:
            return False, (
                f"Qubit index {q} out of bounds for {n_qubits}-qubit system "
                f"(valid: 0 to {n_qubits - 1})."
            )

    if len(set(target_qubits)) != len(target_qubits):
        return False, f"Duplicate qubit indices in target: {target_qubits}"

    return True, ""


def expand_gate(
    gate_matrix: np.ndarray,
    target_qubits: List[int],
    n_qubits: int
) -> np.ndarray:
    """Expand a gate matrix to the full Hilbert space via tensor products.

    For a gate U acting on target qubits within an n-qubit system,
    constructs the full 2^n × 2^n matrix using the appropriate
    tensor product structure.

    Uses the permutation approach:
        1. Reorder qubits so targets are at the front
        2. Apply U ⊗ I on the reordered space
        3. Reverse the reordering

    Args:
        gate_matrix: The unitary matrix of the gate (2^k × 2^k for k-qubit gate).
        target_qubits: List of qubit indices the gate acts on.
        n_qubits: Total number of qubits in the system.

    Returns:
        Full 2^n × 2^n unitary matrix.

    Raises:
        ValueError: If dimensions don't match.
    """
    n_gate_qubits = len(target_qubits)
    expected_size = 2 ** n_gate_qubits

    if gate_matrix.shape != (expected_size, expected_size):
        raise ValueError(
            f"Gate matrix shape {gate_matrix.shape} doesn't match "
            f"{n_gate_qubits} target qubits (expected {expected_size}x{expected_size})."
        )

    dim = 2 ** n_qubits

    if n_gate_qubits == n_qubits:
        # Gate acts on all qubits — may need qubit reordering
        if target_qubits == list(range(n_qubits)):
            return gate_matrix.copy()

    # Build the full matrix by computing its action on each basis state
    full_matrix = np.zeros((dim, dim), dtype=complex)

    for col in range(dim):
        # Decompose basis state index into individual qubit values
        input_bits = [(col >> (n_qubits - 1 - q)) & 1 for q in range(n_qubits)]

        # Extract the bits for target qubits
        target_bits = [input_bits[q] for q in target_qubits]
        target_index = sum(b << (n_gate_qubits - 1 - i) for i, b in enumerate(target_bits))

        # Apply gate to target subspace
        for target_out in range(expected_size):
            amplitude = gate_matrix[target_out, target_index]
            if amplitude == 0:
                continue

            # Reconstruct full output bits
            output_bits = input_bits.copy()
            for i, q in enumerate(target_qubits):
                output_bits[q] = (target_out >> (n_gate_qubits - 1 - i)) & 1

            # Convert bits back to index
            row = sum(b << (n_qubits - 1 - q) for q, b in enumerate(output_bits))
            full_matrix[row, col] += amplitude

    return full_matrix
