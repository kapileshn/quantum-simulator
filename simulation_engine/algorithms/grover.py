"""
Grover's Search Algorithm
=========================
Finds a marked item in an unsorted database of N = 2^n items
with O(√N) queries (quadratic speedup over classical O(N)).

Algorithm:
    1. Initialize n qubits to |0⟩⊗n
    2. Apply H to all qubits → uniform superposition
    3. Repeat ⌊π/4 × √(N/M)⌋ times:
       a. Apply oracle (mark target states with phase flip)
       b. Apply diffusion operator (inversion about the mean)
    4. Measure → high probability of target state

Mathematical details:
    Oracle:    Uf|x⟩ = (-1)^f(x)|x⟩ where f(x)=1 for target states
    Diffusion: D = 2|s⟩⟨s| - I, where |s⟩ = H⊗n|0⟩⊗n (uniform superposition)
"""

from typing import List, Dict, Optional, Set
import numpy as np

from ..quantum_state import QuantumState
from ..gates import hadamard


def build_oracle(n_qubits: int, targets: Set[int]) -> np.ndarray:
    """Build the Grover oracle matrix for given target states.

    The oracle applies a phase flip to target states:
        Uf|x⟩ = -|x⟩  if x ∈ targets
        Uf|x⟩ =  |x⟩  otherwise

    Args:
        n_qubits: Number of qubits.
        targets: Set of target state indices to mark.

    Returns:
        2^n × 2^n diagonal oracle matrix.
    """
    dim = 2 ** n_qubits
    oracle = np.eye(dim, dtype=complex)
    for t in targets:
        if 0 <= t < dim:
            oracle[t, t] = -1.0
    return oracle


def build_diffusion(n_qubits: int) -> np.ndarray:
    """Build the Grover diffusion operator.

    D = 2|s⟩⟨s| - I
    where |s⟩ = (1/√N) Σ|x⟩ is the uniform superposition.

    This is equivalent to: H⊗n (2|0⟩⟨0| - I) H⊗n

    Args:
        n_qubits: Number of qubits.

    Returns:
        2^n × 2^n diffusion matrix.
    """
    dim = 2 ** n_qubits
    # |s⟩ = uniform superposition
    s = np.ones(dim, dtype=complex) / np.sqrt(dim)
    # D = 2|s⟩⟨s| - I
    diffusion = 2 * np.outer(s, s.conj()) - np.eye(dim, dtype=complex)
    return diffusion


def optimal_iterations(n_qubits: int, n_targets: int = 1) -> int:
    """Calculate the optimal number of Grover iterations.

    Formula: ⌊π/4 × √(N/M)⌋
    where N = 2^n, M = number of target states.

    Args:
        n_qubits: Number of qubits.
        n_targets: Number of target states.

    Returns:
        Optimal number of iterations.
    """
    N = 2 ** n_qubits
    return max(1, int(np.floor(np.pi / 4 * np.sqrt(N / n_targets))))


def generate_circuit(
    n_qubits: int = 3,
    target_states: Optional[List[int]] = None,
    n_iterations: Optional[int] = None
) -> List[Dict]:
    """Generate Grover's algorithm as step-by-step circuit instructions.

    Args:
        n_qubits: Number of qubits (2 to 5).
        target_states: List of target state indices. Defaults to [0] (|000...0⟩ is a valid but trivial target).
        n_iterations: Number of Grover iterations. Defaults to optimal.

    Returns:
        List of circuit steps.
    """
    if not 2 <= n_qubits <= 5:
        raise ValueError(f"n_qubits must be 2-5, got {n_qubits}")

    if target_states is None:
        target_states = [2 ** n_qubits - 1]  # Default: search for |11...1⟩

    target_set = set(target_states)

    if n_iterations is None:
        n_iterations = optimal_iterations(n_qubits, len(target_set))

    steps: List[Dict] = []

    # Step 1: Apply H to all qubits
    for i in range(n_qubits):
        steps.append({
            'gate': 'H',
            'targets': [i],
            'label': f'Apply H to qubit {i} (uniform superposition)',
            'param': None,
        })

    # Steps 2-3: Grover iterations
    for iteration in range(n_iterations):
        # Oracle
        steps.append({
            'gate': '__oracle__',
            'targets': list(range(n_qubits)),
            'label': f'Grover iteration {iteration + 1}/{n_iterations}: Apply oracle',
            'param': None,
            'oracle_targets': list(target_set),
        })

        # Diffusion
        steps.append({
            'gate': '__diffusion__',
            'targets': list(range(n_qubits)),
            'label': f'Grover iteration {iteration + 1}/{n_iterations}: Apply diffusion',
            'param': None,
        })

    # Step 4: Measure all qubits
    for i in range(n_qubits):
        steps.append({
            'gate': '__measure__',
            'targets': [i],
            'label': f'Measure qubit {i}',
            'param': None,
        })

    return steps


def run(
    n_qubits: int = 3,
    target_states: Optional[List[int]] = None,
    n_iterations: Optional[int] = None
) -> Dict:
    """Execute Grover's search algorithm.

    Args:
        n_qubits: Number of qubits (2-5).
        target_states: Target state indices to search for.
        n_iterations: Override for iteration count.

    Returns:
        Dict with circuit, results, state history, and success probability.
    """
    if target_states is None:
        target_states = [2 ** n_qubits - 1]

    target_set = set(target_states)

    if n_iterations is None:
        n_iterations = optimal_iterations(n_qubits, len(target_set))

    state = QuantumState(n_qubits)
    circuit = generate_circuit(n_qubits, target_states, n_iterations)
    state_history = [state.to_dict()]

    oracle_matrix = build_oracle(n_qubits, target_set)
    diffusion_matrix = build_diffusion(n_qubits)

    measured_bits = {}

    for step in circuit:
        if step['gate'] == '__oracle__':
            state.apply_gate_matrix(oracle_matrix, step['targets'])
        elif step['gate'] == '__diffusion__':
            state.apply_gate_matrix(diffusion_matrix, step['targets'])
        elif step['gate'] == '__measure__':
            from ..measurement import measure_qubit
            bit, state = measure_qubit(state, step['targets'][0])
            measured_bits[step['targets'][0]] = bit
        else:
            state.apply_gate(step['gate'], step['targets'], step.get('param'))

        state_history.append(state.to_dict())

    measurement = ''.join(str(measured_bits.get(i, 0)) for i in range(n_qubits))
    measured_int = int(measurement, 2)
    success = measured_int in target_set

    # Calculate theoretical success probability before measurement
    pre_measure_probs = state_history[-n_qubits - 1].get('probabilities', {})
    target_labels = [format(t, f'0{n_qubits}b') for t in target_set]
    success_prob = sum(pre_measure_probs.get(label, 0) for label in target_labels)

    return {
        'algorithm': 'grover',
        'n_qubits': n_qubits,
        'target_states': sorted(target_set),
        'target_labels': sorted(target_labels),
        'n_iterations': n_iterations,
        'optimal_iterations': optimal_iterations(n_qubits, len(target_set)),
        'circuit': circuit,
        'measurement': measurement,
        'success': success,
        'success_probability': success_prob,
        'state_history': state_history,
    }
