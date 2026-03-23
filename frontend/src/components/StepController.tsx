/**
 * StepController — Step-by-step execution controls
 * Previous / Next / Play / Reset with step counter and speed slider.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useSimStore } from '../store/useSimStore';

export default function StepController() {
  const {
    currentStep,
    totalSteps,
    isPlaying,
    playSpeed,
    stateHistory,
    nextStep,
    prevStep,
    resetStep,
    setPlaying,
    setPlaySpeed,
    setCurrentStep,
  } = useSimStore();

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopAutoPlay = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setPlaying(false);
  }, [setPlaying]);

  // Auto-play
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        const store = useSimStore.getState();
        if (store.currentStep >= store.totalSteps - 1) {
          stopAutoPlay();
        } else {
          store.nextStep();
        }
      }, playSpeed);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, playSpeed, stopAutoPlay]);

  const togglePlay = () => {
    if (isPlaying) {
      stopAutoPlay();
    } else {
      if (currentStep >= totalSteps - 1) {
        resetStep();
      }
      setPlaying(true);
    }
  };

  const hasSteps = stateHistory.length > 1;
  const stepLabel = hasSteps
    ? `Step ${currentStep} of ${totalSteps - 1}`
    : 'No simulation loaded';

  // Get info about current step from algorithm result
  const { algorithmResult } = useSimStore();
  const circuit = (algorithmResult as Record<string, unknown>)?.circuit as Array<{label?: string}> | undefined;
  const currentStepLabel = circuit && currentStep > 0 && currentStep <= circuit.length
    ? circuit[currentStep - 1]?.label || ''
    : currentStep === 0 ? 'Initial state |0⟩⊗ⁿ' : '';

  return (
    <div className="step-controller">
      <div className="step-buttons">
        <button
          className="step-btn"
          onClick={resetStep}
          disabled={!hasSteps || currentStep === 0}
          title="Reset to start"
        >
          ⏮
        </button>
        <button
          className="step-btn"
          onClick={prevStep}
          disabled={!hasSteps || currentStep === 0}
          title="Previous step"
        >
          ◀
        </button>
        <button
          className={`step-btn play-btn ${isPlaying ? 'playing' : ''}`}
          onClick={togglePlay}
          disabled={!hasSteps}
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? '⏸' : '▶'}
        </button>
        <button
          className="step-btn"
          onClick={nextStep}
          disabled={!hasSteps || currentStep >= totalSteps - 1}
          title="Next step"
        >
          ▶
        </button>
        <button
          className="step-btn"
          onClick={() => setCurrentStep(totalSteps - 1)}
          disabled={!hasSteps || currentStep >= totalSteps - 1}
          title="Go to end"
        >
          ⏭
        </button>
      </div>

      <div className="step-info">
        <span className="step-counter">{stepLabel}</span>
        {currentStepLabel && (
          <span className="step-label">{currentStepLabel}</span>
        )}
      </div>

      {/* Progress bar */}
      {hasSteps && (
        <div className="step-progress">
          <input
            type="range"
            min={0}
            max={totalSteps - 1}
            value={currentStep}
            onChange={(e) => setCurrentStep(parseInt(e.target.value))}
            className="progress-slider"
          />
        </div>
      )}

      {/* Speed control */}
      <div className="speed-control">
        <label>Speed</label>
        <input
          type="range"
          min={100}
          max={3000}
          step={100}
          value={3100 - playSpeed}
          onChange={(e) => setPlaySpeed(3100 - parseInt(e.target.value))}
          className="speed-slider"
        />
        <span className="speed-label">
          {playSpeed < 500 ? 'Fast' : playSpeed < 1500 ? 'Normal' : 'Slow'}
        </span>
      </div>
    </div>
  );
}
