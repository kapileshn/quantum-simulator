/**
 * BlochSphere — Right panel component
 * Three.js/WebGL Bloch sphere visualization per qubit.
 *
 * Features:
 *   - Animated arrow with smooth interpolation (slerp)
 *   - Trajectory trail (last N positions traced as a fading line)
 *   - 3D in-scene entanglement web (glowing lines between entangled spheres)
 *   - Cross-component qubit highlighting (glow ring when gate hovered)
 *   - Purity/entanglement badge
 */

import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Text, Line } from '@react-three/drei';
import * as THREE from 'three';
import { useSimStore } from '../store/useSimStore';

const TRAIL_LENGTH = 18;

interface BlochArrowProps {
  x: number;
  y: number;
  z: number;
  purity: number;
}

// Animated arrow with smooth slerp
function BlochArrow({ x, y, z, purity }: BlochArrowProps) {
  const meshRef = useRef<THREE.Group>(null);
  const targetPos = useMemo(() => new THREE.Vector3(x, z, -y), [x, y, z]);
  const arrowLen = Math.sqrt(x * x + y * y + z * z);
  const color = purity > 0.9 ? '#00d4ff' : purity > 0.5 ? '#a855f7' : '#64748b';

  useFrame(() => {
    if (!meshRef.current) return;
    const dir = targetPos.clone().normalize();
    meshRef.current.quaternion.slerp(
      new THREE.Quaternion().setFromUnitVectors(
        new THREE.Vector3(0, 1, 0),
        dir.length() > 0.001 ? dir : new THREE.Vector3(0, 1, 0)
      ),
      0.12
    );
  });

  if (purity < 0.15) {
    return (
      <group>
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.06, 16, 16]} />
          <meshStandardMaterial color="#a855f7" emissive="#a855f7" emissiveIntensity={0.8} />
        </mesh>
      </group>
    );
  }

  return (
    <group ref={meshRef}>
      <mesh position={[0, arrowLen * 0.4, 0]}>
        <cylinderGeometry args={[0.03, 0.03, arrowLen * 0.8, 8]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} />
      </mesh>
      <mesh position={[0, arrowLen * 0.85, 0]}>
        <coneGeometry args={[0.09, 0.18, 8]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
      </mesh>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial color="#facc15" emissive="#facc15" emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
}

// Fading trajectory trail
function BlochTrail({ trail }: { trail: THREE.Vector3[] }) {
  if (trail.length < 2) return null;
  return (
    <Line
      points={trail}
      color="#00d4ff"
      lineWidth={1.5}
      transparent
      opacity={0.35}
      dashed={false}
    />
  );
}

// Animated pulsing entanglement ring (shown when highlighted from external hover)
function HighlightRing({ active }: { active: boolean }) {
  const ringRef = useRef<THREE.Mesh<THREE.TorusGeometry, THREE.MeshBasicMaterial>>(null);
  useFrame(({ clock }) => {
    if (!ringRef.current) return;
    const t = clock.getElapsedTime();
    ringRef.current.material.opacity = active ? 0.35 + 0.35 * Math.sin(t * 4) : 0;
  });
  return (
    <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[1.05, 0.015, 8, 64]} />
      <meshBasicMaterial color="#facc15" transparent opacity={0} />
    </mesh>
  );
}

interface SphereSceneProps extends BlochArrowProps {
  trail: THREE.Vector3[];
  highlighted: boolean;
}

function SphereScene({ x, y, z, purity, trail, highlighted }: SphereSceneProps) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={0.8} />

      {/* Sphere body */}
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <meshStandardMaterial
          color={highlighted ? '#1a1a2e' : '#1e293b'}
          transparent
          opacity={highlighted ? 0.25 : 0.15}
          side={THREE.DoubleSide}
        />
      </mesh>
      {/* Wireframe */}
      <mesh>
        <sphereGeometry args={[1.001, 16, 16]} />
        <meshBasicMaterial
          color={highlighted ? '#facc15' : '#334155'}
          wireframe
          transparent
          opacity={highlighted ? 0.5 : 0.3}
        />
      </mesh>

      {/* Axes */}
      <Line points={[[-1.3, 0, 0], [1.3, 0, 0]]} color="#ef4444" lineWidth={1} transparent opacity={0.5} />
      <Line points={[[0, -1.3, 0], [0, 1.3, 0]]} color="#22c55e" lineWidth={1} transparent opacity={0.5} />
      <Line points={[[0, 0, -1.3], [0, 0, 1.3]]} color="#3b82f6" lineWidth={1} transparent opacity={0.5} />

      <Text position={[1.5, 0, 0]} fontSize={0.15} color="#ef4444">x</Text>
      <Text position={[0, 1.5, 0]} fontSize={0.15} color="#22c55e">|0⟩</Text>
      <Text position={[0, -1.5, 0]} fontSize={0.15} color="#22c55e">|1⟩</Text>
      <Text position={[0, 0, -1.5]} fontSize={0.15} color="#3b82f6">y</Text>

      {/* Equator ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1, 0.005, 8, 64]} />
        <meshBasicMaterial color="#475569" transparent opacity={0.3} />
      </mesh>

      {/* Highlight ring (cross-component) */}
      <HighlightRing active={highlighted} />

      {/* Trajectory trail */}
      <BlochTrail trail={trail} />

      {/* State arrow */}
      <BlochArrow x={x} y={y} z={z} purity={purity} />
    </>
  );
}

// Detect entanglement pairs from Bloch coords
function findEntangledPairs(
  blochData: Array<{ x: number; y: number; z: number; purity: number }>
): [number, number][] {
  const pairs: [number, number][] = [];
  const entangledQubits = blochData
    .map((c, i) => ({ index: i, purity: c.purity }))
    .filter(q => q.purity < 0.95);
  for (let i = 0; i < entangledQubits.length; i++) {
    for (let j = i + 1; j < entangledQubits.length; j++) {
      pairs.push([entangledQubits[i].index, entangledQubits[j].index]);
    }
  }
  return pairs;
}

export default function BlochSphere() {
  const { stateHistory, currentStep, nQubits, hoveredGateTargets } = useSimStore();

  const currentState = stateHistory[currentStep];
  const blochData = currentState?.bloch_coords || [];
  const entangledPairs = findEntangledPairs(blochData);

  // Per-qubit trail history (stores last TRAIL_LENGTH Bloch vectors)
  const trailsRef = useRef<Map<number, THREE.Vector3[]>>(new Map());

  // Update trails whenever step changes
  useEffect(() => {
    blochData.forEach((coords, i) => {
      if (!trailsRef.current.has(i)) trailsRef.current.set(i, []);
      const trail = trailsRef.current.get(i)!;
      const newPoint = new THREE.Vector3(coords.x, coords.z, -coords.y);
      // Only push if moved significantly
      const last = trail[trail.length - 1];
      if (!last || last.distanceTo(newPoint) > 0.05) {
        trail.push(newPoint.clone());
        if (trail.length > TRAIL_LENGTH) trail.shift();
      }
    });
    // Clear trails for qubits no longer in the system
    for (const key of trailsRef.current.keys()) {
      if (key >= nQubits) trailsRef.current.delete(key);
    }
  }, [currentStep, blochData, nQubits]);

  // Force re-render when trails update
  const [, forceUpdate] = useState(0);
  useEffect(() => { forceUpdate(v => v + 1); }, [currentStep]);

  return (
    <div className="panel bloch-panel">
      <h2 className="panel-title">
        <span className="title-icon">◉</span> Bloch Sphere
      </h2>

      {/* Entanglement Web indicator */}
      {entangledPairs.length > 0 && (
        <div className="entanglement-web">
          <div className="ent-web-label">⚡ Entanglement Links</div>
          <div className="ent-web-pairs">
            {entangledPairs.map(([a, b], i) => (
              <div key={i} className="ent-pair">
                <span className="ent-qubit">q{a}</span>
                <span className="ent-connector">⟷</span>
                <span className="ent-qubit">q{b}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bloch-grid">
        {Array.from({ length: nQubits }, (_, i) => {
          const coords = blochData[i] || { x: 0, y: 0, z: 1, purity: 1 };
          const isEntangled = coords.purity < 0.95;
          const isHighlighted = hoveredGateTargets.includes(i);
          const trail = trailsRef.current.get(i) || [];

          return (
            <div
              key={i}
              className={`bloch-item ${isHighlighted ? 'bloch-highlighted' : ''}`}
            >
              <div className="bloch-label">q{i}</div>
              <div className={`bloch-canvas ${isEntangled ? 'bloch-entangled' : ''} ${isHighlighted ? 'bloch-canvas-highlighted' : ''}`}>
                <Canvas
                  camera={{ position: [2.5, 2, 2.5], fov: 40 }}
                  gl={{ antialias: true, alpha: true }}
                  style={{ background: 'transparent' }}
                >
                  <SphereScene
                    x={coords.x}
                    y={coords.y}
                    z={coords.z}
                    purity={coords.purity}
                    trail={trail}
                    highlighted={isHighlighted}
                  />
                </Canvas>
                {isEntangled && (
                  <div className="bloch-entangled-badge">
                    <span className="entangled-icon">⚡</span>
                    <span>Entangled</span>
                  </div>
                )}
              </div>
              <div className="bloch-coords-display">
                {isEntangled ? (
                  <span className="purity-display">
                    Purity: {(coords.purity * 100).toFixed(0)}% — Mixed State
                  </span>
                ) : (
                  <span>
                    x: {coords.x.toFixed(2)}&nbsp;|&nbsp; y: {coords.y.toFixed(2)}&nbsp;|&nbsp; z: {coords.z.toFixed(2)}
                  </span>
                )}
              </div>
            </div>
          );
        })}
        {blochData.length === 0 && (
          <div className="bloch-placeholder">
            <span>🌐</span>
            <p>Run a circuit or algorithm to see Bloch sphere visualization</p>
          </div>
        )}
      </div>
    </div>
  );
}
