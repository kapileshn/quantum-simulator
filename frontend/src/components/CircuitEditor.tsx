/**
 * CircuitEditor — Center panel component
 * SVG-based quantum circuit renderer with click-to-place gate interaction.
 *
 * Features:
 *   - Active gate highlighting with glow
 *   - Hover math tooltips (matrix + description)
 *   - Circuit pulse propagation animation during playback
 *   - Cross-component qubit highlighting (broadcasts hovered gate targets to BlochSphere)
 *   - Step indicator dashed line
 */

import { useState, useEffect, useRef } from 'react';
import { useSimStore } from '../store/useSimStore';
import type { GateInfo } from '../types/quantum';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const WIRE_Y_START = 60;
const WIRE_Y_GAP = 60;
const GATE_X_START = 120;
const GATE_X_GAP = 70;
const GATE_SIZE = 40;

const GATE_COLORS: Record<string, string> = {
  H: '#00d4ff',
  X: '#f97316',
  Y: '#a855f7',
  Z: '#10b981',
  S: '#6366f1',
  'S†': '#818cf8',
  T: '#ec4899',
  'T†': '#f472b6',
  CNOT: '#f59e0b',
  CZ: '#eab308',
  SWAP: '#14b8a6',
  CCX: '#ef4444',
  Rx: '#06b6d4',
  Ry: '#8b5cf6',
  Rz: '#22c55e',
  P: '#d946ef',
  I: '#64748b',
  M: '#94a3b8',
};

// Gate matrix descriptions for educational tooltips
const GATE_MATRICES: Record<string, { matrix: string; desc: string }> = {
  H:    { matrix: '1/√2 · [[1, 1], [1, -1]]', desc: 'Creates equal superposition' },
  X:    { matrix: '[[0, 1], [1, 0]]', desc: 'Bit-flip (NOT gate)' },
  Y:    { matrix: '[[0, -i], [i, 0]]', desc: 'Bit+phase flip' },
  Z:    { matrix: '[[1, 0], [0, -1]]', desc: 'Phase-flip gate' },
  S:    { matrix: '[[1, 0], [0, i]]', desc: '√Z — 90° phase' },
  'S†': { matrix: '[[1, 0], [0, -i]]', desc: 'S-dagger — -90° phase' },
  T:    { matrix: '[[1, 0], [0, e^(iπ/4)]]', desc: '√S — 45° phase' },
  'T†': { matrix: '[[1, 0], [0, e^(-iπ/4)]]', desc: 'T-dagger — -45° phase' },
  Rx:   { matrix: '[[cos θ/2, -i·sin θ/2], [-i·sin θ/2, cos θ/2]]', desc: 'X-axis rotation' },
  Ry:   { matrix: '[[cos θ/2, -sin θ/2], [sin θ/2, cos θ/2]]', desc: 'Y-axis rotation' },
  Rz:   { matrix: '[[e^(-iθ/2), 0], [0, e^(iθ/2)]]', desc: 'Z-axis rotation' },
  P:    { matrix: '[[1, 0], [0, e^(iφ)]]', desc: 'General phase gate' },
  CNOT: { matrix: '|00⟩⟨00| + |01⟩⟨01| + |11⟩⟨10| + |10⟩⟨11|', desc: 'Flips target if control=|1⟩' },
  CZ:   { matrix: 'diag(1, 1, 1, -1)', desc: 'Phase-flip if both |1⟩' },
  SWAP: { matrix: '|00⟩⟨00| + |01⟩⟨10| + |10⟩⟨01| + |11⟩⟨11|', desc: 'Swaps two qubit states' },
  CCX:  { matrix: 'I₆ ⊕ X', desc: 'Toffoli — flips target if both controls=|1⟩' },
  I:    { matrix: '[[1, 0], [0, 1]]', desc: 'Identity (no operation)' },
  M:    { matrix: 'P₀ = |0⟩⟨0|, P₁ = |1⟩⟨1|', desc: 'Projective measurement' },
};

// Animated pulse dot: travels along all wires at currentStep's x position
interface PulseProps {
  nQubits: number;
  svgWidth: number;
  svgHeight: number;
  active: boolean;
  targetX: number;
}

function PulseLayer({ nQubits, active, targetX }: PulseProps) {
  const dotRef = useRef<SVGCircleElement[]>([]);
  const animFrameRef = useRef<number>(0);
  const startXRef = useRef(GATE_X_START);
  const progressRef = useRef(0);
  const [dots, setDots] = useState<{ x: number; opacity: number }[]>([]);

  useEffect(() => {
    if (!active || nQubits === 0) {
      setDots([]);
      return;
    }

    startXRef.current = GATE_X_START;
    progressRef.current = 0;
    const duration = 350; // ms
    const startTime = performance.now();
    const startX = startXRef.current;

    function animate(now: number) {
      const elapsed = now - startTime;
      const t = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      const currentX = startX + (targetX - startX) * eased;
      const opacity = t < 0.8 ? 1 : 1 - (t - 0.8) / 0.2;
      setDots([{ x: currentX, opacity }]);
      if (t < 1) {
        animFrameRef.current = requestAnimationFrame(animate);
      } else {
        setDots([]);
      }
    }

    animFrameRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrameRef.current);
  }, [active, targetX, nQubits]);

  if (dots.length === 0) return null;

  return (
    <g className="pulse-layer" pointerEvents="none">
      {dots.map((d, di) =>
        Array.from({ length: nQubits }, (_, q) => {
          const y = WIRE_Y_START + q * WIRE_Y_GAP;
          return (
            <g key={`${di}-${q}`}>
              {/* Glow trail */}
              <circle cx={d.x - 8} cy={y} r={5} fill="#00d4ff" opacity={d.opacity * 0.2} />
              <circle cx={d.x - 4} cy={y} r={4} fill="#00d4ff" opacity={d.opacity * 0.35} />
              {/* Main pulse dot */}
              <circle
                ref={el => { if (el) dotRef.current[q] = el; }}
                cx={d.x}
                cy={y}
                r={5}
                fill="#00d4ff"
                opacity={d.opacity * 0.9}
                filter="url(#pulseGlow)"
              />
            </g>
          );
        })
      )}
      {/* Glow filter definition */}
      <defs>
        <filter id="pulseGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
    </g>
  );
}

export default function CircuitEditor() {
  const {
    nQubits, operations, addOperation, removeOperation, clearOperations,
    currentStep, setStateHistory, setHoveredGateTargets,
  } = useSimStore();

  const [gates, setGates] = useState<GateInfo[]>([]);
  const [selectedGate, setSelectedGate] = useState<string | null>(null);
  const [paramValue, setParamValue] = useState<number>(Math.PI / 2);
  const [hoverWire, setHoverWire] = useState<number | null>(null);
  const [secondTarget, setSecondTarget] = useState<{gate: string; first: number} | null>(null);
  const [hoveredGateBtn, setHoveredGateBtn] = useState<string | null>(null);

  // Pulse animation state
  const [pulseActive, setPulseActive] = useState(false);
  const prevStepRef = useRef(currentStep);

  useEffect(() => {
    if (currentStep !== prevStepRef.current && currentStep > 0) {
      setPulseActive(true);
      const t = setTimeout(() => setPulseActive(false), 400);
      prevStepRef.current = currentStep;
      return () => clearTimeout(t);
    }
    prevStepRef.current = currentStep;
  }, [currentStep]);

  // Fetch available gates
  useEffect(() => {
    fetch(`${API_URL}/api/gates`)
      .then((r) => r.json())
      .then((data) => setGates(data.gates))
      .catch(console.error);
  }, []);

  // Automatic simulation on circuit changes
  useEffect(() => {
    const simulate = async () => {
      try {
        const res = await fetch(`${API_URL}/api/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            n_qubits: nQubits,
            operations: operations,
            measure_all: false
          }),
        });
        const data = await res.json();
        if (data.success && data.state_history) {
          setStateHistory(data.state_history);
        }
      } catch (e) {
        console.error('Manual simulation failed:', e);
      }
    };
    simulate();
  }, [operations, nQubits, setStateHistory]);

  const wireY = (q: number) => WIRE_Y_START + q * WIRE_Y_GAP;
  const gateX = (step: number) => GATE_X_START + step * GATE_X_GAP;

  const svgWidth = Math.max(600, GATE_X_START + (operations.length + 2) * GATE_X_GAP);
  const svgHeight = WIRE_Y_START + nQubits * WIRE_Y_GAP + 20;
  const pulseTargetX = currentStep > 0 ? gateX(currentStep - 1) : GATE_X_START;

  const handleWireClick = (qubitIndex: number) => {
    if (!selectedGate) return;
    const gateInfo = gates.find((g) => g.name === selectedGate);
    if (!gateInfo) return;

    if (gateInfo.n_qubits === 1) {
      addOperation({ gate: selectedGate, targets: [qubitIndex], param: gateInfo.has_parameter ? paramValue : undefined });
    } else if (gateInfo.n_qubits === 2) {
      if (!secondTarget) {
        setSecondTarget({ gate: selectedGate, first: qubitIndex });
      } else {
        if (secondTarget.first !== qubitIndex) {
          addOperation({ gate: secondTarget.gate, targets: [secondTarget.first, qubitIndex] });
        }
        setSecondTarget(null);
      }
    } else if (gateInfo.n_qubits === 3) {
      if (!secondTarget) {
        setSecondTarget({ gate: selectedGate, first: qubitIndex });
      } else {
        const used = new Set([secondTarget.first, qubitIndex]);
        let thirdTarget = -1;
        for (let q = 0; q < nQubits; q++) {
          if (!used.has(q)) { thirdTarget = q; break; }
        }
        if (thirdTarget === -1 || secondTarget.first === qubitIndex) { setSecondTarget(null); return; }
        addOperation({ gate: selectedGate, targets: [secondTarget.first, qubitIndex, thirdTarget] });
        setSecondTarget(null);
      }
    }
  };

  const handleAddMeasurement = () => {
    for (let i = 0; i < nQubits; i++) {
      addOperation({ gate: 'M', targets: [i], label: `Measure q${i}` });
    }
  };

  // Cross-component: broadcast which qubits a hovered *placed* gate touches
  const handleGateHoverEnter = (targets: number[]) => setHoveredGateTargets(targets);
  const handleGateHoverLeave = () => setHoveredGateTargets([]);

  return (
    <div className="panel circuit-editor">
      <div className="circuit-toolbar">
        <h2 className="panel-title">
          <span className="title-icon">≡</span> Quantum Circuit
        </h2>
        <div className="toolbar-actions">
          <button className="tool-btn" onClick={handleAddMeasurement} title="Add measurements">
            📏 Measure
          </button>
          <button className="tool-btn danger" onClick={clearOperations} title="Clear all">
            🗑 Clear
          </button>
        </div>
      </div>

      {/* Gate palette with hover tooltips */}
      <div className="gate-palette">
        {gates.filter(g => g.n_qubits <= 2).map((g, index) => (
          <div key={g.name} className="gate-btn-wrapper">
            <button
              className={`gate-btn ${selectedGate === g.name ? 'selected' : ''}`}
              style={{
                borderColor: selectedGate === g.name ? GATE_COLORS[g.name] || '#00d4ff' : undefined,
                color: GATE_COLORS[g.name] || '#00d4ff',
              }}
              onClick={() => {
                setSelectedGate(selectedGate === g.name ? null : g.name);
                setSecondTarget(null);
              }}
              onMouseEnter={() => setHoveredGateBtn(g.name)}
              onMouseLeave={() => setHoveredGateBtn(null)}
            >
              {g.label}
            </button>
            {/* Educational Math Tooltip */}
            {hoveredGateBtn === g.name && GATE_MATRICES[g.name] && (
              <div 
                className="gate-tooltip"
                style={{
                  left: index < 5 ? '-8px' : '50%',
                  transform: index < 5 ? 'none' : 'translateX(-50%)'
                }}
              >
                <style>
                  {`
                    .gate-btn-wrapper:nth-child(${index + 1}) .gate-tooltip::after {
                      left: ${index < 5 ? '24px' : '50%'};
                      transform: ${index < 5 ? 'none' : 'translateX(-50%)'};
                    }
                  `}
                </style>
                <div className="gate-tooltip-name">{g.name} Gate</div>
                <div className="gate-tooltip-matrix">{GATE_MATRICES[g.name].matrix}</div>
                <div className="gate-tooltip-desc">{GATE_MATRICES[g.name].desc}</div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Parameter input for parameterized gates */}
      {selectedGate && gates.find((g) => g.name === selectedGate)?.has_parameter && (
        <div className="param-input-row">
          <label>θ/φ = </label>
          <input
            type="number"
            step="0.1"
            value={paramValue}
            onChange={(e) => {
              const v = parseFloat(e.target.value);
              if (!isNaN(v)) setParamValue(v);
            }}
          />
          <span className="param-hint">
            (π/4≈0.785, π/2≈1.571, π≈3.142)
          </span>
        </div>
      )}

      {/* Second target hint */}
      {secondTarget && (
        <div className="hint-bar">
          Click second qubit wire for {secondTarget.gate} (control: q{secondTarget.first})
        </div>
      )}

      {/* Circuit SVG */}
      <div className="circuit-canvas">
        <svg width={svgWidth} height={svgHeight} className="circuit-svg">
          {/* Qubit labels */}
          {Array.from({ length: nQubits }, (_, q) => (
            <text
              key={`label-${q}`}
              x={20}
              y={wireY(q) + 5}
              className="qubit-label"
              fill="#94a3b8"
            >
              q{q} |0⟩
            </text>
          ))}

          {/* Qubit wires */}
          {Array.from({ length: nQubits }, (_, q) => (
            <g key={`wire-${q}`}>
              <line
                x1={80} y1={wireY(q)} x2={svgWidth - 20} y2={wireY(q)}
                stroke="#334155" strokeWidth={2}
              />
              {/* Invisible wider click target */}
              <line
                x1={80} y1={wireY(q)} x2={svgWidth - 20} y2={wireY(q)}
                stroke="transparent" strokeWidth={20}
                style={{ cursor: selectedGate ? 'crosshair' : 'default' }}
                onClick={() => handleWireClick(q)}
                onMouseEnter={() => setHoverWire(q)}
                onMouseLeave={() => setHoverWire(null)}
              />
              {/* Hover highlight */}
              {hoverWire === q && selectedGate && (
                <line
                  x1={80} y1={wireY(q)} x2={svgWidth - 20} y2={wireY(q)}
                  stroke={GATE_COLORS[selectedGate] || '#00d4ff'} strokeWidth={2}
                  opacity={0.4} pointerEvents="none"
                />
              )}
            </g>
          ))}

          {/* Gates */}
          {operations.map((op, idx) => {
            const x = gateX(idx);
            const color = GATE_COLORS[op.gate] || '#00d4ff';
            const isActive = idx === currentStep - 1;
            const isPast = idx < currentStep - 1;

            if (op.gate === 'M') {
              const y = wireY(op.targets[0]);
              return (
                <g
                  key={idx}
                  opacity={isPast ? 0.5 : 1}
                  onClick={() => removeOperation(idx)}
                  onMouseEnter={() => handleGateHoverEnter(op.targets)}
                  onMouseLeave={handleGateHoverLeave}
                  style={{ cursor: 'pointer' }}
                >
                  <rect x={x - 18} y={y - 18} width={36} height={36} rx={4}
                    fill="#1e293b" stroke={isActive ? '#facc15' : '#475569'} strokeWidth={isActive ? 2.5 : 1.5} />
                  <path d={`M${x - 10} ${y + 6} Q${x} ${y - 10} ${x + 10} ${y + 6}`}
                    fill="none" stroke="#94a3b8" strokeWidth={1.5} />
                  <line x1={x} y1={y - 2} x2={x + 7} y2={y - 10}
                    stroke="#94a3b8" strokeWidth={1.5} />
                  {isActive && (
                    <rect x={x - 22} y={y - 22} width={44} height={44} rx={6}
                      fill="none" stroke="#facc15" strokeWidth={1.5} opacity={0.6}
                      className="gate-active-glow" />
                  )}
                </g>
              );
            }

            if (op.targets.length === 1) {
              const y = wireY(op.targets[0]);
              return (
                <g
                  key={idx}
                  opacity={isPast ? 0.5 : 1}
                  onClick={() => removeOperation(idx)}
                  onMouseEnter={() => handleGateHoverEnter(op.targets)}
                  onMouseLeave={handleGateHoverLeave}
                  style={{ cursor: 'pointer' }}
                >
                  <rect
                    x={x - GATE_SIZE / 2} y={y - GATE_SIZE / 2}
                    width={GATE_SIZE} height={GATE_SIZE} rx={6}
                    fill={isActive ? 'rgba(250, 204, 21, 0.1)' : '#0f172a'}
                    stroke={isActive ? '#facc15' : color}
                    strokeWidth={isActive ? 2.5 : 1.5}
                    className="gate-rect"
                  />
                  <text x={x} y={y + 5} textAnchor="middle"
                    fill={isActive ? '#facc15' : color} fontSize={14} fontWeight="bold">
                    {op.gate}
                  </text>
                  {isActive && (
                    <rect x={x - GATE_SIZE / 2 - 4} y={y - GATE_SIZE / 2 - 4}
                      width={GATE_SIZE + 8} height={GATE_SIZE + 8} rx={8}
                      fill="none" stroke="#facc15" strokeWidth={1} opacity={0.4}
                      className="gate-active-glow" />
                  )}
                </g>
              );
            }

            // Multi-qubit gate
            const y0 = wireY(op.targets[0]);
            const y1 = wireY(op.targets[1]);
            return (
              <g
                key={idx}
                opacity={isPast ? 0.5 : 1}
                onClick={() => removeOperation(idx)}
                onMouseEnter={() => handleGateHoverEnter(op.targets)}
                onMouseLeave={handleGateHoverLeave}
                style={{ cursor: 'pointer' }}
              >
                {isActive && (
                  <rect
                    x={x - 20} y={Math.min(y0, y1) - 20}
                    width={40} height={Math.abs(y1 - y0) + 40} rx={8}
                    fill="rgba(250, 204, 21, 0.05)" stroke="#facc15"
                    strokeWidth={1} opacity={0.4}
                    className="gate-active-glow"
                  />
                )}
                <line
                  x1={x} y1={Math.min(y0, y1)} x2={x} y2={Math.max(y0, y1)}
                  stroke={isActive ? '#facc15' : color} strokeWidth={2}
                />
                <circle cx={x} cy={y0} r={6} fill={isActive ? '#facc15' : color} />
                {op.gate === 'SWAP' ? (
                  <>
                    <text x={x} y={y0 + 5} textAnchor="middle" fill={color} fontSize={18}>×</text>
                    <text x={x} y={y1 + 5} textAnchor="middle" fill={color} fontSize={18}>×</text>
                  </>
                ) : (
                  <>
                    <circle cx={x} cy={y1} r={14} fill="none"
                      stroke={isActive ? '#facc15' : color} strokeWidth={2} />
                    <line x1={x - 10} y1={y1} x2={x + 10} y2={y1}
                      stroke={isActive ? '#facc15' : color} strokeWidth={2} />
                    <line x1={x} y1={y1 - 10} x2={x} y2={y1 + 10}
                      stroke={isActive ? '#facc15' : color} strokeWidth={2} />
                  </>
                )}
              </g>
            );
          })}

          {/* Pulse propagation layer */}
          <PulseLayer
            nQubits={nQubits}
            svgWidth={svgWidth}
            svgHeight={svgHeight}
            active={pulseActive}
            targetX={pulseTargetX}
          />

          {/* Step indicator line */}
          {currentStep > 0 && currentStep <= operations.length && (
            <line
              x1={gateX(currentStep - 1)}
              y1={WIRE_Y_START - 30}
              x2={gateX(currentStep - 1)}
              y2={svgHeight - 10}
              stroke="#facc15"
              strokeWidth={1}
              strokeDasharray="4 4"
              opacity={0.5}
            />
          )}
        </svg>
      </div>
    </div>
  );
}
