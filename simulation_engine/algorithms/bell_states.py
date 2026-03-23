"""
The Four Bell States
====================
Generates one of the four maximally entangled two-qubit Bell states.

|Φ⁺⟩ = (|00⟩ + |11⟩) / √2
|Φ⁻⟩ = (|00⟩ - |11⟩) / √2
|Ψ⁺⟩ = (|01⟩ + |10⟩) / √2
|Ψ⁻⟩ = (|01⟩ - |10⟩) / √2
"""

from typing import Dict, List
from ..quantum_state import QuantumState

def generate_circuit(state_type: str = 'Phi+') -> List[Dict]:
    """Generate the circuit for the requested Bell state."""
    steps = []
    
    # Setup initial state to control which Bell State is produced
    if state_type in ['Phi-', 'Psi-']:
        steps.append({'gate': 'X', 'targets': [0], 'label': 'Initial X on q0'})
    
    if state_type in ['Psi+', 'Psi-']:
        steps.append({'gate': 'X', 'targets': [1], 'label': 'Initial X on q1'})
        
    steps.append({'gate': 'H', 'targets': [0], 'label': 'Superposition on q0'})
    steps.append({'gate': 'CNOT', 'targets': [0, 1], 'label': 'Entangle q0 and q1'})
    
    return steps


def run(state_type: str = 'Phi+') -> Dict:
    """Execute the Bell State generator."""
    valid_states = ['Phi+', 'Phi-', 'Psi+', 'Psi-']
    if state_type not in valid_states:
        raise ValueError(f"state_type must be one of {valid_states}")

    circuit = generate_circuit(state_type)
    state = QuantumState(2)  # Bell states always use 2 qubits
    state_history = [state.to_dict()]
    
    for step in circuit:
        gate = step['gate']
        targets = step['targets']
        state.apply_gate(gate, targets)
        state_history.append(state.to_dict())
        
    # Unicode representation for the summary
    state_map = {
        'Phi+': '|Φ⁺⟩ = (|00⟩ + |11⟩) / √2',
        'Phi-': '|Φ⁻⟩ = (|00⟩ - |11⟩) / √2',
        'Psi+': '|Ψ⁺⟩ = (|01⟩ + |10⟩) / √2',
        'Psi-': '|Ψ⁻⟩ = (|01⟩ - |10⟩) / √2',
    }
        
    return {
        'algorithm': 'bell_states',
        'state_type': state_type,
        'circuit': circuit,
        'state_history': state_history,
        'summary': (
            f"Generated Bell State: {state_type}\n"
            f"Formula: {state_map[state_type]}\n"
            f"Properties: Orthonormal, Maximally entangled, Cannot be separated."
        ),
    }
