"""
Deutsch's Algorithm
===================
Determines whether a 1-bit function f: {0,1} → {0,1} is constant or balanced 
in a single query.

Algorithm (1 input qubit + 1 ancilla):
    1. Initialize to |0⟩|0⟩
    2. Apply X to qubit 1 (ancilla) -> |0⟩|1⟩
    3. Apply H to both -> |+⟩|−⟩
    4. Apply oracle Uf
    5. Apply H to qubit 0
    6. Measure qubit 0:
       - 0 -> constant
       - 1 -> balanced

Function Cases (IBM Course):
    1. f(x) = 0 (Constant)
    2. f(x) = x (Balanced - Identity)
    3. f(x) = 1-x (Balanced - NOT)
    4. f(x) = 1 (Constant)
"""

from typing import List, Dict, Optional
import numpy as np

from ..quantum_state import QuantumState


def deutsch_function(case: int) -> List[Dict]:
    """Generates the gate sequence for the oracle in Deutsch's algorithm.

    Cases:
        1: f(x) = 0 (Constant) -> No gates (Identity)
        2: f(x) = x (Balanced) -> CNOT(0, 1)
        3: f(x) = 1-x (Balanced) -> CNOT(0, 1) then X(1)
        4: f(x) = 1 (Constant) -> X(1)

    Args:
        case: Function case index (1-4).

    Returns:
        List of gate operation dicts.
    """
    if case not in [1, 2, 3, 4]:
        raise ValueError("case must be 1, 2, 3, or 4")

    ops = []
    if case in [2, 3]:
        # f.cx(0, 1)
        ops.append({
            'gate': 'CNOT',
            'targets': [0, 1],
            'label': 'Oracle: CNOT(0, 1)'
        })
    if case in [3, 4]:
        # f.x(1)
        ops.append({
            'gate': 'X',
            'targets': [1],
            'label': 'Oracle: X(1)'
        })
    return ops


def generate_circuit(case: int = 1) -> List[Dict]:
    """Generate the step-by-step circuit for Deutsch's algorithm.

    Args:
        case: Function case index (1-4).

    Returns:
        List of step dicts compatible with the simulator interface.
    """
    steps = []

    # Step 1: Initialize ancilla to |1⟩
    steps.append({
        'gate': 'X',
        'targets': [1],
        'label': 'Initialize ancilla qubit 1 to |1⟩'
    })

    # Step 2: Apply Hadamard to all qubits
    steps.append({
        'gate': 'H',
        'targets': [0],
        'label': 'Apply H to input qubit 0 (create superposition)'
    })
    steps.append({
        'gate': 'H',
        'targets': [1],
        'label': 'Apply H to ancilla qubit 1 (create |−⟩ state)'
    })

    # Step 3: Apply Oracle (Expanded as Gates)
    oracle_ops = deutsch_function(case)
    steps.extend(oracle_ops)

    # Step 4: Apply H to input qubit
    steps.append({
        'gate': 'H',
        'targets': [0],
        'label': 'Apply H to input qubit 0 (Interference)'
    })

    # Step 5: Measure input qubit
    steps.append({
        'gate': '__measure__',
        'targets': [0],
        'label': 'Measure input qubit 0'
    })

    return steps


def run(case: int = 1) -> Dict:
    """Execute Deutsch's algorithm simulation.

    Args:
        case: Function case index (1-4).

    Returns:
        Dict with algorithm name, case, circuit, result, and history.
    """
    n_total = 2
    state = QuantumState(n_total)
    circuit = generate_circuit(case)
    state_history = [state.to_dict()]

    measured_bits = {}

    for step in circuit:
        if step['gate'] == '__measure__':
            from ..measurement import measure_qubit
            bit, state = measure_qubit(state, step['targets'][0])
            measured_bits[step['targets'][0]] = bit
        else:
            state.apply_gate(step['gate'], step['targets'], step.get('param'))
        
        state_history.append(state.to_dict())

    # Determine result: input qubit measured 0 -> constant, 1 -> balanced
    # For cases 2,3 (balanced), probability is 100% for state |1>
    # For cases 1,4 (constant), probability is 100% for state |0>
    input_measurement = measured_bits.get(0, 0)
    
    # In Deutsch, if measured bit is 0 -> Constant, 1 -> Balanced
    is_constant = (input_measurement == 0)

    case_names = {
        1: "Constant 0",
        2: "Balanced (Identity)",
        3: "Balanced (NOT)",
        4: "Constant 1"
    }

    return {
        'algorithm': 'deutsch',
        'case': case,
        'case_name': case_names.get(case, "Unknown"),
        'circuit': circuit,
        'result': 'constant' if is_constant else 'balanced',
        'measurement': str(input_measurement),
        'state_history': state_history,
    }
