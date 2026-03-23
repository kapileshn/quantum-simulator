/**
 * StatevectorPanel — Bottom panel component
 * Shows complex amplitudes table, probability histogram, and Circle Notation (Phase Disks).
 * Includes animated measurement collapse transitions.
 */

import { useState, useRef, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { useSimStore } from '../store/useSimStore';

type ViewMode = 'histogram' | 'circles' | 'table';

// Color based on phase angle
function phaseColor(phase: number): string {
  const hue = ((phase + Math.PI) / (2 * Math.PI)) * 360;
  return `hsl(${hue}, 80%, 60%)`;
}

// Circle Notation (Phase Disk) component
function PhaseDisks({ amplitudes }: { amplitudes: Array<{
  index: number; label: string; real: number; imag: number;
  magnitude: number; phase: number; probability: number;
}> }) {
  const diskSize = 56;
  const radius = diskSize / 2 - 4;

  return (
    <div className="phase-disks-grid">
      {amplitudes.map((a) => {
        const fillRadius = radius * a.magnitude;
        // Phase hand endpoint (clock-hand style, 0 = up)
        const handX = Math.sin(a.phase) * radius * 0.85;
        const handY = -Math.cos(a.phase) * radius * 0.85;
        const isActive = a.probability > 0.01;

        return (
          <div
            key={a.index}
            className={`phase-disk-item ${isActive ? 'active' : 'inactive'}`}
            title={`${a.label}\nP = ${(a.probability * 100).toFixed(1)}%\nPhase = ${(a.phase * 180 / Math.PI).toFixed(0)}°`}
          >
            <svg width={diskSize} height={diskSize} viewBox={`0 0 ${diskSize} ${diskSize}`}>
              {/* Outer ring */}
              <circle
                cx={diskSize / 2}
                cy={diskSize / 2}
                r={radius}
                fill="none"
                stroke={isActive ? 'rgba(148, 163, 184, 0.4)' : 'rgba(51, 65, 85, 0.3)'}
                strokeWidth={1.5}
              />
              {/* Filled area representing probability magnitude */}
              {isActive && (
                <circle
                  cx={diskSize / 2}
                  cy={diskSize / 2}
                  r={fillRadius}
                  fill={phaseColor(a.phase)}
                  opacity={0.35}
                  className="disk-fill"
                />
              )}
              {/* Phase hand (clock hand) */}
              {isActive && a.magnitude > 0.01 && (
                <line
                  x1={diskSize / 2}
                  y1={diskSize / 2}
                  x2={diskSize / 2 + handX}
                  y2={diskSize / 2 + handY}
                  stroke={phaseColor(a.phase)}
                  strokeWidth={2}
                  strokeLinecap="round"
                  className="phase-hand"
                />
              )}
              {/* Center dot */}
              <circle
                cx={diskSize / 2}
                cy={diskSize / 2}
                r={2}
                fill={isActive ? '#e2e8f0' : '#475569'}
              />
            </svg>
            <span className="disk-label">{a.label}</span>
            <span className="disk-prob">
              {isActive ? `${(a.probability * 100).toFixed(0)}%` : '0'}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function StatevectorPanel() {
  const { stateHistory, currentStep } = useSimStore();
  const [viewMode, setViewMode] = useState<ViewMode>('histogram');
  const [animatingCollapse, setAnimatingCollapse] = useState(false);
  const prevStepRef = useRef(currentStep);

  const currentState = stateHistory[currentStep];
  const amplitudes = currentState?.amplitudes || [];

  // Detect measurement collapse — trigger animation
  useEffect(() => {
    if (prevStepRef.current !== currentStep && currentStep > 0) {
      const prevState = stateHistory[prevStepRef.current];
      const currState = stateHistory[currentStep];
      if (prevState && currState) {
        const prevNonZero = prevState.amplitudes?.filter((a: any) => a.probability > 0.01).length || 0;
        const currNonZero = currState.amplitudes?.filter((a: any) => a.probability > 0.01).length || 0;
        // If states dramatically collapsed (e.g., from 2+ to 1), animate
        if (prevNonZero > 1 && currNonZero === 1) {
          setAnimatingCollapse(true);
          setTimeout(() => setAnimatingCollapse(false), 600);
        }
      }
    }
    prevStepRef.current = currentStep;
  }, [currentStep, stateHistory]);

  // Always build from amplitudes to preserve phase information
  const displayData = amplitudes.map((a) => ({
    label: a.label,
    probability: parseFloat((a.probability * 100).toFixed(2)),
    raw: a.probability,
    phase: a.phase,
  }));

  return (
    <div className={`panel statevector-panel ${animatingCollapse ? 'collapsing' : ''}`}>
      <div className="sv-header">
        <h2 className="panel-title">
          <span className="title-icon">ψ</span> State Vector
        </h2>
        <div className="view-toggle">
          <button
            className={`toggle-btn ${viewMode === 'histogram' ? 'active' : ''}`}
            onClick={() => setViewMode('histogram')}
          >
            📊 Bars
          </button>
          <button
            className={`toggle-btn ${viewMode === 'circles' ? 'active' : ''}`}
            onClick={() => setViewMode('circles')}
          >
            ◎ Disks
          </button>
          <button
            className={`toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
          >
            📋 Table
          </button>
        </div>
      </div>

      {amplitudes.length === 0 ? (
        <div className="sv-placeholder">
          <p>Run a circuit or load an algorithm to see the state vector</p>
        </div>
      ) : viewMode === 'circles' ? (
        <PhaseDisks amplitudes={amplitudes} />
      ) : viewMode === 'histogram' ? (
        <div className="sv-chart">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={displayData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
              <XAxis
                dataKey="label"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={{ stroke: '#334155' }}
              />
              <YAxis
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={{ stroke: '#334155' }}
                label={{ value: '%', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                domain={[0, 100]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#e2e8f0',
                }}
                formatter={(value: unknown, _: any, props: any) => {
                  if (props?.payload?.phase !== undefined) {
                    const phaseDeg = (props.payload.phase * 180 / Math.PI).toFixed(0);
                    return [`${value}% (Phase: ${phaseDeg}°)`, 'Probability'];
                  }
                  return [`${value}%`, 'Probability'];
                }}
              />
              <Bar dataKey="probability" radius={[4, 4, 0, 0]}>
                {displayData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={entry.raw > 0.01 ? phaseColor(entry.phase) : '#1e293b'}
                    fillOpacity={Math.max(0.3, entry.raw)}
                    className={animatingCollapse && entry.raw < 0.01 ? 'bar-collapse' : ''}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="sv-table-container">
          <table className="sv-table">
            <thead>
              <tr>
                <th>Basis</th>
                <th>Amplitude</th>
                <th>|α|</th>
                <th>Phase</th>
                <th className="prob-col">Probability</th>
              </tr>
            </thead>
            <tbody>
              {amplitudes.map((a) => (
                <tr key={a.index} className={a.probability > 0.01 ? 'active-row' : ''}>
                  <td className="basis-cell">{a.label}</td>
                  <td className="amp-cell">
                    {a.real.toFixed(3)}{a.imag >= 0 ? '+' : ''}{a.imag.toFixed(3)}i
                  </td>
                  <td>{a.magnitude.toFixed(4)}</td>
                  <td>
                    <span
                      className="phase-dot"
                      style={{ backgroundColor: phaseColor(a.phase) }}
                    />
                    {(a.phase * 180 / Math.PI).toFixed(1)}°
                  </td>
                  <td className="prob-col">
                    <div className="prob-bar-container">
                      <div
                        className="prob-bar"
                        style={{ width: `${a.probability * 100}%` }}
                      />
                      <span>{(a.probability * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
