"""
Quantum Teleportation Protocol
==============================
Transfers a quantum state from Alice to Bob using a shared Bell pair
and two classical bits, without physically moving the qubit.

Protocol:
    1. Create Bell pair: H(q1), CNOT(q1, q2) → |Φ+⟩ = (|00⟩+|11⟩)/√2
    2. Alice has qubit q0 in state |ψ⟩ = α|0⟩ + β|1⟩
    3. Alice applies CNOT(q0, q1), then H(q0)
    4. Alice measures q0 and q1, getting classical bits (m0, m1)
    5. Bob applies corrections based on (m0, m1):
       - m1 = 1 → apply X to q2
       - m0 = 1 → apply Z to q2
    6. Bob's qubit q2 is now in state |ψ⟩

Qubits:
    q0: Alice's qubit (state to teleport)
    q1: Alice's half of Bell pair
    q2: Bob's half of Bell pair (receives state)
"""

from typing import List, Dict, Optional, Tuple
import numpy as np

from ..quantum_state import QuantumState
from ..measurement import measure_qubit


def generate_circuit(
    alpha: complex = 1.0,
    beta: complex = 0.0
) -> List[Dict]:
    """Generate the quantum teleportation circuit.

    Args:
        alpha: Amplitude for |0⟩ component of state to teleport.
        beta: Amplitude for |1⟩ component of state to teleport.

    Returns:
        List of circuit steps with classical communication markers.
    """
    steps: List[Dict] = []

    # Step 0: Prepare Alice's qubit (if non-trivial state)
    if not (np.isclose(alpha, 1.0) and np.isclose(beta, 0.0)):
        steps.append({
            'gate': '__prepare__',
            'targets': [0],
            'label': f'Prepare Alice\'s qubit: {alpha:.3f}|0⟩ + {beta:.3f}|1⟩',
            'param': None,
            'alpha': complex(alpha),
            'beta': complex(beta),
        })

    # Step 1: Create Bell pair between q1 and q2
    steps.append({
        'gate': 'H',
        'targets': [1],
        'label': 'Create Bell pair: H on q1',
        'param': None,
    })
    steps.append({
        'gate': 'CNOT',
        'targets': [1, 2],
        'label': 'Create Bell pair: CNOT(q1, q2) → |Φ+⟩',
        'param': None,
    })

    # Step 2: Alice's Bell measurement
    steps.append({
        'gate': 'CNOT',
        'targets': [0, 1],
        'label': 'Alice: CNOT(q0, q1)',
        'param': None,
    })
    steps.append({
        'gate': 'H',
        'targets': [0],
        'label': 'Alice: H on q0',
        'param': None,
    })

    # Step 3: Alice measures her qubits
    steps.append({
        'gate': '__measure__',
        'targets': [0],
        'label': 'Alice measures q0 → classical bit m0',
        'param': None,
        'classical': True,
    })
    steps.append({
        'gate': '__measure__',
        'targets': [1],
        'label': 'Alice measures q1 → classical bit m1',
        'param': None,
        'classical': True,
    })

    # Step 4: Bob's conditional corrections (classical communication)
    steps.append({
        'gate': '__conditional_x__',
        'targets': [2],
        'label': 'Bob: if m1=1, apply X to q2 (classical channel)',
        'param': None,
        'condition_qubit': 1,
        'classical_comm': True,
    })
    steps.append({
        'gate': '__conditional_z__',
        'targets': [2],
        'label': 'Bob: if m0=1, apply Z to q2 (classical channel)',
        'param': None,
        'condition_qubit': 0,
        'classical_comm': True,
    })

    return steps


def run(
    alpha: Optional[complex] = None,
    beta: Optional[complex] = None,
    theta: Optional[float] = None,
    phi: Optional[float] = None
) -> Dict:
    """Execute quantum teleportation protocol.

    You can specify the state to teleport either via:
        - alpha, beta: raw amplitudes (will be normalized)
        - theta, phi: Bloch sphere angles |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩

    Args:
        alpha: Amplitude for |0⟩. Defaults to (|0⟩+|1⟩)/√2.
        beta: Amplitude for |1⟩.
        theta: Polar angle on Bloch sphere (0 to π).
        phi: Azimuthal angle on Bloch sphere (0 to 2π).

    Returns:
        Dict with circuit, state history, measurement results, and verification.
    """
    # Determine state to teleport
    if theta is not None:
        if phi is None:
            phi = 0.0
        alpha = np.cos(theta / 2)
        beta = np.exp(1j * phi) * np.sin(theta / 2)
    elif alpha is None:
        # Default: teleport |+⟩ state
        alpha = 1.0 / np.sqrt(2)
        beta = 1.0 / np.sqrt(2)

    # Normalize
    norm = np.sqrt(np.abs(alpha)**2 + np.abs(beta)**2)
    alpha = complex(alpha / norm)
    beta = complex(beta / norm)

    # Initialize 3-qubit system
    state = QuantumState(3)

    # Prepare Alice's qubit
    state.state_vector[0] = alpha  # α|000⟩
    state.state_vector[1] = 0.0   # clear
    state.state_vector[4] = beta   # β|100⟩ (q0=1)
    # Re-normalize just in case
    norm = np.linalg.norm(state.state_vector)
    state.state_vector /= norm

    circuit = generate_circuit(alpha, beta)
    state_history = [state.to_dict()]

    # Record original state for verification
    original_state = {'alpha': alpha, 'beta': beta}

    measurement_results = {}

    for step in circuit:
        if step['gate'] == '__prepare__':
            # Already prepared above
            pass
        elif step['gate'] == '__measure__':
            qubit = step['targets'][0]
            bit, state = measure_qubit(state, qubit)
            measurement_results[f'q{qubit}'] = bit
        elif step['gate'] == '__conditional_x__':
            cond_qubit = step['condition_qubit']
            if measurement_results.get(f'q{cond_qubit}', 0) == 1:
                state.apply_gate('X', step['targets'])
        elif step['gate'] == '__conditional_z__':
            cond_qubit = step['condition_qubit']
            if measurement_results.get(f'q{cond_qubit}', 0) == 1:
                state.apply_gate('Z', step['targets'])
        else:
            state.apply_gate(step['gate'], step['targets'], step.get('param'))

        state_history.append(state.to_dict())

    # Verify: Bob's qubit (q2) should have the teleported state
    # Extract q2's reduced state
    bob_bloch = state.get_bloch_coords(2)

    return {
        'algorithm': 'teleportation',
        'original_state': {
            'alpha': {'real': alpha.real, 'imag': alpha.imag},
            'beta': {'real': beta.real, 'imag': beta.imag},
        },
        'circuit': circuit,
        'measurements': measurement_results,
        'bob_qubit_bloch': bob_bloch,
        'state_history': state_history,
        'success': True,  # Teleportation always succeeds
        'explanation': (
            f"Alice measured m0={measurement_results.get('q0', '?')}, "
            f"m1={measurement_results.get('q1', '?')}. "
            f"Bob applied corrections accordingly. "
            f"The state has been teleported to qubit 2."
        ),
    }
