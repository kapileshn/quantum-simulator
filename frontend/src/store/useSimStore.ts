/**
 * Zustand store for global simulation state.
 * Manages circuit operations, state history, step navigation, and connection status.
 */

import { create } from 'zustand';
import type {
  StateSnapshot,
  GateOperation,
  AlgorithmInfo,
  ConnectionStatus,
} from '../types/quantum';

interface SimState {
  // Circuit state
  nQubits: number;
  operations: GateOperation[];
  currentStep: number;
  totalSteps: number;
  stateHistory: StateSnapshot[];
  isPlaying: boolean;
  playSpeed: number;

  // Algorithm selection
  selectedAlgorithm: string | null;
  algorithms: AlgorithmInfo[];
  algorithmResult: Record<string, unknown> | null;

  // Connection
  connectionStatus: ConnectionStatus;
  sessionId: string | null;

  // UI cross-component
  hoveredGateTargets: number[];

  // Actions
  setNQubits: (n: number) => void;
  addOperation: (op: GateOperation) => void;
  removeOperation: (index: number) => void;
  clearOperations: () => void;
  loadPreset: (ops: GateOperation[], nQubits: number) => void;

  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  resetStep: () => void;
  setPlaying: (playing: boolean) => void;
  setPlaySpeed: (speed: number) => void;

  setStateHistory: (history: StateSnapshot[]) => void;
  setAlgorithms: (algorithms: AlgorithmInfo[]) => void;
  setSelectedAlgorithm: (name: string | null) => void;
  setAlgorithmResult: (result: Record<string, unknown> | null) => void;
  setConnectionStatus: (status: ConnectionStatus) => void;
  setSessionId: (id: string | null) => void;
  setHoveredGateTargets: (targets: number[]) => void;
}

export const useSimStore = create<SimState>((set, get) => ({
  // Initial state
  nQubits: 2,
  operations: [],
  currentStep: 0,
  totalSteps: 1,
  stateHistory: [],
  isPlaying: false,
  playSpeed: 1000,

  selectedAlgorithm: null,
  algorithms: [],
  algorithmResult: null,

  connectionStatus: 'connecting',
  sessionId: null,

  hoveredGateTargets: [],

  // Circuit actions
  setNQubits: (n) => set({ nQubits: n, operations: [], currentStep: 0, stateHistory: [] }),

  addOperation: (op) => set((s) => ({
    operations: [...s.operations, op],
  })),

  removeOperation: (index) => set((s) => ({
    operations: s.operations.filter((_, i) => i !== index),
  })),

  clearOperations: () => set({
    operations: [],
    currentStep: 0,
    stateHistory: [],
    totalSteps: 1,
    algorithmResult: null,
  }),

  loadPreset: (ops, nQubits) => set({
    operations: ops,
    nQubits,
    currentStep: 0,
    algorithmResult: null,
  }),

  // Step navigation
  setCurrentStep: (step) => set({ currentStep: step }),

  nextStep: () => {
    const { currentStep, totalSteps } = get();
    if (currentStep < totalSteps - 1) {
      set({ currentStep: currentStep + 1 });
    }
  },

  prevStep: () => {
    const { currentStep } = get();
    if (currentStep > 0) {
      set({ currentStep: currentStep - 1 });
    }
  },

  resetStep: () => set({ currentStep: 0 }),

  setPlaying: (playing) => set({ isPlaying: playing }),
  setPlaySpeed: (speed) => set({ playSpeed: speed }),

  // State updates
  setStateHistory: (history) => set({
    stateHistory: history,
    totalSteps: history.length,
    currentStep: 0,
  }),

  setAlgorithms: (algorithms) => set({ algorithms }),
  setSelectedAlgorithm: (name) => set({ selectedAlgorithm: name, algorithmResult: null }),
  setAlgorithmResult: (result) => set({ algorithmResult: result }),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  setSessionId: (id) => set({ sessionId: id }),
  setHoveredGateTargets: (targets) => set({ hoveredGateTargets: targets }),
}));
