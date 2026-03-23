/**
 * TypeScript interfaces for the Quantum Simulator.
 * Mirrors the Pydantic models from the backend.
 */

export interface AmplitudeInfo {
  index: number;
  label: string;
  real: number;
  imag: number;
  magnitude: number;
  phase: number;
  probability: number;
}

export interface BlochCoords {
  x: number;
  y: number;
  z: number;
  theta: number;
  phi: number;
  purity: number;
}

export interface StateSnapshot {
  n_qubits: number;
  amplitudes: AmplitudeInfo[];
  probabilities: Record<string, number>;
  bloch_coords: BlochCoords[];
  classical_bits: Record<number, number>;
}

export interface GateOperation {
  gate: string;
  targets: number[];
  param?: number | null;
  label?: string;
}

export interface GateInfo {
  name: string;
  label: string;
  description: string;
  n_qubits: number;
  has_parameter: boolean;
  parameter_name: string | null;
}

export interface AlgorithmParameter {
  name: string;
  type: string;
  default: unknown;
  description: string;
  min?: number;
  max?: number;
  options?: string[];
}

export interface AlgorithmInfo {
  name: string;
  display_name: string;
  description: string;
  category: 'algorithm' | 'protocol';
  parameters: AlgorithmParameter[];
}

export interface CircuitStep extends GateOperation {
  oracle_type?: string;
  oracle_targets?: number[];
  classical_comm?: boolean;
  condition_qubit?: number;
  round?: number;
}

export interface SimulationResult {
  success: boolean;
  n_qubits: number;
  final_state: StateSnapshot;
  measurement?: string;
  measurement_counts?: Record<string, number>;
  state_history?: StateSnapshot[];
}

export interface AlgorithmResult {
  success: boolean;
  algorithm: string;
  result: Record<string, unknown>;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';
