"""
Deutsch-Jozsa Algorithm
=======================
Determines whether a function f: {0,1}ⁿ → {0,1} is constant or balanced 
in a single query (exponential speedup over classical).

Algorithm:
    1. Initialize n+1 qubits: |0⟩⊗n|1⟩
    2. Apply H to all qubits
    3. Apply oracle Uf
    4. Apply H to first n qubits
    5. Measure first n qubits:
       - All zeros → constant
       - Any non-zero → balanced

Oracle types:
    - Constant-0: f(x) = 0 for all x → Uf = I
    - Constant-1: f(x) = 1 for all x → Uf flips ancilla always
    - Balanced:   f(x) = 0 for half, 1 for other half
"""

from typing import List, Dict, Optional, Tuple
import numpy as np

from ..quantum_state import QuantumState
from ..gates import get_gate_matrix, GATE_REGISTRY


def build_constant_oracle(n_input: int, value: int) -> np.ndarray:
    """Build oracle matrix for a constant function.

    Args:
        n_input: Number of input qubits.
        value: 0 for f(x)=0, 1 for f(x)=1.

    Returns:
        Unitary oracle matrix of size 2^(n+1) × 2^(n+1).
    """
    n_total = n_input + 1
    dim = 2 ** n_total

    if value == 0:
        # f(x) = 0: oracle is identity
        return np.eye(dim, dtype=complex)
    else:
        # f(x) = 1: flip ancilla for all inputs → X on last qubit
        oracle = np.zeros((dim, dim), dtype=complex)
        for i in range(dim):
            # Flip the last bit
            j = i ^ 1
            oracle[j, i] = 1.0
        return oracle


def build_balanced_oracle(n_input: int, pattern: Optional[int] = None) -> np.ndarray:
    """Build oracle matrix for a balanced function.

    The balanced function returns 1 for exactly half of all inputs.
    Uses a specific bit pattern to determine which inputs map to 1.

    Args:
        n_input: Number of input qubits.
        pattern: Bitmask determining f(x). f(x) = popcount(x & pattern) mod 2.
                 If None, uses pattern where MSB determines output.

    Returns:
        Unitary oracle matrix of size 2^(n+1) × 2^(n+1).
    """
    n_total = n_input + 1
    dim = 2 ** n_total

    if pattern is None:
        # Default: f(x) = x's MSB (most significant bit)
        pattern = 1 << (n_input - 1)

    oracle = np.zeros((dim, dim), dtype=complex)

    for i in range(dim):
        # Split into input bits and ancilla
        ancilla = i & 1
        input_val = i >> 1

        # Compute f(x) = popcount(x & pattern) mod 2
        f_x = bin(input_val & pattern).count('1') % 2

        # Oracle: |x⟩|y⟩ → |x⟩|y ⊕ f(x)⟩
        new_ancilla = ancilla ^ f_x
        j = (input_val << 1) | new_ancilla
        oracle[j, i] = 1.0

    return oracle


def generate_circuit(
    n_input: int = 2,
    oracle_type: str = "balanced",
    pattern: Optional[int] = None
) -> List[Dict]:
    """Generate the Deutsch-Jozsa circuit as step-by-step instructions.

    Args:
        n_input: Number of input qubits (1 to 4).
        oracle_type: "constant_0", "constant_1", or "balanced".
        pattern: Bitmask for balanced oracle (optional).

    Returns:
        List of circuit steps, each a dict with:
            - 'gate': gate name
            - 'targets': list of qubit indices
            - 'label': human-readable step description
            - 'param': optional gate parameter

    Raises:
        ValueError: If oracle_type is invalid or n_input out of range.
    """
    if not 1 <= n_input <= 4:
        raise ValueError(f"n_input must be 1-4, got {n_input}")

    valid_types = ("constant_0", "constant_1", "balanced")
    if oracle_type not in valid_types:
        raise ValueError(f"oracle_type must be one of {valid_types}")

    n_total = n_input + 1  # input qubits + 1 ancilla
    steps: List[Dict] = []

    # Step 1: Initialize ancilla to |1⟩ by applying X
    steps.append({
        'gate': 'X',
        'targets': [n_input],  # ancilla is last qubit
        'label': f'Initialize ancilla qubit {n_input} to |1⟩',
        'param': None,
    })

    # Step 2: Apply Hadamard to all qubits
    for i in range(n_total):
        steps.append({
            'gate': 'H',
            'targets': [i],
            'label': f'Apply H to qubit {i} (create superposition)',
            'param': None,
        })

    # Step 3: Apply Oracle (as a custom matrix gate)
    steps.append({
        'gate': '__oracle__',
        'targets': list(range(n_total)),
        'label': f'Apply {oracle_type} oracle Uf',
        'param': None,
        'oracle_type': oracle_type,
        'oracle_pattern': pattern,
    })

    # Step 4: Apply Hadamard to input qubits (not ancilla)
    for i in range(n_input):
        steps.append({
            'gate': 'H',
            'targets': [i],
            'label': f'Apply H to input qubit {i}',
            'param': None,
        })

    # Step 5: Measure input qubits
    for i in range(n_input):
        steps.append({
            'gate': '__measure__',
            'targets': [i],
            'label': f'Measure input qubit {i}',
            'param': None,
        })

    return steps


def run(
    n_input: int = 2,
    oracle_type: str = "balanced",
    pattern: Optional[int] = None
) -> Dict:
    """Execute the Deutsch-Jozsa algorithm and return results.

    Args:
        n_input: Number of input qubits (1-4).
        oracle_type: "constant_0", "constant_1", or "balanced".
        pattern: Bitmask for balanced oracle.

    Returns:
        Dict with:
            - 'circuit': step-by-step circuit description
            - 'result': "constant" or "balanced"
            - 'measurement': measured bitstring
            - 'state_history': list of state snapshots at each step
    """
    n_total = n_input + 1
    state = QuantumState(n_total)
    circuit = generate_circuit(n_input, oracle_type, pattern)
    state_history = [state.to_dict()]

    # Build oracle matrix
    if oracle_type == "constant_0":
        oracle_matrix = build_constant_oracle(n_input, 0)
    elif oracle_type == "constant_1":
        oracle_matrix = build_constant_oracle(n_input, 1)
    else:
        oracle_matrix = build_balanced_oracle(n_input, pattern)

    measured_bits = {}

    for step in circuit:
        if step['gate'] == '__oracle__':
            state.apply_gate_matrix(oracle_matrix, step['targets'])
        elif step['gate'] == '__measure__':
            from ..measurement import measure_qubit
            bit, state = measure_qubit(state, step['targets'][0])
            measured_bits[step['targets'][0]] = bit
        else:
            state.apply_gate(step['gate'], step['targets'], step.get('param'))

        state_history.append(state.to_dict())

    # Determine result: all input qubits measured 0 → constant
    input_measurements = [measured_bits.get(i, 0) for i in range(n_input)]
    is_constant = all(b == 0 for b in input_measurements)

    return {
        'algorithm': 'deutsch_jozsa',
        'n_input': n_input,
        'oracle_type': oracle_type,
        'circuit': circuit,
        'result': 'constant' if is_constant else 'balanced',
        'measurement': ''.join(str(b) for b in input_measurements),
        'state_history': state_history,
    }
