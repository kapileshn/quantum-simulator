/**
 * AlgorithmSelector — Left panel component
 * Collapsible cards for each quantum algorithm/protocol with parameter inputs.
 */

import { useState, useEffect } from 'react';
import { useSimStore } from '../store/useSimStore';
import type { AlgorithmInfo } from '../types/quantum';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Icons for each algorithm category
const ALGO_ICONS: Record<string, string> = {
  deutsch_jozsa: '⚡',
  grover: '🔍',
  teleportation: '🌀',
  bb84: '🔐',
  qrng: '🎲',
};

export default function AlgorithmSelector() {
  const {
    algorithms,
    setAlgorithms,
    selectedAlgorithm,
    setSelectedAlgorithm,
    setStateHistory,
    algorithmResult,
    setAlgorithmResult,
    nQubits,
    setNQubits,
    setCurrentStep,
  } = useSimStore();

  const [params, setParams] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  // Fetch available algorithms on mount
  useEffect(() => {
    fetch(`${API_URL}/api/algorithms`)
      .then((r) => r.json())
      .then((data) => setAlgorithms(data.algorithms))
      .catch((e) => console.error('Failed to load algorithms:', e));
  }, [setAlgorithms]);

  const handleSelect = (algo: AlgorithmInfo) => {
    setSelectedAlgorithm(algo.name);
    setExpanded(expanded === algo.name ? null : algo.name);
    // Initialize default params
    const defaults: Record<string, unknown> = {};
    algo.parameters.forEach((p) => {
      defaults[p.name] = p.default;
    });
    setParams(defaults);
  };

  const handleParamChange = (name: string, value: unknown) => {
    setParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleRun = async () => {
    if (!selectedAlgorithm) return;
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/algorithms/${selectedAlgorithm}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: selectedAlgorithm, params }),
      });
      const data = await res.json();

      if (data.success && data.result) {
        setAlgorithmResult(data.result);
        if (data.result.state_history) {
          setStateHistory(data.result.state_history);
          // Auto-forward to end to immediately show visualization
          setCurrentStep(data.result.state_history.length - 1);
        }
      }
    } catch (e) {
      console.error('Algorithm execution failed:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel algorithm-selector">
      <h2 className="panel-title">
        <span className="title-icon">◈</span> Algorithms & Protocols
      </h2>

      {/* Qubit count selector */}
      <div className="qubit-selector">
        <label>Qubits</label>
        <div className="qubit-buttons">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              className={`qubit-btn ${nQubits === n ? 'active' : ''}`}
              onClick={() => setNQubits(n)}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Algorithm list */}
      <div className="algo-list">
        {algorithms.length === 0 && (
          <div className="algo-loading">
            <div className="spinner" />
            <span>Loading algorithms...</span>
          </div>
        )}

        {algorithms.map((algo) => (
          <div
            key={algo.name}
            className={`algo-card ${selectedAlgorithm === algo.name ? 'selected' : ''}`}
          >
            <button
              className="algo-header"
              onClick={() => handleSelect(algo)}
            >
              <span className="algo-icon">{ALGO_ICONS[algo.name] || '⚛'}</span>
              <div className="algo-info">
                <span className="algo-name">{algo.display_name}</span>
                <span className="algo-category">{algo.category}</span>
              </div>
              <span className={`algo-chevron ${expanded === algo.name ? 'open' : ''}`}>
                ›
              </span>
            </button>

            {expanded === algo.name && (
              <div className="algo-body">
                <p className="algo-desc">{algo.description}</p>

                {/* Parameter inputs */}
                <div className="algo-params">
                  {algo.parameters.map((p) => (
                    <div key={p.name} className="param-field">
                      <label>{p.description}</label>
                      {p.type === 'int' && (
                        <input
                          type="number"
                          min={p.min}
                          max={p.max}
                          value={params[p.name] as number ?? p.default as number}
                          onChange={(e) => handleParamChange(p.name, parseInt(e.target.value))}
                        />
                      )}
                      {p.type === 'float' && (
                        <input
                          type="number"
                          step="0.1"
                          min={p.min}
                          max={p.max}
                          value={params[p.name] as number ?? p.default as number}
                          onChange={(e) => handleParamChange(p.name, parseFloat(e.target.value))}
                        />
                      )}
                      {p.type === 'bool' && (
                        <label className="toggle">
                          <input
                            type="checkbox"
                            checked={params[p.name] as boolean ?? p.default as boolean}
                            onChange={(e) => handleParamChange(p.name, e.target.checked)}
                          />
                          <span className="toggle-slider" />
                        </label>
                      )}
                      {p.type === 'select' && (
                        <select
                          value={params[p.name] as string ?? p.default as string}
                          onChange={(e) => handleParamChange(p.name, e.target.value)}
                        >
                          {p.options?.map((opt) => (
                            <option key={opt} value={opt}>{opt.replace(/_/g, ' ')}</option>
                          ))}
                        </select>
                      )}
                      {p.type === 'int_list' && (
                        <input
                          type="text"
                          placeholder="e.g., 3,5,7"
                          value={
                            Array.isArray(params[p.name])
                              ? (params[p.name] as number[]).join(',')
                              : String(p.default)
                          }
                          onChange={(e) =>
                            handleParamChange(
                              p.name,
                              e.target.value.split(',').map((v) => parseInt(v.trim())).filter((v) => !isNaN(v))
                            )
                          }
                        />
                      )}
                    </div>
                  ))}
                </div>

                <button
                  className="run-btn"
                  onClick={handleRun}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner small" /> Running...
                    </>
                  ) : (
                    <>▶ Run Algorithm</>
                  )}
                </button>

                {algorithmResult?.algorithm === algo.name && Boolean(algorithmResult?.summary) && (
                  <div className="algo-summary">
                    <div className="algo-summary-title">Result &amp; Formula</div>
                    {String(algorithmResult.summary).split('\n').map((line, i) => {
                      const isFormula = line.includes('Formula:');
                      return (
                        <div
                          key={i}
                          className={isFormula ? 'algo-formula' : 'algo-summary-line'}
                        >
                          {line.replace('Formula:', '')}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
