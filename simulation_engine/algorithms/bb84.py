"""
BB84 Quantum Key Distribution Protocol
=======================================
Simulates the BB84 protocol for quantum key distribution (QKD),
enabling two parties (Alice and Bob) to establish a shared secret key
using quantum mechanics, with eavesdropping detection.

Protocol steps:
    1. Alice generates random bits and random bases (Z or X)
    2. Alice prepares qubits:
       - Basis Z: |0⟩ for bit 0, |1⟩ for bit 1
       - Basis X: |+⟩ for bit 0, |−⟩ for bit 1
    3. (Optional) Eve intercepts, measures, and resends
    4. Bob chooses random bases and measures
    5. Sifting: Alice and Bob compare bases (public channel)
       - Keep bits where bases match
    6. Error estimation: compare subset of sifted key
       - If error rate > 11% → eavesdropping detected

Note: BB84 is a multi-round protocol, NOT a single circuit.
Each round involves preparing and measuring one qubit.
"""

from typing import List, Dict, Optional
import numpy as np

from ..quantum_state import QuantumState
from ..measurement import measure_qubit, measure_in_basis


def run(
    n_bits: int = 16,
    eve_present: bool = False,
    seed: Optional[int] = None
) -> Dict:
    """Execute the BB84 QKD protocol.

    Args:
        n_bits: Number of qubits to exchange (8 to 64).
        eve_present: Whether Eve intercepts the channel.
        seed: Random seed for reproducibility.

    Returns:
        Dict with per-round data, sifted key, error rate, and security status.
    """
    if not 4 <= n_bits <= 64:
        raise ValueError(f"n_bits must be 4-64, got {n_bits}")

    rng = np.random.default_rng(seed)

    # ========================================
    # Step 1: Alice generates random data
    # ========================================
    alice_bits = rng.integers(0, 2, size=n_bits)
    alice_bases = rng.integers(0, 2, size=n_bits)  # 0=Z, 1=X

    # ========================================
    # Step 2-4: Per-round quantum exchange
    # ========================================
    rounds: List[Dict] = []
    bob_bases = rng.integers(0, 2, size=n_bits)  # 0=Z, 1=X
    bob_bits = np.zeros(n_bits, dtype=int)
    eve_bits = np.zeros(n_bits, dtype=int) if eve_present else None
    eve_bases = rng.integers(0, 2, size=n_bits) if eve_present else None

    for i in range(n_bits):
        # Prepare qubit
        state = QuantumState(1)
        basis_name = 'Z' if alice_bases[i] == 0 else 'X'

        # Apply gates to encode Alice's bit in her chosen basis
        if alice_bits[i] == 1:
            state.apply_gate('X', [0])  # |0⟩ → |1⟩
        if alice_bases[i] == 1:
            state.apply_gate('H', [0])  # Z→X basis: |0⟩→|+⟩, |1⟩→|−⟩

        alice_state = state.to_dict()

        # Eve's interception (if present)
        eve_info = None
        if eve_present and eve_bases is not None:
            eve_basis = 'Z' if eve_bases[i] == 0 else 'X'
            eve_bit, state = measure_in_basis(state, 0, eve_basis, rng)
            eve_bits[i] = eve_bit
            eve_info = {
                'basis': eve_basis,
                'measured_bit': int(eve_bit),
            }
            # Eve must resend: prepare a new qubit in the measured state
            state = QuantumState(1)
            if eve_bit == 1:
                state.apply_gate('X', [0])
            if eve_bases[i] == 1:
                state.apply_gate('H', [0])

        # Bob measures in his chosen basis
        bob_basis_name = 'Z' if bob_bases[i] == 0 else 'X'
        bob_bit, _ = measure_in_basis(state, 0, bob_basis_name, rng)
        bob_bits[i] = bob_bit

        rounds.append({
            'round': i,
            'alice_bit': int(alice_bits[i]),
            'alice_basis': basis_name,
            'alice_state': alice_state,
            'eve': eve_info,
            'bob_basis': bob_basis_name,
            'bob_bit': int(bob_bit),
            'bases_match': bool(alice_bases[i] == bob_bases[i]),
        })

    # ========================================
    # Step 5: Sifting (keep matching bases)
    # ========================================
    matching_indices = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
    sifted_alice = [int(alice_bits[i]) for i in matching_indices]
    sifted_bob = [int(bob_bits[i]) for i in matching_indices]

    # ========================================
    # Step 6: Error estimation
    # ========================================
    if len(sifted_alice) > 0:
        errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
        error_rate = errors / len(sifted_alice)
    else:
        errors = 0
        error_rate = 0.0

    # Threshold: ~11% QBER indicates eavesdropping
    SECURITY_THRESHOLD = 0.11
    secure = error_rate < SECURITY_THRESHOLD

    # Final key (in practice, additional privacy amplification is applied)
    # Use first half for error checking, second half as key
    n_sifted = len(sifted_alice)
    check_size = max(1, n_sifted // 4)  # Use 25% for verification
    key_bits = sifted_alice[check_size:]

    return {
        'protocol': 'bb84',
        'n_bits': n_bits,
        'eve_present': eve_present,
        'rounds': rounds,
        'sifted_indices': matching_indices,
        'sifted_key_alice': sifted_alice,
        'sifted_key_bob': sifted_bob,
        'n_sifted': n_sifted,
        'errors': errors,
        'error_rate': float(error_rate),
        'security_threshold': SECURITY_THRESHOLD,
        'secure': secure,
        'final_key': key_bits,
        'final_key_length': len(key_bits),
        'summary': (
            f"Exchanged {n_bits} qubits → {n_sifted} sifted bits "
            f"({n_sifted/n_bits*100:.0f}% retention). "
            f"Error rate: {error_rate*100:.1f}%. "
            f"{'🔒 Channel SECURE' if secure else '🚨 EAVESDROPPING DETECTED'}"
            f"{' (Eve was intercepting!)' if eve_present else ''}"
        ),
    }
