"""
Unit Tests: Quantum Gates
=========================
Verifies mathematical correctness of all gate implementations.

Tests:
    - Unitarity: U†U = I for all gates
    - Known identities: HXH = Z, H² = I, X² = I, etc.
    - Gate dimensions
    - Gate expansion to multi-qubit systems
    - Gate validation logic
"""

import numpy as np
import pytest
from simulation_engine.gates import (
    identity, pauli_x, pauli_y, pauli_z, hadamard,
    s_gate, s_dagger, t_gate, t_dagger,
    phase_gate, rx, ry, rz,
    cnot, cz, swap, toffoli,
    get_gate_matrix, validate_gate_placement, expand_gate,
    GATE_REGISTRY,
)


class TestSingleQubitGates:
    """Tests for all single-qubit gate matrices."""

    @pytest.mark.parametrize("gate_func", [
        identity, pauli_x, pauli_y, pauli_z, hadamard,
        s_gate, s_dagger, t_gate, t_dagger,
    ])
    def test_unitarity(self, gate_func):
        """All gates must satisfy U†U = I (unitarity)."""
        U = gate_func()
        product = U.conj().T @ U
        np.testing.assert_allclose(product, np.eye(2), atol=1e-12,
                                   err_msg=f"{gate_func.__name__} is not unitary")

    @pytest.mark.parametrize("gate_func", [
        identity, pauli_x, pauli_y, pauli_z, hadamard,
        s_gate, s_dagger, t_gate, t_dagger,
    ])
    def test_shape(self, gate_func):
        """All single-qubit gates must be 2x2."""
        assert gate_func().shape == (2, 2)

    def test_pauli_x_action(self):
        """X|0⟩ = |1⟩, X|1⟩ = |0⟩."""
        X = pauli_x()
        ket_0 = np.array([1, 0], dtype=complex)
        ket_1 = np.array([0, 1], dtype=complex)
        np.testing.assert_allclose(X @ ket_0, ket_1)
        np.testing.assert_allclose(X @ ket_1, ket_0)

    def test_hadamard_action(self):
        """H|0⟩ = |+⟩, H|1⟩ = |−⟩."""
        H = hadamard()
        ket_0 = np.array([1, 0], dtype=complex)
        ket_plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(H @ ket_0, ket_plus, atol=1e-12)

    def test_x_squared_is_identity(self):
        """X² = I."""
        X = pauli_x()
        np.testing.assert_allclose(X @ X, np.eye(2), atol=1e-12)

    def test_h_squared_is_identity(self):
        """H² = I."""
        H = hadamard()
        np.testing.assert_allclose(H @ H, np.eye(2), atol=1e-12)

    def test_hxh_is_z(self):
        """HXH = Z."""
        H = hadamard()
        X = pauli_x()
        Z = pauli_z()
        np.testing.assert_allclose(H @ X @ H, Z, atol=1e-12)

    def test_hzh_is_x(self):
        """HZH = X."""
        H = hadamard()
        X = pauli_x()
        Z = pauli_z()
        np.testing.assert_allclose(H @ Z @ H, X, atol=1e-12)

    def test_sdag_s_is_identity(self):
        """S†S = I."""
        S = s_gate()
        Sd = s_dagger()
        np.testing.assert_allclose(Sd @ S, np.eye(2), atol=1e-12)

    def test_tdag_t_is_identity(self):
        """T†T = I."""
        T = t_gate()
        Td = t_dagger()
        np.testing.assert_allclose(Td @ T, np.eye(2), atol=1e-12)

    def test_s_squared_is_z(self):
        """S² = Z."""
        S = s_gate()
        Z = pauli_z()
        np.testing.assert_allclose(S @ S, Z, atol=1e-12)

    def test_pauli_anticommutation(self):
        """Pauli matrices anticommute: {σᵢ, σⱼ} = 2δᵢⱼI."""
        X, Y, Z = pauli_x(), pauli_y(), pauli_z()
        # XY + YX = 0
        np.testing.assert_allclose(X @ Y + Y @ X, np.zeros((2, 2)), atol=1e-12)
        # XZ + ZX = 0
        np.testing.assert_allclose(X @ Z + Z @ X, np.zeros((2, 2)), atol=1e-12)
        # YZ + ZY = 0
        np.testing.assert_allclose(Y @ Z + Z @ Y, np.zeros((2, 2)), atol=1e-12)


class TestParameterizedGates:
    """Tests for parameterized rotation gates."""

    @pytest.mark.parametrize("theta", [0, np.pi/4, np.pi/2, np.pi, 2*np.pi])
    def test_rx_unitarity(self, theta):
        """Rx(θ) is unitary for all θ."""
        U = rx(theta)
        np.testing.assert_allclose(U.conj().T @ U, np.eye(2), atol=1e-12)

    @pytest.mark.parametrize("theta", [0, np.pi/4, np.pi/2, np.pi, 2*np.pi])
    def test_ry_unitarity(self, theta):
        """Ry(θ) is unitary for all θ."""
        U = ry(theta)
        np.testing.assert_allclose(U.conj().T @ U, np.eye(2), atol=1e-12)

    @pytest.mark.parametrize("theta", [0, np.pi/4, np.pi/2, np.pi, 2*np.pi])
    def test_rz_unitarity(self, theta):
        """Rz(θ) is unitary for all θ."""
        U = rz(theta)
        np.testing.assert_allclose(U.conj().T @ U, np.eye(2), atol=1e-12)

    def test_rx_pi_is_neg_i_x(self):
        """Rx(π) = -iX (up to global phase)."""
        U = rx(np.pi)
        expected = -1j * pauli_x()
        np.testing.assert_allclose(U, expected, atol=1e-12)

    def test_phase_at_pi_half_is_s(self):
        """P(π/2) = S."""
        np.testing.assert_allclose(phase_gate(np.pi/2), s_gate(), atol=1e-12)

    def test_phase_at_pi_quarter_is_t(self):
        """P(π/4) = T."""
        np.testing.assert_allclose(phase_gate(np.pi/4), t_gate(), atol=1e-12)


class TestMultiQubitGates:
    """Tests for multi-qubit gate matrices."""

    def test_cnot_unitarity(self):
        """CNOT is unitary."""
        U = cnot()
        np.testing.assert_allclose(U.conj().T @ U, np.eye(4), atol=1e-12)

    def test_cnot_shape(self):
        """CNOT is 4x4."""
        assert cnot().shape == (4, 4)

    def test_cnot_action(self):
        """CNOT: |10⟩ → |11⟩, |11⟩ → |10⟩."""
        C = cnot()
        ket_10 = np.array([0, 0, 1, 0], dtype=complex)
        ket_11 = np.array([0, 0, 0, 1], dtype=complex)
        np.testing.assert_allclose(C @ ket_10, ket_11)
        np.testing.assert_allclose(C @ ket_11, ket_10)

    def test_swap_action(self):
        """SWAP: |01⟩ → |10⟩."""
        S = swap()
        ket_01 = np.array([0, 1, 0, 0], dtype=complex)
        ket_10 = np.array([0, 0, 1, 0], dtype=complex)
        np.testing.assert_allclose(S @ ket_01, ket_10)

    def test_swap_unitarity(self):
        S = swap()
        np.testing.assert_allclose(S.conj().T @ S, np.eye(4), atol=1e-12)

    def test_cz_unitarity(self):
        U = cz()
        np.testing.assert_allclose(U.conj().T @ U, np.eye(4), atol=1e-12)

    def test_toffoli_unitarity(self):
        """Toffoli is unitary."""
        U = toffoli()
        np.testing.assert_allclose(U.conj().T @ U, np.eye(8), atol=1e-12)

    def test_toffoli_shape(self):
        assert toffoli().shape == (8, 8)

    def test_toffoli_action(self):
        """Toffoli: |110⟩ → |111⟩."""
        T = toffoli()
        ket_110 = np.zeros(8, dtype=complex)
        ket_110[6] = 1.0  # |110⟩ = index 6
        ket_111 = np.zeros(8, dtype=complex)
        ket_111[7] = 1.0  # |111⟩ = index 7
        np.testing.assert_allclose(T @ ket_110, ket_111)


class TestGateRegistry:
    """Tests for the gate registry and utility functions."""

    def test_all_gates_registered(self):
        """Check all expected gates are in the registry."""
        expected = {'I', 'X', 'Y', 'Z', 'H', 'S', 'S†', 'T', 'T†',
                    'P', 'Rx', 'Ry', 'Rz', 'CNOT', 'CZ', 'SWAP', 'CCX'}
        assert set(GATE_REGISTRY.keys()) == expected

    def test_get_gate_matrix_basic(self):
        """get_gate_matrix returns correct matrices."""
        np.testing.assert_allclose(get_gate_matrix('X'), pauli_x())
        np.testing.assert_allclose(get_gate_matrix('H'), hadamard())

    def test_get_gate_matrix_parametric(self):
        """get_gate_matrix handles parameters correctly."""
        result = get_gate_matrix('Rx', np.pi)
        expected = rx(np.pi)
        np.testing.assert_allclose(result, expected, atol=1e-12)

    def test_get_gate_matrix_missing_param(self):
        """get_gate_matrix raises ValueError for missing parameter."""
        with pytest.raises(ValueError, match="requires parameter"):
            get_gate_matrix('Rx')

    def test_get_gate_matrix_unexpected_param(self):
        """get_gate_matrix raises ValueError for unexpected parameter."""
        with pytest.raises(ValueError, match="does not accept"):
            get_gate_matrix('X', 1.0)

    def test_get_gate_matrix_unknown(self):
        """get_gate_matrix raises ValueError for unknown gate."""
        with pytest.raises(ValueError, match="Unknown gate"):
            get_gate_matrix('UNKNOWN_GATE')


class TestGateValidation:
    """Tests for gate placement validation."""

    def test_valid_single_qubit(self):
        valid, msg = validate_gate_placement('H', [0], 3)
        assert valid
        assert msg == ''

    def test_valid_two_qubit(self):
        valid, msg = validate_gate_placement('CNOT', [0, 1], 3)
        assert valid

    def test_invalid_too_few_targets(self):
        valid, msg = validate_gate_placement('CNOT', [0], 3)
        assert not valid
        assert 'requires 2' in msg

    def test_invalid_out_of_bounds(self):
        valid, msg = validate_gate_placement('H', [5], 3)
        assert not valid
        assert 'out of bounds' in msg

    def test_invalid_duplicate_targets(self):
        valid, msg = validate_gate_placement('CNOT', [1, 1], 3)
        assert not valid
        assert 'Duplicate' in msg

    def test_invalid_unknown_gate(self):
        valid, msg = validate_gate_placement('FAKE', [0], 2)
        assert not valid


class TestGateExpansion:
    """Tests for expanding gates to full Hilbert space."""

    def test_single_qubit_on_first(self):
        """X on qubit 0 of 2-qubit system: X⊗I."""
        X = pauli_x()
        full = expand_gate(X, [0], 2)
        expected = np.kron(X, np.eye(2))
        np.testing.assert_allclose(full, expected, atol=1e-12)

    def test_single_qubit_on_second(self):
        """X on qubit 1 of 2-qubit system: I⊗X."""
        X = pauli_x()
        full = expand_gate(X, [1], 2)
        expected = np.kron(np.eye(2), X)
        np.testing.assert_allclose(full, expected, atol=1e-12)

    def test_cnot_natural_order(self):
        """CNOT on qubits [0,1] of 2-qubit system (natural order)."""
        C = cnot()
        full = expand_gate(C, [0, 1], 2)
        np.testing.assert_allclose(full, C, atol=1e-12)

    def test_expanded_gate_is_unitary(self):
        """Expanded gate preserves unitarity."""
        H = hadamard()
        full = expand_gate(H, [1], 3)
        np.testing.assert_allclose(
            full.conj().T @ full, np.eye(8), atol=1e-12
        )

    def test_bell_state_creation(self):
        """H on q0 + CNOT(0,1) creates Bell state |Φ+⟩."""
        H = hadamard()
        C = cnot()

        state = np.array([1, 0, 0, 0], dtype=complex)  # |00⟩

        H_full = expand_gate(H, [0], 2)
        state = H_full @ state  # |+0⟩

        C_full = expand_gate(C, [0, 1], 2)
        state = C_full @ state  # Bell state |Φ+⟩

        expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(state, expected, atol=1e-12)
