"""
Quantum Measurement & Collapse
===============================
Implements projective measurement on quantum states.

Mathematical foundation:
    Measurement probability: P(i) = |⟨i|ψ⟩|²
    Post-measurement state:  |ψ'⟩ = Pᵢ|ψ⟩ / √P(i)
    where Pᵢ is the projector onto outcome i.

Supports:
    - Single-qubit measurement in computational basis
    - Full system measurement
    - Measurement in arbitrary basis (X, Y, Z) for BB84
"""

from typing import Tuple, Dict, List, Optional
import numpy as np

from .quantum_state import QuantumState
from .gates import hadamard, s_dagger


def measure_qubit(
    state: QuantumState,
    qubit_index: int,
    rng: Optional[np.random.Generator] = None
) -> Tuple[int, QuantumState]:
    """Measure a single qubit in the computational (Z) basis.

    Performs a projective measurement:
        1. Calculate P(0) and P(1) for the target qubit
        2. Randomly collapse to |0⟩ or |1⟩ based on probabilities
        3. Project and renormalize the state vector

    Args:
        state: The quantum state to measure.
        qubit_index: Index of the qubit to measure.
        rng: Optional random number generator for reproducibility.

    Returns:
        Tuple of (measured_bit, new_state) where:
            - measured_bit: 0 or 1
            - new_state: Collapsed state (new copy, original unchanged)

    Raises:
        ValueError: If qubit_index is out of range.
    """
    if qubit_index < 0 or qubit_index >= state.n_qubits:
        raise ValueError(
            f"Qubit index {qubit_index} out of range for "
            f"{state.n_qubits}-qubit system."
        )

    if rng is None:
        rng = np.random.default_rng()

    n = state.n_qubits
    new_state = state.copy()

    # Calculate probability of measuring |0⟩ on target qubit
    prob_0 = 0.0
    for i in range(state.dim):
        # Check if qubit at qubit_index is 0 in basis state i
        bit = (i >> (n - 1 - qubit_index)) & 1
        if bit == 0:
            prob_0 += np.abs(state.state_vector[i]) ** 2

    prob_1 = 1.0 - prob_0

    # Random collapse
    measured_bit = 0 if rng.random() < prob_0 else 1
    collapse_prob = prob_0 if measured_bit == 0 else prob_1

    # Prevent division by zero for deterministic states
    if collapse_prob < 1e-15:
        collapse_prob = 1e-15

    # Project: zero out amplitudes inconsistent with measurement
    for i in range(state.dim):
        bit = (i >> (n - 1 - qubit_index)) & 1
        if bit != measured_bit:
            new_state.state_vector[i] = 0.0

    # Renormalize
    new_state.state_vector /= np.sqrt(collapse_prob)

    # Record classical bit
    new_state.classical_bits[qubit_index] = measured_bit

    return measured_bit, new_state


def measure_all(
    state: QuantumState,
    rng: Optional[np.random.Generator] = None
) -> Tuple[str, QuantumState]:
    """Measure all qubits in the computational basis.

    Collapses the entire state to a single basis state.

    Args:
        state: The quantum state to measure.
        rng: Optional random number generator.

    Returns:
        Tuple of (bitstring, new_state) where:
            - bitstring: String of 0s and 1s (e.g., "01101")
            - new_state: Fully collapsed state
    """
    if rng is None:
        rng = np.random.default_rng()

    # Get probability distribution
    probs = np.abs(state.state_vector) ** 2

    # Normalize to handle floating-point drift
    probs /= probs.sum()

    # Sample one basis state
    outcome = rng.choice(state.dim, p=probs)

    # Create collapsed state
    new_state = state.copy()
    new_state.state_vector = np.zeros(state.dim, dtype=complex)
    new_state.state_vector[outcome] = 1.0

    # Record all classical bits
    bitstring = format(outcome, f'0{state.n_qubits}b')
    for i, bit in enumerate(bitstring):
        new_state.classical_bits[i] = int(bit)

    return bitstring, new_state


def measure_in_basis(
    state: QuantumState,
    qubit_index: int,
    basis: str,
    rng: Optional[np.random.Generator] = None
) -> Tuple[int, QuantumState]:
    """Measure a single qubit in a specified basis.

    Supported bases:
        - 'Z' (computational): Standard |0⟩/|1⟩ measurement
        - 'X' (Hadamard):      Measure in |+⟩/|−⟩ basis
        - 'Y':                 Measure in |i⟩/|−i⟩ basis

    Implementation:
        1. Rotate to computational basis (apply basis change gate)
        2. Measure in Z basis
        3. Rotate back (not applied — state is collapsed)

    This is essential for BB84 protocol where Alice and Bob
    independently choose random measurement bases.

    Args:
        state: The quantum state to measure.
        qubit_index: Index of the qubit to measure.
        basis: One of 'X', 'Y', 'Z'.
        rng: Optional random number generator.

    Returns:
        Tuple of (measured_bit, new_state).

    Raises:
        ValueError: If basis is not 'X', 'Y', or 'Z'.
    """
    basis = basis.upper()
    if basis not in ('X', 'Y', 'Z'):
        raise ValueError(f"Basis must be 'X', 'Y', or 'Z', got '{basis}'.")

    if basis == 'Z':
        return measure_qubit(state, qubit_index, rng)

    # For X and Y bases, transform to Z basis first
    transformed = state.copy()

    if basis == 'X':
        # X basis: apply H to rotate |+⟩→|0⟩, |−⟩→|1⟩
        transformed.apply_gate("H", [qubit_index])
    elif basis == 'Y':
        # Y basis: apply S†H to rotate |i⟩→|0⟩, |−i⟩→|1⟩
        transformed.apply_gate("S†", [qubit_index])
        transformed.apply_gate("H", [qubit_index])

    # Measure in computational basis
    result, collapsed = measure_qubit(transformed, qubit_index, rng)

    return result, collapsed


def get_measurement_statistics(
    state: QuantumState,
    n_shots: int = 1000,
    rng: Optional[np.random.Generator] = None
) -> Dict[str, int]:
    """Run measurement multiple times and collect statistics.

    Useful for demonstrating the probabilistic nature of quantum measurement.

    Args:
        state: The quantum state to measure (not modified).
        n_shots: Number of measurement repetitions.
        rng: Optional random number generator.

    Returns:
        Dictionary mapping bitstrings to counts.
    """
    if rng is None:
        rng = np.random.default_rng()

    probs = np.abs(state.state_vector) ** 2
    probs /= probs.sum()

    outcomes = rng.choice(state.dim, size=n_shots, p=probs)

    counts: Dict[str, int] = {}
    for outcome in outcomes:
        bitstring = format(outcome, f'0{state.n_qubits}b')
        counts[bitstring] = counts.get(bitstring, 0) + 1

    return dict(sorted(counts.items()))
