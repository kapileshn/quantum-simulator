"""
Unit Tests: Quantum Algorithms
==============================
Tests for all implemented quantum algorithms and protocols.
"""

import numpy as np
import pytest
from simulation_engine.algorithms import deutsch_jozsa, grover, teleportation, bb84, qrng


class TestDeutschJozsa:
    """Tests for the Deutsch-Jozsa algorithm."""

    def test_constant_0_detected(self):
        """Constant-0 oracle should be detected as constant."""
        result = deutsch_jozsa.run(n_input=2, oracle_type='constant_0')
        assert result['result'] == 'constant'

    def test_constant_1_detected(self):
        """Constant-1 oracle should be detected as constant."""
        result = deutsch_jozsa.run(n_input=2, oracle_type='constant_1')
        assert result['result'] == 'constant'

    def test_balanced_detected(self):
        """Balanced oracle should be detected as balanced."""
        result = deutsch_jozsa.run(n_input=2, oracle_type='balanced')
        assert result['result'] == 'balanced'

    def test_single_qubit_balanced(self):
        """1-input qubit balanced function (Deutsch's problem)."""
        result = deutsch_jozsa.run(n_input=1, oracle_type='balanced')
        assert result['result'] == 'balanced'

    def test_constant_measurement_all_zeros(self):
        """Constant oracle → measurement should be all zeros."""
        result = deutsch_jozsa.run(n_input=3, oracle_type='constant_0')
        assert result['measurement'] == '000'

    def test_has_state_history(self):
        """Result includes state history for step-by-step visualization."""
        result = deutsch_jozsa.run(n_input=2, oracle_type='balanced')
        assert 'state_history' in result
        assert len(result['state_history']) > 1

    def test_invalid_oracle_type(self):
        """Reject invalid oracle type."""
        with pytest.raises(ValueError):
            deutsch_jozsa.run(oracle_type='invalid')


class TestGrover:
    """Tests for Grover's search algorithm."""

    def test_finds_target_2_qubits(self):
        """2-qubit Grover should find target with high probability."""
        # Run multiple times to handle probabilistic nature
        successes = 0
        target = 3  # |11⟩
        for _ in range(10):
            result = grover.run(n_qubits=2, target_states=[target])
            if result['success']:
                successes += 1
        # Grover's should succeed with very high probability
        assert successes >= 7, f"Only {successes}/10 successes"

    def test_finds_target_3_qubits(self):
        """3-qubit Grover should find target."""
        successes = 0
        target = 5  # |101⟩
        for _ in range(10):
            result = grover.run(n_qubits=3, target_states=[target])
            if result['success']:
                successes += 1
        assert successes >= 6

    def test_optimal_iterations_calculated(self):
        """Optimal iteration count is correctly computed."""
        result = grover.run(n_qubits=3, target_states=[7])
        assert result['optimal_iterations'] == grover.optimal_iterations(3, 1)

    def test_has_state_history(self):
        result = grover.run(n_qubits=2, target_states=[0])
        assert 'state_history' in result
        assert len(result['state_history']) > 1

    def test_invalid_qubit_count(self):
        with pytest.raises(ValueError):
            grover.run(n_qubits=1)
        with pytest.raises(ValueError):
            grover.run(n_qubits=6)


class TestTeleportation:
    """Tests for quantum teleportation."""

    def test_teleport_zero_state(self):
        """Teleporting |0⟩ should produce |0⟩ on Bob's qubit."""
        result = teleportation.run(alpha=1.0, beta=0.0)
        bloch = result['bob_qubit_bloch']
        # |0⟩ → z ≈ 1
        assert abs(bloch['z'] - 1.0) < 0.3, f"Expected z≈1 for |0⟩, got z={bloch['z']}"

    def test_teleport_one_state(self):
        """Teleporting |1⟩ should produce |1⟩ on Bob's qubit."""
        result = teleportation.run(alpha=0.0, beta=1.0)
        bloch = result['bob_qubit_bloch']
        # |1⟩ → z ≈ -1
        assert abs(bloch['z'] + 1.0) < 0.3, f"Expected z≈-1 for |1⟩, got z={bloch['z']}"

    def test_always_succeeds(self):
        """Teleportation always succeeds (deterministic with corrections)."""
        result = teleportation.run(theta=np.pi/4, phi=np.pi/3)
        assert result['success']

    def test_measurements_are_classical_bits(self):
        """Alice's measurements produce valid classical bits."""
        result = teleportation.run()
        assert all(v in (0, 1) for v in result['measurements'].values())

    def test_has_state_history(self):
        result = teleportation.run()
        assert len(result['state_history']) > 1


class TestBB84:
    """Tests for BB84 QKD protocol."""

    def test_no_eve_is_secure(self):
        """Without eavesdropper, channel should be secure."""
        result = bb84.run(n_bits=32, eve_present=False, seed=42)
        assert result['secure']
        assert result['error_rate'] < 0.11

    def test_eve_detected(self):
        """With eavesdropper, error rate should increase."""
        # Eve introduces ~25% error rate on average
        # Run multiple times since it's probabilistic
        high_error_count = 0
        for seed in range(5):
            result = bb84.run(n_bits=32, eve_present=True, seed=seed)
            if result['error_rate'] > 0.05:  # Some error expected
                high_error_count += 1
        assert high_error_count >= 2  # Eve should usually be detectable

    def test_sifting_reduces_key(self):
        """Sifting should produce fewer bits than exchanged."""
        result = bb84.run(n_bits=32, seed=42)
        assert result['n_sifted'] < 32
        # On average ~50% retention
        assert result['n_sifted'] > 0

    def test_matching_bases_produce_same_bits(self):
        """When bases match and no Eve, Alice and Bob get same bits."""
        result = bb84.run(n_bits=32, eve_present=False, seed=42)
        for a, b in zip(result['sifted_key_alice'], result['sifted_key_bob']):
            assert a == b  # Should be identical without Eve

    def test_has_round_data(self):
        result = bb84.run(n_bits=8, seed=0)
        assert len(result['rounds']) == 8
        assert 'alice_bit' in result['rounds'][0]
        assert 'bob_bit' in result['rounds'][0]


class TestQRNG:
    """Tests for Quantum Random Number Generator."""

    def test_correct_length(self):
        """Output has requested number of bits."""
        result = qrng.run(n_bits=16, seed=42)
        assert len(result['bitstring']) == 16

    def test_frequency_sums_to_total(self):
        """Frequency counts sum to total bits."""
        result = qrng.run(n_bits=32, seed=42)
        total = result['frequency']['zeros'] + result['frequency']['ones']
        assert total == 32

    def test_has_integer_value(self):
        """Small bit count produces integer value."""
        result = qrng.run(n_bits=8, seed=42)
        assert result['integer_value'] is not None
        assert 0 <= result['integer_value'] <= 255

    def test_approximately_uniform(self):
        """Large sample should be roughly 50/50."""
        result = qrng.run(n_bits=200, seed=42)
        ratio = result['frequency']['ones'] / 200
        assert 0.3 < ratio < 0.7  # Generous bounds

    def test_invalid_bit_count(self):
        with pytest.raises(ValueError):
            qrng.run(n_bits=0)
        with pytest.raises(ValueError):
            qrng.run(n_bits=300)
