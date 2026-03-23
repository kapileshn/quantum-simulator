"""
Quantum State Management
========================
Core statevector simulation for up to 5 qubits (2^5 = 32 amplitudes).

Mathematical foundation:
    Qubit state:       |ψ⟩ = α|0⟩ + β|1⟩,  where |α|² + |β|² = 1
    Multi-qubit state: |ψ⟩ = Σᵢ cᵢ|i⟩
    Gate operation:    |ψ'⟩ = U|ψ⟩  (U is unitary)
    Measurement prob:  P(i) = |⟨i|ψ⟩|²

The state vector uses big-endian qubit ordering:
    |q₀ q₁ ... qₙ₋₁⟩ where q₀ is the most significant bit.
"""

from typing import List, Tuple, Optional, Dict
import numpy as np
from copy import deepcopy

from .gates import expand_gate, validate_gate_placement, get_gate_matrix


MAX_QUBITS = 5


class QuantumState:
    """Manages a quantum statevector for n-qubit systems.

    Attributes:
        n_qubits: Number of qubits in the system.
        state_vector: Complex numpy array of shape (2^n,).
        classical_bits: Dictionary mapping qubit index to measured classical value.

    Example:
        >>> qs = QuantumState(2)               # |00⟩
        >>> qs.apply_gate("H", [0])            # H ⊗ I → |+0⟩
        >>> qs.apply_gate("CNOT", [0, 1])      # Bell state |Φ+⟩
        >>> probs = qs.get_probabilities()      # {0: 0.5, 3: 0.5}
    """

    def __init__(self, n_qubits: int) -> None:
        """Initialize quantum state to |00...0⟩.

        Args:
            n_qubits: Number of qubits (1 to MAX_QUBITS).

        Raises:
            ValueError: If n_qubits is out of range.
        """
        if not 1 <= n_qubits <= MAX_QUBITS:
            raise ValueError(
                f"n_qubits must be between 1 and {MAX_QUBITS}, got {n_qubits}."
            )

        self.n_qubits: int = n_qubits
        self._dim: int = 2 ** n_qubits
        self.state_vector: np.ndarray = np.zeros(self._dim, dtype=complex)
        self.state_vector[0] = 1.0  # |00...0⟩
        self.classical_bits: Dict[int, int] = {}

    @property
    def dim(self) -> int:
        """Dimension of the Hilbert space (2^n)."""
        return self._dim

    def reset(self) -> None:
        """Reset state to |00...0⟩ and clear classical bits."""
        self.state_vector = np.zeros(self._dim, dtype=complex)
        self.state_vector[0] = 1.0
        self.classical_bits.clear()

    def set_state(self, amplitudes: np.ndarray) -> None:
        """Set the state vector to a custom state.

        Args:
            amplitudes: Complex array of shape (2^n,). Must be normalized.

        Raises:
            ValueError: If shape is wrong or state isn't normalized.
        """
        amplitudes = np.asarray(amplitudes, dtype=complex)
        if amplitudes.shape != (self._dim,):
            raise ValueError(
                f"Expected state vector of shape ({self._dim},), "
                f"got {amplitudes.shape}."
            )

        norm = np.sum(np.abs(amplitudes) ** 2)
        if not np.isclose(norm, 1.0, atol=1e-10):
            raise ValueError(
                f"State vector must be normalized (|α|² + |β|² = 1). "
                f"Got norm² = {norm:.10f}."
            )

        self.state_vector = amplitudes.copy()

    def apply_gate(
        self,
        gate_name: str,
        target_qubits: List[int],
        param: Optional[float] = None
    ) -> None:
        """Apply a named gate to the state vector.

        Implements |ψ'⟩ = U|ψ⟩ where U is the full-system unitary.

        Args:
            gate_name: Name of the gate (from GATE_REGISTRY).
            target_qubits: Qubit indices the gate acts on.
            param: Optional parameter for parameterized gates.

        Raises:
            ValueError: If gate placement is invalid.
        """
        is_valid, error = validate_gate_placement(
            gate_name, target_qubits, self.n_qubits
        )
        if not is_valid:
            raise ValueError(error)

        gate_matrix = get_gate_matrix(gate_name, param)
        full_matrix = expand_gate(gate_matrix, target_qubits, self.n_qubits)

        self.state_vector = full_matrix @ self.state_vector

        # Renormalize to combat floating-point drift
        norm = np.linalg.norm(self.state_vector)
        if norm > 0:
            self.state_vector /= norm

    def apply_gate_matrix(
        self,
        gate_matrix: np.ndarray,
        target_qubits: List[int]
    ) -> None:
        """Apply a raw matrix gate to the state vector.

        Used for custom/algorithm-generated gates (e.g., oracles).

        Args:
            gate_matrix: Unitary matrix for the gate.
            target_qubits: Qubit indices the gate acts on.

        Raises:
            ValueError: If matrix dimensions don't match target qubits.
        """
        full_matrix = expand_gate(gate_matrix, target_qubits, self.n_qubits)
        self.state_vector = full_matrix @ self.state_vector

        norm = np.linalg.norm(self.state_vector)
        if norm > 0:
            self.state_vector /= norm

    def get_probabilities(self) -> Dict[int, float]:
        """Calculate measurement probabilities for all basis states.

        Implements P(i) = |⟨i|ψ⟩|² = |cᵢ|²

        Returns:
            Dictionary mapping basis state index to probability.
            Only includes states with P > 1e-14.
        """
        probs = np.abs(self.state_vector) ** 2
        return {
            i: float(p)
            for i, p in enumerate(probs)
            if p > 1e-14
        }

    def get_probability_array(self) -> np.ndarray:
        """Get probability array for all basis states.

        Returns:
            Array of shape (2^n,) with probabilities.
        """
        return np.abs(self.state_vector) ** 2

    def get_amplitudes(self) -> List[Dict]:
        """Get complex amplitudes with basis state labels.

        Returns:
            List of dicts with keys:
                - 'index': basis state integer
                - 'label': binary string label (e.g., '|01⟩')
                - 'amplitude': complex number
                - 'real': real part
                - 'imag': imaginary part
                - 'magnitude': |amplitude|
                - 'phase': angle in radians
                - 'probability': |amplitude|²
        """
        result = []
        for i, amp in enumerate(self.state_vector):
            label = format(i, f'0{self.n_qubits}b')
            prob = float(np.abs(amp) ** 2)
            result.append({
                'index': i,
                'label': f'|{label}⟩',
                'real': float(amp.real),
                'imag': float(amp.imag),
                'magnitude': float(np.abs(amp)),
                'phase': float(np.angle(amp)),
                'probability': prob,
            })
        return result

    def get_bloch_coords(self, qubit_index: int) -> Dict[str, float]:
        """Get Bloch sphere coordinates for a single qubit.

        For single-qubit systems, uses the state directly.
        For multi-qubit systems, computes the reduced density matrix
        via partial trace and extracts the Bloch vector.

        Bloch vector: (x, y, z) where:
            x = 2·Re(ρ₀₁)
            y = 2·Im(ρ₀₁)   (note: actually -2·Im(ρ₀₁) for standard convention)
            z = ρ₀₀ - ρ₁₁

        Args:
            qubit_index: Index of the qubit to visualize.

        Returns:
            Dict with keys 'x', 'y', 'z' (Bloch vector components)
            and 'theta', 'phi' (spherical coordinates).

        Raises:
            ValueError: If qubit_index is out of range.
        """
        if qubit_index < 0 or qubit_index >= self.n_qubits:
            raise ValueError(
                f"Qubit index {qubit_index} out of range for "
                f"{self.n_qubits}-qubit system."
            )

        rho = self._reduced_density_matrix(qubit_index)

        # Bloch vector from density matrix
        x = float(2 * rho[0, 1].real)
        y = float(-2 * rho[0, 1].imag)
        z = float(rho[0, 0].real - rho[1, 1].real)

        # Spherical coordinates
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = float(np.arccos(np.clip(z / max(r, 1e-10), -1, 1)))
        phi = float(np.arctan2(y, x))

        return {
            'x': x, 'y': y, 'z': z,
            'theta': theta, 'phi': phi,
            'purity': float(r),  # 1.0 for pure, < 1.0 for mixed
        }

    def _reduced_density_matrix(self, qubit_index: int) -> np.ndarray:
        """Compute the reduced density matrix for a single qubit by partial trace.

        For state |ψ⟩, the full density matrix is ρ = |ψ⟩⟨ψ|.
        The reduced density matrix ρ_A = Tr_B(ρ) traces over all
        qubits except the target.

        Args:
            qubit_index: The qubit to keep.

        Returns:
            2x2 complex density matrix for the specified qubit.
        """
        # Reshape state vector: separate target qubit from rest
        # Total state: 2^n amplitudes
        n = self.n_qubits
        sv = self.state_vector.reshape([2] * n)

        # Full density matrix in tensor form
        rho_full = np.outer(self.state_vector, self.state_vector.conj())
        rho_tensor = rho_full.reshape([2] * (2 * n))

        # Trace over all qubits except qubit_index
        # For axes: first n are "ket" indices, last n are "bra" indices
        # We need to trace (contract) axis i with axis n+i for all i != qubit_index
        axes_to_trace = []
        for i in range(n):
            if i != qubit_index:
                axes_to_trace.append(i)

        # Perform partial trace by iteratively contracting pairs
        # We'll use a simpler approach: sum over computational basis of other qubits
        rho_reduced = np.zeros((2, 2), dtype=complex)

        n_other = n - 1
        for other_state in range(2 ** n_other):
            # Build index into full state vector for both ket and bra
            for a in range(2):  # target qubit ket
                # Build full index with target qubit = a
                idx_a = self._build_index(qubit_index, a, other_state)
                for b in range(2):  # target qubit bra
                    idx_b = self._build_index(qubit_index, b, other_state)
                    rho_reduced[a, b] += (
                        self.state_vector[idx_a] *
                        self.state_vector[idx_b].conj()
                    )

        return rho_reduced

    def _build_index(
        self, target_qubit: int, target_val: int, other_state: int
    ) -> int:
        """Build a full basis state index from target qubit value and other qubits' state.

        Args:
            target_qubit: Index of the target qubit.
            target_val: Value of the target qubit (0 or 1).
            other_state: Integer encoding the state of all other qubits.

        Returns:
            Full basis state index.
        """
        n = self.n_qubits
        bits = []
        other_idx = 0
        for q in range(n):
            if q == target_qubit:
                bits.append(target_val)
            else:
                # Extract bit from other_state
                bit_pos = (n - 2) - other_idx  # big-endian within other qubits
                bit_val = (other_state >> bit_pos) & 1 if bit_pos >= 0 else 0
                bits.append(bit_val)
                other_idx += 1

        # Convert bits to index (big-endian)
        index = 0
        for q, b in enumerate(bits):
            index |= (b << (n - 1 - q))
        return index

    def copy(self) -> 'QuantumState':
        """Create a deep copy of this quantum state.

        Useful for step-by-step execution history.

        Returns:
            New QuantumState with identical state vector and classical bits.
        """
        new_state = QuantumState.__new__(QuantumState)
        new_state.n_qubits = self.n_qubits
        new_state._dim = self._dim
        new_state.state_vector = self.state_vector.copy()
        new_state.classical_bits = self.classical_bits.copy()
        return new_state

    def to_dict(self) -> Dict:
        """Serialize state to a JSON-compatible dictionary.

        Returns:
            Dictionary with all state information for WebSocket transmission.
        """
        return {
            'n_qubits': self.n_qubits,
            'amplitudes': self.get_amplitudes(),
            'probabilities': {
                format(k, f'0{self.n_qubits}b'): v
                for k, v in self.get_probabilities().items()
            },
            'bloch_coords': [
                self.get_bloch_coords(i) for i in range(self.n_qubits)
            ],
            'classical_bits': self.classical_bits,
        }

    def __repr__(self) -> str:
        """String representation showing non-zero amplitudes."""
        terms = []
        for i, amp in enumerate(self.state_vector):
            if np.abs(amp) > 1e-10:
                label = format(i, f'0{self.n_qubits}b')
                if np.isclose(amp.imag, 0):
                    terms.append(f"{amp.real:+.4f}|{label}⟩")
                else:
                    terms.append(f"({amp:.4f})|{label}⟩")
        return " ".join(terms) if terms else "|vacuum⟩"
