"""
Unit Tests: Quantum State
=========================
Tests for QuantumState class: initialization, gate application,
measurement probabilities, Bloch sphere coordinates, and serialization.
"""

import numpy as np
import pytest
from simulation_engine.quantum_state import QuantumState


class TestInitialization:
    """Tests for QuantumState initialization."""

    def test_single_qubit_init(self):
        """1-qubit state initializes to |0⟩."""
        qs = QuantumState(1)
        np.testing.assert_allclose(qs.state_vector, [1, 0])

    def test_two_qubit_init(self):
        """2-qubit state initializes to |00⟩."""
        qs = QuantumState(2)
        expected = np.zeros(4, dtype=complex)
        expected[0] = 1.0
        np.testing.assert_allclose(qs.state_vector, expected)

    def test_five_qubit_init(self):
        """5-qubit state has 32 amplitudes, all zero except |00000⟩."""
        qs = QuantumState(5)
        assert len(qs.state_vector) == 32
        assert qs.state_vector[0] == 1.0
        assert np.sum(np.abs(qs.state_vector[1:]) ** 2) == 0.0

    def test_invalid_qubit_count(self):
        """Reject n_qubits < 1 or > 5."""
        with pytest.raises(ValueError):
            QuantumState(0)
        with pytest.raises(ValueError):
            QuantumState(6)

    def test_dim_property(self):
        """dim = 2^n."""
        assert QuantumState(1).dim == 2
        assert QuantumState(3).dim == 8
        assert QuantumState(5).dim == 32


class TestGateApplication:
    """Tests for applying gates to quantum states."""

    def test_x_flips_zero(self):
        """X|0⟩ = |1⟩."""
        qs = QuantumState(1)
        qs.apply_gate('X', [0])
        np.testing.assert_allclose(qs.state_vector, [0, 1], atol=1e-12)

    def test_h_creates_superposition(self):
        """H|0⟩ = |+⟩ = (|0⟩+|1⟩)/√2."""
        qs = QuantumState(1)
        qs.apply_gate('H', [0])
        expected = np.array([1, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(qs.state_vector, expected, atol=1e-12)

    def test_double_x_is_identity(self):
        """XX|0⟩ = |0⟩."""
        qs = QuantumState(1)
        qs.apply_gate('X', [0])
        qs.apply_gate('X', [0])
        np.testing.assert_allclose(qs.state_vector, [1, 0], atol=1e-12)

    def test_bell_state(self):
        """H on q0, CNOT(0,1) creates Bell state."""
        qs = QuantumState(2)
        qs.apply_gate('H', [0])
        qs.apply_gate('CNOT', [0, 1])
        expected = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(qs.state_vector, expected, atol=1e-12)

    def test_invalid_gate_name(self):
        """Reject unknown gate names."""
        qs = QuantumState(1)
        with pytest.raises(ValueError):
            qs.apply_gate('FAKE_GATE', [0])

    def test_wrong_qubit_count(self):
        """Reject CNOT on single qubit target."""
        qs = QuantumState(2)
        with pytest.raises(ValueError):
            qs.apply_gate('CNOT', [0])

    def test_qubit_out_of_bounds(self):
        """Reject qubit index beyond system size."""
        qs = QuantumState(2)
        with pytest.raises(ValueError):
            qs.apply_gate('H', [5])

    def test_parameterized_gate(self):
        """Rx(π)|0⟩ = -i|1⟩."""
        qs = QuantumState(1)
        qs.apply_gate('Rx', [0], param=np.pi)
        # Rx(π)|0⟩ = -i|1⟩
        expected = np.array([0, -1j], dtype=complex)
        np.testing.assert_allclose(qs.state_vector, expected, atol=1e-12)


class TestProbabilities:
    """Tests for measurement probability calculations."""

    def test_zero_state_probs(self):
        """|0⟩ → P(0)=1, P(1)=0."""
        qs = QuantumState(1)
        probs = qs.get_probabilities()
        assert 0 in probs
        assert abs(probs[0] - 1.0) < 1e-10

    def test_superposition_probs(self):
        """|+⟩ → P(0)=P(1)=0.5."""
        qs = QuantumState(1)
        qs.apply_gate('H', [0])
        probs = qs.get_probabilities()
        assert abs(probs[0] - 0.5) < 1e-10
        assert abs(probs[1] - 0.5) < 1e-10

    def test_bell_state_probs(self):
        """Bell state → P(00)=P(11)=0.5."""
        qs = QuantumState(2)
        qs.apply_gate('H', [0])
        qs.apply_gate('CNOT', [0, 1])
        probs = qs.get_probabilities()
        assert abs(probs[0] - 0.5) < 1e-10  # |00⟩
        assert abs(probs[3] - 0.5) < 1e-10  # |11⟩

    def test_probs_sum_to_one(self):
        """All probabilities sum to 1."""
        qs = QuantumState(3)
        qs.apply_gate('H', [0])
        qs.apply_gate('H', [1])
        qs.apply_gate('CNOT', [0, 2])
        probs = qs.get_probabilities()
        assert abs(sum(probs.values()) - 1.0) < 1e-10


class TestBlochSphere:
    """Tests for Bloch sphere coordinate extraction."""

    def test_zero_state_north_pole(self):
        """|0⟩ → Bloch vector (0, 0, 1)."""
        qs = QuantumState(1)
        bloch = qs.get_bloch_coords(0)
        assert abs(bloch['z'] - 1.0) < 1e-10
        assert abs(bloch['x']) < 1e-10
        assert abs(bloch['y']) < 1e-10

    def test_one_state_south_pole(self):
        """|1⟩ → Bloch vector (0, 0, -1)."""
        qs = QuantumState(1)
        qs.apply_gate('X', [0])
        bloch = qs.get_bloch_coords(0)
        assert abs(bloch['z'] + 1.0) < 1e-10

    def test_plus_state_x_axis(self):
        """|+⟩ → Bloch vector (1, 0, 0)."""
        qs = QuantumState(1)
        qs.apply_gate('H', [0])
        bloch = qs.get_bloch_coords(0)
        assert abs(bloch['x'] - 1.0) < 1e-10
        assert abs(bloch['y']) < 1e-10
        assert abs(bloch['z']) < 1e-10

    def test_invalid_qubit_index(self):
        """Reject out-of-range qubit index."""
        qs = QuantumState(2)
        with pytest.raises(ValueError):
            qs.get_bloch_coords(5)


class TestStateManagement:
    """Tests for copy, reset, and serialization."""

    def test_copy_independence(self):
        """copy() creates independent state."""
        qs1 = QuantumState(1)
        qs1.apply_gate('H', [0])
        qs2 = qs1.copy()

        qs2.apply_gate('X', [0])
        # qs1 should be unchanged
        expected_qs1 = np.array([1, 1], dtype=complex) / np.sqrt(2)
        np.testing.assert_allclose(qs1.state_vector, expected_qs1, atol=1e-12)

    def test_reset(self):
        """reset() returns to |0⟩."""
        qs = QuantumState(2)
        qs.apply_gate('H', [0])
        qs.apply_gate('CNOT', [0, 1])
        qs.reset()
        np.testing.assert_allclose(qs.state_vector[0], 1.0)
        assert np.sum(np.abs(qs.state_vector[1:]) ** 2) < 1e-14

    def test_to_dict(self):
        """to_dict() returns valid serializable dict."""
        qs = QuantumState(1)
        d = qs.to_dict()
        assert d['n_qubits'] == 1
        assert len(d['amplitudes']) == 2
        assert len(d['bloch_coords']) == 1
        assert isinstance(d['probabilities'], dict)

    def test_set_state_valid(self):
        """set_state() accepts normalized state."""
        qs = QuantumState(1)
        custom = np.array([1, 1], dtype=complex) / np.sqrt(2)
        qs.set_state(custom)
        np.testing.assert_allclose(qs.state_vector, custom)

    def test_set_state_unnormalized(self):
        """set_state() rejects unnormalized state."""
        qs = QuantumState(1)
        with pytest.raises(ValueError, match="normalized"):
            qs.set_state(np.array([1, 1], dtype=complex))

    def test_repr(self):
        """__repr__ produces readable string."""
        qs = QuantumState(1)
        repr_str = repr(qs)
        assert '|0⟩' in repr_str
