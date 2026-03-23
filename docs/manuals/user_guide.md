# Comprehensive User Manual: Quantum Protocol & Algorithm Simulator

Welcome to the **Quantum Protocol & Algorithm Simulator** — an interactive, physics-accurate platform designed to teach quantum mechanics, computing, and cryptography natively in your browser. This document provides an exhaustive breakdown of the interface, the underlying quantum theory, and exact instructions on how to leverage the tool.

---

## Part 1: Interface & Core Features

When you launch the application at `http://localhost:5173`, you are presented with a 4-panel dashboard designed for maximum visibility into the mathematical engine.

### 1.1 Top Navigation Bar
- **System Qubit Counter**: A dropdown at the top-left allowing you to define the mathematical dimension of your Hilbert space. You can select between 1 and 5 qubits. (Note: 5 qubits requires the engine to compute a $2^5 = 32$ dimension complex vector in real-time).
- **Global Reset Button**: The circular icon (Arrow-Circle-Left). Clicking this instantly destroys the current circuit and resets the quantum state vector to absolute $|00 \dots 0\rangle$.
- **Connection Indicator**: A glowing dot indicating WebSocket health. If it is **Green**, the UI is connected to the Python/FastAPI engine. If **Red**, the Math Engine is offline and circuits will not simulate.

### 1.2 The Gate Palette (Circuit Editor Toolbar)
This is your toolkit for manually manipulating quantum states.
- **Selection Tool (Cursor Icon)**: The default mode. Allows you to click gates already placed on the wire to inspect them.
- **Eraser Tool (Trash Icon)**: Click this, then click any gate on the wire to delete it from the circuit. The math engine instantly recalculates the new state history.
- **Gate Buttons (`H`, `X`, `Y`, `Z`, `Rx`, `Ry`, `Rz`, `P`, `CNOT`, `CZ`, `SWAP`, `CCX`)**: Clicking any of these selects the gate for placement. It will gain a bright cyan border.
- **Parameter Input**: If you select a rotation gate (`Rx`, `Ry`, `Rz`, `P`), a numeric input box appears. You must define the phase angle $\theta$ in radians (e.g., `3.14159` for $\pi$, `1.5708` for $\pi/2$) before you can place the gate.

### 1.3 The Circuit Canvas
The interactive SVG board where algorithms are built.
- **Qubit Wires (Horizontal Lines)**: Labeled `q0`, `q1`... down to `qn`. In this simulator, `q0` is the **most significant bit** (Big-Endian notation).
1. **Placing Single-Qubit Gates**: With a single-qubit gate selected (e.g., `H`), simply click anywhere on a black wire. The gate drops into the first available time-step column.
2. **Placing Multi-Qubit Gates**: With a multi-qubit gate selected (e.g., `CNOT`), you must click exactly **twice**. Your first click on a wire sets the **Control** qubit (represented by a small dot). Your second click sets the **Target** qubit (represented by a large cross/box). A vertical entanglement line is drawn connecting them.

### 1.4 The Step Controller (Bottom Panel)
Quantum execution in this simulator is not instantaneous; it is temporal.
- **Play Button (▶)**: Begins autonomous forward playback. The simulator applies one gate column per tick.
- **Pause Button (⏸)**: Halts automatic playback.
- **Step Forward (►|) / Step Backward (|◄)**: Manually scrub time forwards or backward. This allows you to inspect the exact quantum state *between* operations.
- **Speed Slider**: Accelerates or decelerates the automatic playback `Play` rate.

### 1.5 State Visualization Panels
- **Bloch Sphere (Right Panel)**: An interactive 3D WebGL sphere for each individual qubit. It plots the Reduced Density Matrix Bloch Vector $(x, y, z)$. You can drag to rotate the camera.
- **Statevector Data (Bottom Left)**: Click the **Table Icon** to view raw mathematical data (Real, Imaginary, Magnitude, Phase) for the $2^n$ basis states spanning the global wave function $|\psi\rangle$.
- **Probability Data (Bottom Left)**: Click the **Bar Chart Icon** to view the Born Rule probability histogram. This dictates the statistical likelihood of measuring a specific classical bitstring if you were to collapse the wave function at that exact temporal step.

---

## Part 2: Quantum Theory & Available Gates

Quantum Computing replaces classical bits (0 or 1) with **Qubits** in superposition.

The mathematical state of a single qubit is denoted:
$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$
Where $\alpha$ and $\beta$ are complex numbers called **amplitudes**. The condition $|\alpha|^2 + |\beta|^2 = 1$ ensures conservation of probability.

### 2.1 Single-Qubit Gates
These gates execute unitary $2 \times 2$ matrix multiplication on a specific wire.

* **Hadamard (`H`)**: The superposition gate. It puts a definite state into an equal mixture of 0 and 1. If applied to $|0\rangle$, the Bloch vector rotates from the North Pole down to the Equator at the $|+\rangle$ state.
  * *UI Interaction*: Click `H`, click `q0`. Watch the probability chart split to 50/50.
* **Pauli-X (`X`)**: The quantum `NOT` gate. It flips $|0\rangle \leftrightarrow |1\rangle$. Visually, it rotates the Bloch vector $180^\circ$ around the X-axis.
* **Pauli-Y (`Y`) / Pauli-Z (`Z`)**: Phase flip gates. `Z` applies a $-1$ phase to the $|1\rangle$ component, rotating $180^\circ$ around the Z-axis. `Y` is a combination resulting in $X$ and $Z$ flips with a complex $i$ coefficient.
* **Rotation Gates (`Rx`, `Ry`, `Rz`)**: Allow you to continuously rotate the Bloch vector around an axis by the parameter strictly defined in the UI's parameter box.
* **Phase Gate (`P`)**: A generalized `Z` gate that applies a rotation of angle $\theta$ strictly to the $|1\rangle$ state while leaving $|0\rangle$ untouched.

### 2.2 Multi-Qubit Gates (Entanglement)
These gates create **Entanglement**, a core quantum phenomenon where the state of one qubit cannot be described independently of the state of the other.

* **Controlled-NOT (`CNOT`)**: The primary entanglement gate. It flips the **Target** qubit if and only if the **Control** qubit is in the state $|1\rangle$. 
  * *Theory Check*: Apply a Hadamard (`H`) to `q0`, then apply a `CNOT` with `q0` as control and `q1` as target. This creates a **Bell State** $\frac{|00\rangle + |11\rangle}{\sqrt{2}}$. 
  * *UI Observation*: Notice how the Bloch spheres vector lengths shrink when entangled. The density matrices of the individual bounded qubits lose "purity", representing that information now resides globally in correlations, not locally.
* **Controlled-Z (`CZ`)**: Applies a `Z` phase flip to the target if the control is $|1\rangle$.
* **SWAP (`SWAP`)**: Flips the physical states of two qubits.
* **Toffoli (`CCX`)**: A 3-qubit gate. It flips the target if and only if **both** control qubits are $|1\rangle$. Universally classical-computation complete. (Requires selecting a control, a second control, and a target in the UI).

---

## Part 3: Pre-Built Algorithms & Protocols

The left "Algorithm Selector" panel automatically injects complex circuits into the canvas to demonstrate famous quantum computing algorithms. Click the accordion header to expand any algorithm, configure its parameters, and click the blue **Run** button at the bottom of the card.

### 3.1 Deutsch-Jozsa Algorithm
**The Theory:** How can you tell if a black-box function (an "Oracle") is *Constant* (returns all 0s or all 1s) or *Balanced* (returns exactly half 0s and half 1s)? Claisscally, for $n$ bits, it takes $2^{n-1} + 1$ queries. Quantumly, Deutsch-Jozsa solves it in exactly **1 query** utilizing massive quantum interference and phase kickback.
**Using the UI:**
1. Set the `Number of Input Qubits` ($n$).
2. Choose an oracle type: `constant_0` or `balanced`.
3. Click **Run Algorithm**.
4. Press **Play** in the bottom right. Watch as parallel Hadamards put all inputs into superposition, the Oracle applies phase shifts mapping $f(x)$ into the auxiliary qubit's phase, and a final Hadamard array causes constructive/destructive interference. The final measurement probability will be 100% $|00 \dots 0\rangle$ if Constant, and 0% if Balanced.

### 3.2 Grover's Search Algorithm
**The Theory:** Searching an unsorted database of size $N$ classically takes $O(N)$ time. Grover's algorithm uses amplitude amplification to find the target in $O(\sqrt{N})$ time—a quadratic speedup.
**Using the UI:**
1. Define the search space size via `Number of Qubits` (e.g., 3 qubits = $2^3 = 8$ possible items).
2. Type the decimal integer of the state you want to "find" in `Target States` (e.g., 5 = $|101\rangle$).
3. Click **Run Algorithm**.
4. As you scrub the timeline using the `Step Forward` button, observe the Probability Chart. You will see the probability of the target state begin at uniform ($1/8$), dip slightly due to the Oracle phase flip, and then *violently shoot upwards* as the Diffusion Operator reflects probabilities around the mean.

### 3.3 Quantum Teleportation
**The Theory:** Teleportation transfers the exact quantum state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ from Alice to Bob, across any distance, using shared entanglement (a Bell pair) and the transmission of just 2 classical bits.
**Using the UI:**
1. The protocol fixes the system at 3 qubits (`q0` = message, `q1` = Alice's half of Bell pair, `q2` = Bob's half).
2. Use the **Polar ($\theta$)** and **Azimuthal ($\phi$)** sliders to arbitrarily arrange the red Bloch Vector of the message in `q0` that you wish to teleport.
3. Click **Run Protocol**.
4. Step through the timeline. Watch `q1` and `q2` become entangled. Watch Alice apply a CNOT and Hadamard to entangle her message with her Bell half. At the end, Bob receives classical bits and applies conditional $X$ or $Z$ gates. By the final step, look at Bob's Bloch sphere (`q2`)—it perfectly mirrors the starting state of `q0`, despite them never interacting directly!

### 3.4 BB84 Quantum Key Distribution (Cryptography)
**The Theory:** The BB84 protocol allows Alice and Bob to establish a perfectly secure shared cryptographic encryption key by transmitting polarized single photons. It relies on the *No-Cloning Theorem* and *Measurement Collapse*—if an eavesdropper (Eve) tries to read the quantum bits in transit, she physically alters them, alerting Alice and Bob to her presence.
**Using the UI:**
1. Set the `Number of Bits` to exchange over the quantum fiber.
2. Toggle the `Eavesdropper (Eve) Present` switch ON or OFF to simulate a wiretap attempt.
3. Click **Run Protocol**.
4. The algorithm does not render a visual circuit directly (as calculating massive $N>5$ qubit circuits crashes browsers). Instead, it runs the statistical analysis through the engine and returns a dedicated cryptographic report modal detailing the generated Key, the Quantum Bit Error Rate (QBER), and whether the channel was deemed secure or compromised.

### 3.5 Quantum Random Number Generator (QRNG)
**The Theory:** Classical computers can never generate true random numbers; they use deterministic pseudo-random algorithms (PRNG). Quantum Mechanics is fundamentally probabilistic. Measuring a $|+\rangle$ state yields a 0 or 1 with absolute physical randomness.
**Using the UI:**
1. Select the `Number of Random Bits` desired.
2. Click **Run Algorithm**.
3. The UI will render parallel Hadamard gates, placing all target qubits into the equatorial state, followed by immediate measurement. Look at the measurement report indicating the generated bitstring result.
