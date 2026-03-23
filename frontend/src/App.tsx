/**
 * App.tsx — Main application component
 * 4-panel layout: Algorithm selector, Circuit editor, Bloch sphere, Statevector panel
 * With connection status indicator and responsive design.
 */

import { useEffect } from 'react';
import AlgorithmSelector from './components/AlgorithmSelector';
import CircuitEditor from './components/CircuitEditor';
import BlochSphere from './components/BlochSphere';
import StatevectorPanel from './components/StatevectorPanel';
import StepController from './components/StepController';
import { useSocket } from './hooks/useSocket';
import { useSimStore } from './store/useSimStore';
import type { ConnectionStatus } from './types/quantum';


const STATUS_CONFIG: Record<ConnectionStatus, { color: string; label: string; icon: string }> = {
  connecting: { color: '#f59e0b', label: 'Connecting...', icon: '◌' },
  connected: { color: '#10b981', label: 'Connected', icon: '●' },
  disconnected: { color: '#ef4444', label: 'Disconnected', icon: '○' },
  error: { color: '#ef4444', label: 'Connection Error', icon: '✕' },
};

function ConnectionIndicator() {
  const { connectionStatus } = useSimStore();
  const cfg = STATUS_CONFIG[connectionStatus];

  return (
    <div className="connection-indicator" style={{ color: cfg.color }}>
      <span className="status-dot" style={{ backgroundColor: cfg.color }}>{cfg.icon}</span>
      <span className="status-text">{cfg.label}</span>
    </div>
  );
}

export default function App() {
  useSocket(); // Initialize Socket.IO connection

  const { stateHistory } = useSimStore();

  useEffect(() => {
    // Set initial empty state if needed
    if (stateHistory.length === 0) {
      useSimStore.getState().setStateHistory([{
        n_qubits: 2,
        amplitudes: [
          { index: 0, label: '|00⟩', real: 1, imag: 0, magnitude: 1, phase: 0, probability: 1 },
          { index: 1, label: '|01⟩', real: 0, imag: 0, magnitude: 0, phase: 0, probability: 0 },
          { index: 2, label: '|10⟩', real: 0, imag: 0, magnitude: 0, phase: 0, probability: 0 },
          { index: 3, label: '|11⟩', real: 0, imag: 0, magnitude: 0, phase: 0, probability: 0 },
        ],
        probabilities: { '00': 1, '01': 0, '10': 0, '11': 0 },
        bloch_coords: [
          { x: 0, y: 0, z: 1, theta: 0, phi: 0, purity: 1 },
          { x: 0, y: 0, z: 1, theta: 0, phi: 0, purity: 1 },
        ],
        classical_bits: {},
      }]);
    }
  }, [stateHistory.length]);

  return (
    <div className="app">
      {/* Top header */}
      <header className="app-header">
        <div className="header-left">
          <h1 className="app-title">
            <span className="logo-icon">⚛</span>
            Quantum Simulator
          </h1>
          <span className="app-subtitle">Protocol & Algorithm Visualizer</span>
        </div>
        <div className="header-right">
          <ConnectionIndicator />
          <span className="version-badge">v1.0</span>
        </div>
      </header>

      {/* Main grid layout */}
      <main className="app-grid">
        <aside className="grid-left">
          <AlgorithmSelector />
        </aside>

        <section className="grid-center">
          <CircuitEditor />
        </section>

        <aside className="grid-right">
          <BlochSphere />
        </aside>

        <footer className="grid-bottom">
          <StatevectorPanel />
          <StepController />
        </footer>
      </main>
    </div>
  );
}
