"""
Quantum Random Number Generator (QRNG)
=======================================
Generates truly random numbers using quantum superposition.

The simplest quantum algorithm:
    1. Prepare qubit in |0⟩
    2. Apply Hadamard: |0⟩ → (|0⟩ + |1⟩)/√2
    3. Measure: 50/50 chance of 0 or 1
    4. Repeat N times for N random bits

The randomness is guaranteed by quantum mechanics —
unlike pseudo-random number generators (PRNGs),
the outcome is fundamentally unpredictable.
"""

from typing import Dict, Optional, List
import numpy as np
from collections import Counter

from ..quantum_state import QuantumState
from ..measurement import measure_qubit


def generate_circuit(n_bits: int = 8) -> List[Dict]:
    """Generate the QRNG circuit for N random bits.

    Each bit requires: prepare |0⟩ → H → measure.
    For visualization, we show each round as a step.

    Args:
        n_bits: Number of random bits to generate.

    Returns:
        List of circuit steps.
    """
    steps: List[Dict] = []

    for i in range(n_bits):
        steps.append({
            'gate': 'H',
            'targets': [0],
            'label': f'Bit {i + 1}/{n_bits}: Apply H to |0⟩',
            'param': None,
            'round': i,
        })
        steps.append({
            'gate': '__measure__',
            'targets': [0],
            'label': f'Bit {i + 1}/{n_bits}: Measure',
            'param': None,
            'round': i,
        })

    return steps


def run(
    n_bits: int = 8,
    seed: Optional[int] = None
) -> Dict:
    """Execute the QRNG to generate random bits.

    Args:
        n_bits: Number of random bits (1 to 256).
        seed: Random seed (for demonstration reproducibility only).

    Returns:
        Dict with bitstring, integer value, and frequency analysis.
    """
    if not 1 <= n_bits <= 256:
        raise ValueError(f"n_bits must be 1-256, got {n_bits}")

    rng = np.random.default_rng(seed)
    circuit = generate_circuit(n_bits)

    bits: List[int] = []
    state_history: List[Dict] = []

    for i in range(n_bits):
        # Fresh qubit each round
        state = QuantumState(1)
        state_history.append(state.to_dict())

        # Apply Hadamard
        state.apply_gate('H', [0])
        state_history.append(state.to_dict())

        # Measure
        bit, state = measure_qubit(state, 0, rng)
        bits.append(bit)
        state_history.append(state.to_dict())

    # Compose result
    bitstring = ''.join(str(b) for b in bits)

    # Convert to integer (if ≤ 64 bits)
    int_value = int(bitstring, 2) if n_bits <= 64 else None

    # Frequency analysis
    counts = Counter(bits)
    n_zeros = counts.get(0, 0)
    n_ones = counts.get(1, 0)

    # Hex representation (if applicable)
    hex_value = None
    if n_bits % 4 == 0 and n_bits <= 64:
        hex_value = hex(int(bitstring, 2))

    return {
        'algorithm': 'qrng',
        'n_bits': n_bits,
        'circuit': circuit,
        'bitstring': bitstring,
        'integer_value': int_value,
        'hex_value': hex_value,
        'frequency': {
            'zeros': n_zeros,
            'ones': n_ones,
            'ratio': n_ones / n_bits if n_bits > 0 else 0,
        },
        'state_history': state_history,
        'summary': (
            f"Generated {n_bits} quantum random bits: {bitstring[:32]}"
            f"{'...' if n_bits > 32 else ''}\n"
            f"Distribution: {n_zeros} zeros, {n_ones} ones "
            f"({n_ones/n_bits*100:.1f}% ones)"
        ),
    }
