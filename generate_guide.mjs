import {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, TableRow, TableCell, Table,
  WidthType, ShadingType, PageBreak, Tab, TabStopPosition,
  TabStopType, Footer, Header, NumberFormat,
  convertInchesToTwip, ExternalHyperlink, ImageRun,
} from "docx";
import * as fs from "fs";

// ── Color palette ──
const BLUE = "1a56db";
const DARK = "1f2937";
const GRAY = "6b7280";
const LIGHT_BG = "f0f4ff";
const WHITE = "ffffff";
const ACCENT = "7c3aed";

// ── Reusable builders ──
function title(text) {
  return new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({ text, bold: true, size: 56, color: BLUE, font: "Calibri" })],
    alignment: AlignmentType.CENTER,
  });
}
function subtitle(text) {
  return new Paragraph({
    spacing: { after: 400 },
    children: [new TextRun({ text, size: 28, color: GRAY, font: "Calibri", italics: true })],
    alignment: AlignmentType.CENTER,
  });
}
function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 480, after: 200 },
    children: [new TextRun({ text, bold: true, size: 36, color: BLUE, font: "Calibri" })],
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLUE } },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, color: DARK, font: "Calibri" })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 24, color: ACCENT, font: "Calibri" })],
  });
}
function para(...runs) {
  return new Paragraph({
    spacing: { after: 160, line: 320 },
    children: runs.map(r =>
      typeof r === "string"
        ? new TextRun({ text: r, size: 22, font: "Calibri", color: DARK })
        : r
    ),
  });
}
function bold(text) {
  return new TextRun({ text, bold: true, size: 22, font: "Calibri", color: DARK });
}
function italic(text) {
  return new TextRun({ text, italics: true, size: 22, font: "Calibri", color: DARK });
}
function code(text) {
  return new TextRun({ text, size: 20, font: "Consolas", color: "b91c1c" });
}
function bullet(text, level = 0) {
  return new Paragraph({
    bullet: { level },
    spacing: { after: 80, line: 300 },
    children: [new TextRun({ text, size: 22, font: "Calibri", color: DARK })],
  });
}
function bulletRuns(runs, level = 0) {
  return new Paragraph({
    bullet: { level },
    spacing: { after: 80, line: 300 },
    children: runs.map(r =>
      typeof r === "string"
        ? new TextRun({ text: r, size: 22, font: "Calibri", color: DARK })
        : r
    ),
  });
}
function mathBlock(text) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    alignment: AlignmentType.CENTER,
    indent: { left: convertInchesToTwip(0.5), right: convertInchesToTwip(0.5) },
    shading: { type: ShadingType.CLEAR, fill: LIGHT_BG },
    children: [new TextRun({ text, size: 22, font: "Cambria Math", color: DARK, italics: true })],
  });
}
function gateRow(name, matrix, desc) {
  return new TableRow({
    children: [
      new TableCell({
        width: { size: 1200, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: LIGHT_BG },
        children: [new Paragraph({ children: [new TextRun({ text: name, bold: true, size: 20, font: "Consolas" })] })],
      }),
      new TableCell({
        width: { size: 3600, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun({ text: matrix, size: 18, font: "Consolas" })] })],
      }),
      new TableCell({
        width: { size: 4800, type: WidthType.DXA },
        children: [new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: desc, size: 20, font: "Calibri" })] })],
      }),
    ],
  });
}
function headerRow(...cells) {
  return new TableRow({
    tableHeader: true,
    children: cells.map(c =>
      new TableCell({
        shading: { type: ShadingType.CLEAR, fill: BLUE },
        children: [new Paragraph({ children: [new TextRun({ text: c, bold: true, size: 20, font: "Calibri", color: WHITE })] })],
      })
    ),
  });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ── Build document ──
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Calibri", size: 22, color: DARK },
        paragraph: { spacing: { line: 300 } },
      },
    },
  },
  sections: [
    {
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(1),
            bottom: convertInchesToTwip(1),
            left: convertInchesToTwip(1.2),
            right: convertInchesToTwip(1.2),
          },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [new TextRun({ text: "Quantum Simulator \u2014 User Guide", size: 16, color: GRAY, font: "Calibri", italics: true })],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "Confidential \u2014 Quantum Protocol & Algorithm Simulator", size: 14, color: GRAY })],
            }),
          ],
        }),
      },
      children: [
        // ════════════════════════════════════════
        // COVER PAGE
        // ════════════════════════════════════════
        new Paragraph({ spacing: { before: 4000 }, children: [] }),
        title("Quantum Protocol & Algorithm Simulator"),
        subtitle("Comprehensive User Guide & Physics Reference"),
        new Paragraph({
          spacing: { before: 800 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Version 1.0  \u2022  2026", size: 24, color: GRAY, font: "Calibri" })],
        }),
        new Paragraph({
          spacing: { before: 200 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "An interactive, physics-accurate platform for learning quantum computing,\ncryptography, and quantum mechanics in the browser.", size: 22, color: DARK, font: "Calibri" })],
        }),

        pageBreak(),

        // ════════════════════════════════════════
        // TABLE OF CONTENTS (manual)
        // ════════════════════════════════════════
        h1("Table of Contents"),
        para("Part 1: Getting Started"),
        para("Part 2: Interface & Core Features"),
        para("Part 3: Complete Quantum Gate Reference & Physics"),
        para("Part 4: Pre-Built Algorithms & Protocols"),
        para("Part 5: The Mathematics Behind the Simulator"),
        para("Part 6: Troubleshooting & Tips"),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 1: GETTING STARTED
        // ════════════════════════════════════════
        h1("Part 1: Getting Started"),

        h2("1.1 Prerequisites"),
        bullet("Python 3.10 or later"),
        bullet("Node.js 18 or later"),
        bullet("A modern web browser (Chrome, Firefox, Edge)"),

        h2("1.2 Installation"),
        h3("Backend (Simulation Engine)"),
        para("Open a terminal in the ", code("quantum-simulator/"), " directory and run:"),
        mathBlock("pip install -r requirements.txt"),
        para("Start the FastAPI server:"),
        mathBlock("python -m uvicorn api.simulation_api:app --reload --port 8000"),

        h3("Frontend (React Dashboard)"),
        para("In a second terminal, navigate to ", code("frontend/"), " and run:"),
        mathBlock("npm install  &&  npm run dev"),
        para("The application launches at ", bold("http://localhost:5173"), ". The connection indicator in the top bar should glow ", bold("green"), " once both servers are running."),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 2: INTERFACE
        // ════════════════════════════════════════
        h1("Part 2: Interface & Core Features"),

        h2("2.1 Navigation Bar"),
        bulletRuns([bold("System Qubit Counter: "), "A dropdown (top-left) to set the dimension of your Hilbert space. Supports 1\u20135 qubits (up to 2\u2075 = 32 amplitudes)."]),
        bulletRuns([bold("Global Reset: "), "Circular arrow icon. Destroys the current circuit and resets the state vector to |\u03C8\u27E9 = |00\u20260\u27E9."]),
        bulletRuns([bold("Connection Indicator: "), "Green = WebSocket connected to backend. Red = backend offline."]),

        h2("2.2 Gate Palette (Circuit Editor Toolbar)"),
        para("The toolbar across the top of the circuit canvas provides:"),
        bulletRuns([bold("Selection Tool (Cursor): "), "Default mode. Click placed gates to inspect them."]),
        bulletRuns([bold("Eraser Tool (Trash): "), "Click any placed gate to delete it. The engine recalculates the state history."]),
        bulletRuns([bold("Gate Buttons: "), code("H"), ", ", code("X"), ", ", code("Y"), ", ", code("Z"), ", ", code("Rx"), ", ", code("Ry"), ", ", code("Rz"), ", ", code("P"), ", ", code("CNOT"), ", ", code("CZ"), ", ", code("SWAP"), ", ", code("CCX"), ". Click to select, then click a qubit wire to place."]),
        bulletRuns([bold("Parameter Input: "), "Appears for rotation gates (Rx, Ry, Rz, P). Enter the angle \u03B8 in radians before placing. The simulator validates against NaN inputs."]),
        bulletRuns([bold("Measure Button: "), "Adds a measurement operation that collapses the qubit to a classical bit."]),

        h2("2.3 Circuit Canvas"),
        para("The interactive SVG board where circuits are built. Qubit wires run horizontally, labeled ", code("q0"), " (most significant, big-endian) through ", code("qN"), "."),
        h3("Placing Single-Qubit Gates"),
        para("Select a gate (e.g., ", code("H"), "), then click any qubit wire. The gate appears at the next available time-step."),
        h3("Placing Two-Qubit Gates"),
        para("Select a 2-qubit gate (e.g., ", code("CNOT"), "), then click two different qubit wires sequentially. First click = control qubit (dot), second click = target qubit (box)."),
        h3("Placing Three-Qubit Gates"),
        para("Select ", code("CCX"), " (Toffoli), then click two qubit wires for the two controls. The third target qubit is auto-selected as the next available qubit that does not duplicate either control."),

        h2("2.4 Step Controller"),
        para("The bottom panel provides temporal control over circuit execution:"),
        bulletRuns([bold("Play (\u25B6): "), "Auto-advances one gate per tick."]),
        bulletRuns([bold("Pause (\u23F8): "), "Halts automatic playback."]),
        bulletRuns([bold("Step Forward / Backward: "), "Manually scrub through time. Inspect the exact quantum state between any operations."]),
        bulletRuns([bold("Speed Slider: "), "Controls the auto-play rate."]),

        h2("2.5 Visualization Panels"),
        h3("Bloch Sphere (Right Panel)"),
        para("An interactive 3D WebGL sphere for each qubit. Displays the Bloch vector (x, y, z) extracted from the reduced density matrix. The axes follow the standard right-handed convention:"),
        bullet("Z-axis (vertical): |0\u27E9 at north pole, |1\u27E9 at south pole"),
        bullet("X-axis (horizontal): |+\u27E9 at +X, |\u2212\u27E9 at \u2212X"),
        bullet("Y-axis (depth): |+i\u27E9 at +Y, |\u2212i\u27E9 at \u2212Y"),
        para("When qubits are entangled, the Bloch vector length shrinks below 1, representing a mixed state (loss of local purity)."),

        h3("Statevector Table"),
        para("Displays all 2\u207F amplitudes of the global wavefunction |\u03C8\u27E9:"),
        bullet("Basis state label (e.g., |01\u27E9)"),
        bullet("Real and imaginary parts of each amplitude \u03B1"),
        bullet("Magnitude |\u03B1| and phase arg(\u03B1)"),
        bullet("Born-rule probability |\u03B1|\u00B2"),

        h3("Probability Histogram"),
        para("Bar chart showing P(outcome) = |\u27E8outcome|\u03C8\u27E9|\u00B2 for every computational basis state. This is the distribution you would see if you performed a measurement at the current step."),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 3: GATE REFERENCE
        // ════════════════════════════════════════
        h1("Part 3: Complete Quantum Gate Reference"),
        para("Every gate in this simulator is a unitary matrix U satisfying U\u2020U = I (preserves probability). The simulator implements 17 gates, all verified for unitarity."),

        h2("3.1 Single-Qubit Gates (Fixed)"),
        para("These gates perform a 2\u00D72 unitary transformation on one qubit."),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            headerRow("Gate", "Matrix", "Description & Physics"),
            gateRow("I", "[[1, 0], [0, 1]]", "Identity. No operation. |0\u27E9 \u2192 |0\u27E9, |1\u27E9 \u2192 |1\u27E9"),
            gateRow("X", "[[0, 1], [1, 0]]", "Pauli-X (NOT). Bit flip: |0\u27E9 \u2194 |1\u27E9. 180\u00B0 rotation around X-axis on Bloch sphere."),
            gateRow("Y", "[[0, -i], [i, 0]]", "Pauli-Y. Combined bit+phase flip: |0\u27E9 \u2192 i|1\u27E9, |1\u27E9 \u2192 -i|0\u27E9. 180\u00B0 rotation around Y-axis."),
            gateRow("Z", "[[1, 0], [0, -1]]", "Pauli-Z. Phase flip: |1\u27E9 \u2192 -|1\u27E9. 180\u00B0 rotation around Z-axis."),
            gateRow("H", "(1/\u221A2)[[1,1],[1,-1]]", "Hadamard. Creates superposition: |0\u27E9 \u2192 (|0\u27E9+|1\u27E9)/\u221A2. Rotates from Z to X axis (north pole to equator)."),
            gateRow("S", "[[1, 0], [0, i]]", "S gate (\u221AZ). Phase gate at \u03C0/2: |1\u27E9 \u2192 i|1\u27E9. Quarter-turn around Z-axis. Equivalent to P(\u03C0/2)."),
            gateRow("S\u2020", "[[1, 0], [0, -i]]", "S-dagger. Inverse of S. Phase gate at -\u03C0/2. Equivalent to P(-\u03C0/2)."),
            gateRow("T", "[[1, 0], [0, e^(i\u03C0/4)]]", "T gate (\u221AS, \u03C0/8 gate). Phase gate at \u03C0/4. Equivalent to P(\u03C0/4)."),
            gateRow("T\u2020", "[[1, 0], [0, e^(-i\u03C0/4)]]", "T-dagger. Inverse of T. Phase gate at -\u03C0/4."),
          ],
        }),

        h2("3.2 Single-Qubit Gates (Parameterized)"),
        para("These gates take a continuous angle parameter \u03B8 (in radians)."),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            headerRow("Gate", "Matrix", "Description & Physics"),
            gateRow("P(\u03C6)", "[[1,0],[0,e^(i\u03C6)]]", "General phase gate. Applies phase e^(i\u03C6) to |1\u27E9. Generalizes S, T, and Z gates."),
            gateRow("Rx(\u03B8)", "[[cos\u03B8/2, -i\u00B7sin\u03B8/2], [-i\u00B7sin\u03B8/2, cos\u03B8/2]]", "X-axis rotation by \u03B8. At \u03B8=\u03C0: Rx(\u03C0)|0\u27E9 = -i|1\u27E9. Traces a great circle through |0\u27E9 and |1\u27E9 on Bloch sphere."),
            gateRow("Ry(\u03B8)", "[[cos\u03B8/2, -sin\u03B8/2], [sin\u03B8/2, cos\u03B8/2]]", "Y-axis rotation by \u03B8. Uniquely, this gate has only real entries \u2014 it rotates between |0\u27E9 and |1\u27E9 without introducing phases."),
            gateRow("Rz(\u03B8)", "[[e^(-i\u03B8/2), 0], [0, e^(i\u03B8/2)]]", "Z-axis rotation by \u03B8. Applies opposite phases to |0\u27E9 and |1\u27E9. The Bloch vector rotates in the XY-plane."),
          ],
        }),

        h2("3.3 Multi-Qubit Gates"),
        para("These gates create entanglement \u2014 quantum correlations that have no classical counterpart."),

        new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            headerRow("Gate", "Qubits", "Description & Physics"),
            gateRow("CNOT", "2 (control, target)", "Controlled-NOT. Flips target if control = |1\u27E9. The primary entangling gate. H(q0) + CNOT(q0,q1) creates the Bell state (\u03A6+) = (|00\u27E9+|11\u27E9)/\u221A2."),
            gateRow("CZ", "2 (control, target)", "Controlled-Z. Applies Z-phase to target if control = |1\u27E9. Symmetric: CZ(a,b) = CZ(b,a). Matrix: diag(1,1,1,-1)."),
            gateRow("SWAP", "2", "Exchanges the states of two qubits: |01\u27E9 \u2194 |10\u27E9. Can be decomposed into three CNOTs."),
            gateRow("CCX", "3 (ctrl, ctrl, tgt)", "Toffoli gate. Flips target only when BOTH controls = |1\u27E9. Universal for classical computation. |110\u27E9 \u2194 |111\u27E9."),
          ],
        }),

        h2("3.4 Key Gate Identities"),
        para("The simulator respects and can be used to verify these fundamental identities:"),
        bullet("XX = YY = ZZ = HH = I (all are self-inverse / involutory)"),
        bullet("S\u00B2 = Z (two S gates compose to a Z gate)"),
        bullet("T\u00B2 = S (two T gates compose to an S gate)"),
        bullet("HXH = Z and HZH = X (Hadamard swaps the X and Z bases)"),
        bullet("SS\u2020 = TT\u2020 = I (dagger gates are exact inverses)"),
        bullet("{X, Y} = {Y, Z} = {X, Z} = 0 (Paulis anticommute)"),
        bullet("Rx(\u03C0) = -iX, Ry(\u03C0) = -iY, Rz(\u03C0) = -iZ (up to global phase)"),
        bullet("P(\u03C0/2) = S, P(\u03C0/4) = T, P(\u03C0) = Z"),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 4: ALGORITHMS
        // ════════════════════════════════════════
        h1("Part 4: Pre-Built Algorithms & Protocols"),
        para("The Algorithm Selector panel (left sidebar) provides five pre-built quantum algorithms. Select one, configure parameters, and click ", bold("Run"), "."),

        h2("4.1 Deutsch-Jozsa Algorithm"),
        h3("The Problem"),
        para("Given a black-box function f: {0,1}\u207F \u2192 {0,1} that is promised to be either ", bold("constant"), " (same output for all inputs) or ", bold("balanced"), " (outputs 0 for exactly half the inputs and 1 for the other half), determine which. Classically this requires 2\u207F\u207B\u00B9 + 1 queries. Quantum: ", bold("1 query"), "."),
        h3("How It Works"),
        bullet("Prepare n input qubits in |0\u27E9 and 1 ancilla qubit in |1\u27E9."),
        bullet("Apply Hadamard to all qubits, creating uniform superposition."),
        bullet("Apply the oracle U_f which encodes f(x) into the phase via phase kickback."),
        bullet("Apply Hadamard to input qubits again."),
        bullet("Measure input qubits: all |0\u27E9 \u2192 constant; any |1\u27E9 \u2192 balanced."),
        h3("Physics: Why It Works"),
        para("The oracle maps |x\u27E9|y\u27E9 \u2192 |x\u27E9|y \u2295 f(x)\u27E9. With the ancilla in |\u2212\u27E9 = (|0\u27E9-|1\u27E9)/\u221A2, this becomes a phase kickback: |x\u27E9 \u2192 (-1)^f(x)|x\u27E9. The final Hadamard causes constructive interference at |0\u27E9\u207F for constant functions and destructive interference for balanced functions."),
        h3("Using the Simulator"),
        bullet("Set Number of Input Qubits (1\u20134)."),
        bullet("Choose oracle type: constant_0, constant_1, or balanced."),
        bullet("Click Run Algorithm. Step through to watch interference build."),
        bullet("Final measurement: 100% probability on |00\u20260\u27E9 = constant."),

        h2("4.2 Grover's Search Algorithm"),
        h3("The Problem"),
        para("Search an unsorted database of N = 2\u207F items for a marked target. Classical: O(N) queries. Quantum: O(\u221AN) queries \u2014 a quadratic speedup."),
        h3("How It Works"),
        bullet("Initialize all qubits to uniform superposition via Hadamard."),
        bullet("Repeat the following \u230A\u03C0/4 \u00B7 \u221A(N/M)\u230B times (M = number of targets):"),
        bullet("  1. Oracle: flip the phase of target states |t\u27E9 \u2192 -|t\u27E9.", 1),
        bullet("  2. Diffusion: reflect all amplitudes about the mean (2|s\u27E9\u27E8s| - I).", 1),
        bullet("Measure. The target state has probability \u2248 1."),
        h3("Physics: Amplitude Amplification"),
        para("The oracle marks targets with a \u03C0 phase flip. The diffusion operator performs an inversion-about-the-mean: amplitudes above the mean are reduced, below are boosted. Each iteration rotates the state vector in a 2D subspace by angle 2\u03B8 where sin(\u03B8) = \u221A(M/N). After ~\u03C0/(4\u03B8) rotations, the state aligns with the target subspace."),
        h3("Using the Simulator"),
        bullet("Set Number of Qubits (2\u20135). This defines N = 2\u207F search space."),
        bullet("Enter Target State as a decimal integer (e.g., 5 = |101\u27E9)."),
        bullet("Click Run. Watch the probability histogram: the target bar grows with each Grover iteration."),
        bullet("The summary shows the optimal iteration count and success probability."),

        h2("4.3 Quantum Teleportation"),
        h3("The Protocol"),
        para("Transfers an arbitrary quantum state |\u03C8\u27E9 = \u03B1|0\u27E9 + \u03B2|1\u27E9 from Alice to Bob using shared entanglement and 2 classical bits. The original state is destroyed (no-cloning theorem)."),
        h3("Step-by-Step"),
        bullet("Step 1 \u2014 Bell Pair Creation: Apply H to q1, then CNOT(q1, q2). Now q1 and q2 share a Bell state."),
        bullet("Step 2 \u2014 Alice\u2019s Operations: Alice applies CNOT(q0, q1) then H(q0), entangling her message qubit with her half of the Bell pair."),
        bullet("Step 3 \u2014 Alice Measures: Alice measures q0 and q1, obtaining two classical bits (m0, m1)."),
        bullet("Step 4 \u2014 Bob\u2019s Corrections: Bob applies X if m1=1, then Z if m0=1. His qubit q2 is now in state |\u03C8\u27E9."),
        h3("Physics: Why It Works"),
        para("After Alice's CNOT and Hadamard, the 3-qubit state decomposes into four terms, each conditioned on Alice's measurement outcome. Each term leaves Bob's qubit in a known Pauli rotation of |\u03C8\u27E9. The classical communication tells Bob which Pauli correction to apply. No information travels faster than light \u2014 Bob cannot use his qubit until he receives the classical bits."),
        h3("Using the Simulator"),
        bullet("Set the state to teleport using Polar (\u03B8) and Azimuthal (\u03C6) sliders, or set \u03B1 and \u03B2 directly."),
        bullet("Click Run Protocol. Step through the timeline."),
        bullet("Watch Bob's Bloch sphere (q2) \u2014 by the final step it matches the original state of q0."),

        h2("4.4 BB84 Quantum Key Distribution"),
        h3("The Protocol"),
        para("BB84 enables two parties (Alice and Bob) to establish a shared secret cryptographic key, with security guaranteed by quantum mechanics. Any eavesdropper (Eve) is detectable."),
        h3("Step-by-Step"),
        bullet("Alice randomly generates bits and randomly picks a basis (Z or X) for each."),
        bullet("Z-basis encoding: 0 \u2192 |0\u27E9, 1 \u2192 |1\u27E9.    X-basis encoding: 0 \u2192 |+\u27E9, 1 \u2192 |\u2212\u27E9."),
        bullet("Bob randomly picks a measurement basis for each qubit."),
        bullet("Sifting: Alice and Bob publicly compare bases (not values). They keep only bits where bases matched (\u224850% of bits)."),
        bullet("Error estimation: They sacrifice a subset to compute the Quantum Bit Error Rate (QBER)."),
        bullet("If QBER < 11%, the channel is secure. If QBER \u2265 11%, an eavesdropper is present."),
        h3("Physics: Why Eve Gets Caught"),
        para("Eve must measure each qubit to read it, but she doesn't know Alice's basis. If Eve guesses wrong (probability 50%), her measurement collapses the qubit to the wrong basis. When she re-sends it, Bob gets an error 50% of the time (when his basis matches Alice's). Net result: Eve introduces a ~25% error rate on the sifted key, far above the 11% threshold."),
        h3("Using the Simulator"),
        bullet("Set Number of Bits (8\u2013256)."),
        bullet("Toggle Eavesdropper Present on or off."),
        bullet("Click Run. The results panel shows: raw bits, sifted key, QBER, and secure/compromised verdict."),
        bullet("With Eve present, observe QBER rise to ~25%. Without Eve, QBER \u2248 0%."),

        h2("4.5 Quantum Random Number Generator (QRNG)"),
        h3("The Concept"),
        para("Classical computers use deterministic pseudo-random number generators (PRNGs). Quantum mechanics provides ", bold("true randomness"), ": measuring a qubit in superposition yields a fundamentally unpredictable result."),
        h3("How It Works"),
        bullet("For each random bit: prepare |0\u27E9 \u2192 apply H \u2192 measure."),
        bullet("H|0\u27E9 = (|0\u27E9+|1\u27E9)/\u221A2 gives exactly 50/50 probability."),
        bullet("Repeat N times for N truly random bits."),
        h3("Using the Simulator"),
        bullet("Set Number of Bits (1\u2013256)."),
        bullet("Click Run. The output shows: bitstring, integer/hex values, and frequency analysis."),
        bullet("For large N, the frequency ratio should approach 50% ones."),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 5: MATHEMATICS
        // ════════════════════════════════════════
        h1("Part 5: The Mathematics Behind the Simulator"),

        h2("5.1 Quantum State Representation"),
        para("A single qubit lives in a 2-dimensional complex Hilbert space. Its state is:"),
        mathBlock("|\u03C8\u27E9 = \u03B1|0\u27E9 + \u03B2|1\u27E9,    where \u03B1, \u03B2 \u2208 \u2102,    |\u03B1|\u00B2 + |\u03B2|\u00B2 = 1"),
        para("An n-qubit system lives in a 2\u207F-dimensional Hilbert space. Its state is:"),
        mathBlock("|\u03C8\u27E9 = \u2211\u1D62 c\u1D62|i\u27E9,    where \u2211 |c\u1D62|\u00B2 = 1"),
        para("The simulator stores this as a complex numpy array of 2\u207F amplitudes, using big-endian qubit ordering: |q\u2080q\u2081\u2026q\u2099\u208B\u2081\u27E9 where q\u2080 is the most significant bit."),

        h2("5.2 Gate Application"),
        para("A quantum gate is a unitary matrix U (meaning U\u2020U = I). Gate application is matrix-vector multiplication:"),
        mathBlock("|\u03C8'\u27E9 = U|\u03C8\u27E9"),
        para("For a k-qubit gate acting on specific qubits within an n-qubit system, the simulator constructs the full 2\u207F \u00D7 2\u207F matrix using tensor product expansion. The expand_gate function:"),
        bullet("Decomposes each basis state index into individual qubit values."),
        bullet("Extracts the subspace corresponding to the target qubits."),
        bullet("Applies the k-qubit unitary to the target subspace only."),
        bullet("Reconstructs the full output index from the result."),
        para("After every gate application, the simulator renormalizes the state vector to combat floating-point drift, ensuring |\u03B1|\u00B2 + |\u03B2|\u00B2 = 1 is maintained."),

        h2("5.3 Measurement"),
        para("Measurement collapses the quantum state. For measuring qubit j in the computational (Z) basis:"),
        mathBlock("P(0) = \u2211 |c\u1D62|\u00B2  (sum over all i where qubit j = 0)"),
        mathBlock("P(1) = 1 - P(0)"),
        para("The simulator:"),
        bullet("Calculates P(0) by summing |c\u1D62|\u00B2 for all basis states where the j-th bit is 0."),
        bullet("Draws a random number r \u2208 [0,1). If r < P(0), outcome = 0; else outcome = 1."),
        bullet("Projects: zeroes out all amplitudes inconsistent with the outcome."),
        bullet("Renormalizes: divides remaining amplitudes by \u221AP(outcome)."),
        para("For X-basis measurement (used in BB84), the simulator applies H before measuring in Z. For Y-basis: S\u2020 then H."),

        h2("5.4 Bloch Sphere Representation"),
        para("Any single-qubit state can be visualized as a point on the Bloch sphere. For mixed states (e.g., a qubit entangled with others), the simulator computes the reduced density matrix \u03C1 via partial trace:"),
        mathBlock("\u03C1 = Tr_B(|\u03C8\u27E9\u27E8\u03C8|)"),
        para("The Bloch vector (x, y, z) is extracted as:"),
        mathBlock("x = 2\u00B7Re(\u03C1\u2080\u2081),    y = -2\u00B7Im(\u03C1\u2080\u2081),    z = \u03C1\u2080\u2080 - \u03C1\u2081\u2081"),
        para("These correspond to the expectation values of the Pauli operators:"),
        mathBlock("x = Tr(\u03C1\u00B7\u03C3\u2093),    y = Tr(\u03C1\u00B7\u03C3\u1D67),    z = Tr(\u03C1\u00B7\u03C3\u2094)"),
        para("The purity r = \u221A(x\u00B2+y\u00B2+z\u00B2) is 1.0 for pure states and < 1.0 for mixed states. Key positions:"),
        bullet("|0\u27E9: north pole (0, 0, 1)"),
        bullet("|1\u27E9: south pole (0, 0, -1)"),
        bullet("|+\u27E9 = (|0\u27E9+|1\u27E9)/\u221A2: equator at (1, 0, 0)"),
        bullet("|\u2212\u27E9 = (|0\u27E9-|1\u27E9)/\u221A2: equator at (-1, 0, 0)"),
        bullet("|+i\u27E9 = (|0\u27E9+i|1\u27E9)/\u221A2: equator at (0, 1, 0)"),
        bullet("|\u2212i\u27E9 = (|0\u27E9-i|1\u27E9)/\u221A2: equator at (0, -1, 0)"),

        h2("5.5 Entanglement & Bell States"),
        para("Two qubits are entangled when their joint state cannot be written as a tensor product. The four Bell states form a maximally entangled basis:"),
        mathBlock("|\u03A6\u207A\u27E9 = (|00\u27E9 + |11\u27E9)/\u221A2        |\u03A6\u207B\u27E9 = (|00\u27E9 - |11\u27E9)/\u221A2"),
        mathBlock("|\u03A8\u207A\u27E9 = (|01\u27E9 + |10\u27E9)/\u221A2        |\u03A8\u207B\u27E9 = (|01\u27E9 - |10\u27E9)/\u221A2"),
        para("In the simulator, create |\u03A6+\u27E9 by applying H to q0 then CNOT(q0, q1). Notice both Bloch spheres collapse to the centre (purity < 1), indicating the qubits are individually mixed but globally pure."),

        h2("5.6 No-Cloning Theorem"),
        para("It is physically impossible to create an identical copy of an arbitrary unknown quantum state. This is why:"),
        bullet("Teleportation destroys the original state (Alice's qubit collapses)."),
        bullet("BB84 is secure (Eve cannot copy qubits to measure in both bases)."),
        bullet("Quantum information cannot be broadcast."),

        pageBreak(),

        // ════════════════════════════════════════
        // PART 6: TROUBLESHOOTING
        // ════════════════════════════════════════
        h1("Part 6: Troubleshooting & Tips"),

        h2("6.1 Common Issues"),
        bulletRuns([bold("Connection indicator is red: "), "Ensure the backend is running (uvicorn on port 8000). Check that ", code("VITE_API_URL"), " in ", code("frontend/.env"), " matches the backend address."]),
        bulletRuns([bold("Circuit does nothing: "), "Make sure the Step Controller is advanced. Gates are applied at each step, not instantly."]),
        bulletRuns([bold("Bloch sphere looks wrong: "), "For entangled qubits, reduced purity is expected. The Bloch vector will be inside the sphere, not on its surface."]),
        bulletRuns([bold("Grover's doesn't find the target: "), "With few qubits, the success probability is high but not 100%. Run multiple times. Also check that the target state is within the valid range [0, 2\u207F - 1]."]),

        h2("6.2 Tips for Learning"),
        bullet("Start with 1 qubit. Apply H, then step through and observe the Bloch sphere moving to the equator."),
        bullet("Create a Bell state (H on q0, CNOT q0\u2192q1) and observe how both Bloch spheres lose purity."),
        bullet("Try Deutsch-Jozsa with constant_0 vs balanced \u2014 observe the interference patterns differ."),
        bullet("In teleportation, try different initial states and verify Bob always receives the correct state."),
        bullet("Toggle Eve in BB84 and compare QBER values."),

        h2("6.3 System Limits"),
        bullet("Maximum 5 qubits (32 \u00D7 32 = 1024-element unitary matrices)."),
        bullet("QRNG supports up to 256 bits per run."),
        bullet("BB84 is statistical (not circuit-based) for performance reasons."),
        bullet("All arithmetic uses 64-bit complex floating point (numpy complex128)."),
      ],
    },
  ],
});

// ── Write file ──
const buffer = await Packer.toBuffer(doc);
fs.writeFileSync("Quantum_Simulator_User_Guide.docx", buffer);
console.log("Created: Quantum_Simulator_User_Guide.docx");
