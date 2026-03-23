import {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, BorderStyle, ShadingType, PageBreak, Footer, Header, convertInchesToTwip, Table, TableRow, TableCell, WidthType
} from "docx";
import * as fs from "fs";

// Colors
const BLUE = "1a56db";
const DARK = "1f2937";
const GRAY = "6b7280";
const ACCENT = "7c3aed";
const GREEN = "047857";
const RED = "b91c1c";

// Helpers
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
function experimentBox(titleText, instructions) {
  const rows = [
    new TableRow({
      children: [
        new TableCell({
          shading: { type: ShadingType.CLEAR, fill: "e0e7ff" }, // Light indigo
          padding: { top: 100, bottom: 100, left: 150, right: 150 },
          children: [new Paragraph({ children: [new TextRun({ text: "🧪 INTERACTIVE EXPERIMENT: " + titleText, bold: true, size: 22, color: BLUE, font: "Calibri" })] })]
        })
      ]
    })
  ];
  
  instructions.forEach(inst => {
    rows.push(
      new TableRow({
        children: [
          new TableCell({
            padding: { top: 80, bottom: 80, left: 150, right: 150 },
            children: [new Paragraph({ 
              spacing: { line: 280 },
              children: [new TextRun({ text: "• " + inst, size: 20, font: "Calibri", color: DARK })] 
            })]
          })
        ]
      })
    );
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 12, color: BLUE },
      bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE },
      left: { style: BorderStyle.SINGLE, size: 12, color: BLUE },
      right: { style: BorderStyle.SINGLE, size: 12, color: BLUE },
    },
    rows: rows
  });
}
function conceptualNote(text) {
  return new Paragraph({
    spacing: { before: 160, after: 160, line: 300 },
    shading: { type: ShadingType.CLEAR, fill: "fef3c7" }, // light yellow
    indent: { left: convertInchesToTwip(0.2), right: convertInchesToTwip(0.2) },
    children: [new TextRun({ text: "💡 Physics Concept: " + text, bold: true, size: 22, color: "92400e", font: "Calibri" })]
  });
}
function warningNote(text) {
  return new Paragraph({
    spacing: { before: 160, after: 160, line: 300 },
    shading: { type: ShadingType.CLEAR, fill: "fee2e2" }, // light red
    indent: { left: convertInchesToTwip(0.2), right: convertInchesToTwip(0.2) },
    children: [new TextRun({ text: "⚠️ Crucial Detail: " + text, bold: true, size: 22, color: RED, font: "Calibri" })]
  });
}
function para(text) {
  return new Paragraph({
    spacing: { after: 160, line: 320 },
    children: [new TextRun({ text, size: 22, font: "Calibri", color: DARK })],
  });
}
function bullet(text) {
  return new Paragraph({
    bullet: { level: 0 },
    spacing: { after: 80, line: 300 },
    children: [new TextRun({ text, size: 22, font: "Calibri", color: DARK })],
  });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

const doc = new Document({
  sections: [
    {
      properties: {
        page: { margin: { top: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1), right: convertInchesToTwip(1) } },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [new TextRun({ text: "Interactive Quantum Lab Manual", size: 16, color: GRAY, font: "Calibri", italics: true })],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [new TextRun({ text: "Educational Materials \u2014 Quantum Simulator Pro", size: 14, color: GRAY })],
            }),
          ],
        }),
      },
      children: [
        new Paragraph({ spacing: { before: 3000 }, children: [] }),
        title("Interactive Quantum Lab Manual"),
        subtitle("A Hands-on Guide to Quantum Physics and Computing"),
        new Paragraph({
          spacing: { before: 800 },
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Learn the fundamentals of quantum mechanics by performing interactive experiments in the simulator.", size: 22, color: DARK, font: "Calibri" })],
        }),
        pageBreak(),

        h1("Table of Contents"),
        para("Lab 1: The UI and Your First Qubit"),
        para("Lab 2: Superposition and Interference (The Hadamard Gate)"),
        para("Lab 3: Measurement (Collapsing the Wavefunction)"),
        para("Lab 4: Entanglement (Spooky Action at a Distance)"),
        para("Lab 5: Quantum Teleportation (Moving States)"),
        para("Lab 6: BB84 Quantum Cryptography (Unbreakable Keys)"),
        para("Lab 7: Deutsch-Jozsa Algorithm (Quantum Parallelism)"),
        para("Lab 8: Grover's Search (Amplitude Amplification)"),
        pageBreak(),

        // ════════════ LAB 1 ════════════
        h1("Lab 1: The UI and Your First Qubit"),
        para("Before manipulating the fabric of reality, you need to understand your instruments. Your primary tools are the Circuit Editor (where you place gates), the Bloch Sphere (where you view 3D qubit states), and the State Vector panel (where you view the mathematical data)."),
        
        conceptualNote("A classical bit is an absolute 0 or 1. A Quantum Bit (Qubit) exists in an infinite continuum between |0> and |1>, represented by a point on the surface of a 3D sphere called the Bloch Sphere."),

        experimentBox("Flipping a Qubit (The Pauli-X Gate)", [
          "Set the Qubit Counter (top left) to 1 Qubit.",
          "Hover your mouse over the orange 'X' gate in the palette. Note the tooltip explains it is a 'Bit-flip' and shows its mathematical 2x2 matrix.",
          "Click the 'X' gate, then click the 'q0' wire on the circuit.",
          "Observe the Bloch Sphere on the right. The arrow, which started pointing straight up at |0>, has instantly rotated 180° to point straight down at |1>.",
          "Look at the State Vector bottom panel. The probability bar for |0> is gone, and the bar for |1> is at 100%."
        ]),

        // ════════════ LAB 2 ════════════
        h1("Lab 2: Superposition and Interference"),
        para("Superposition is the ability of a quantum system to be in multiple states at once. It is not that we don't know the state; rather, the state is mathematically spread across both possibilities."),

        experimentBox("Entering Superposition (The Hadamard Gate)", [
          "Click the Global Reset button (circular arrow top left).",
          "Place a blue 'H' (Hadamard) gate on the q0 wire.",
          "Look at the Bloch Sphere. The arrow has rotated 90° from the North Pole to the Equator. It points along the X-axis (the |+> state).",
          "Switch the bottom State Vector panel to '◎ Disks' mode.",
          "Notice both the |0> and |1> circles are exactly half full (50% probability each). The clock-hands inside both circles point straight up (Phase = 0°)."
        ]),

        conceptualNote("Interference is the core of quantum computing. If you toss a classical coin twice, it's still 50/50. If you apply a quantum Hadamard gate twice, the probabilities interfere."),

        experimentBox("Quantum Interference", [
          "Add a SECOND 'H' gate exactly after the first one on q0.",
          "Use the Step Controller (bottom) to step backward to the first H gate. You see 50/50 superposition.",
          "Step forward to the second H gate.",
          "Notice the state returns to 100% |0>. The positive phases constructively interfered to build |0>, while the opposing phases destructively interfered to perfectly erase |1>."
        ]),
        pageBreak(),

        // ════════════ LAB 3 ════════════
        h1("Lab 3: Measurement"),
        para("In classical physics, looking at a ball doesn't change it. In quantum physics, measuring a superposition violently forces it to choose a single definite reality. This is called 'Collapsing the Wavefunction'."),

        experimentBox("The Collapse", [
          "Reset the circuit.",
          "Place an 'H' gate on q0 to create a 50/50 superposition.",
          "In the circuit toolbar, click the '📏 Measure' button to place an 'M' gate after the 'H'.",
          "Use the Step Controller to step backwards before the 'M' gate (observe the 50/50 split in the histogram).",
          "Click 'Step Forward' to pass through the measurement gate.",
          "Watch the histogram flash and instantly collapse to either 100% |0> or 100% |1>."
        ]),

        warningNote("Measurement is completely irreversible! Once the wavefunction collapses, all quantum information about the superposition (and its phase) is permanently destroyed."),

        // ════════════ LAB 4 ════════════
        h1("Lab 4: Entanglement"),
        para("Albert Einstein called it 'Spooky action at a distance'. Entanglement happens when two qubits become so deeply linked that reading the state of one instantly defines the state of the other, no matter the distance."),

        conceptualNote("When qubits entangle, they lose their individual identities. They can no longer be described by an arrow on a Bloch Sphere. They enter a 'Mixed State' locally, whileremaining 'Pure' globally."),

        experimentBox("Creating a Bell State", [
          "Expand 'Algorithms & Protocols' on the left panel.",
          "Select 'The Four Bell States'. Leave 'Phi+' selected and click Run.",
          "Look closely at the Bloch Spheres. The arrows have vanished! A glowing purple '⚡ Entangled' badge appears, and the dot moves to the dead center of the sphere.",
          "Look above the spheres at the '⚡ Entanglement Links' web. It says 'q0 ⟷ q1', proving these two specific qubits are physically tied.",
          "Look at the State Vector histogram. You see 50% |00> and 50% |11>. You will never see |01> or |10>. If you measure q0 to be a 0, q1 is forced to instantly become a 0."
        ]),
        pageBreak(),

        // ════════════ LAB 5 ════════════
        h1("Lab 5: Quantum Teleportation"),
        para("Because of the 'No-Cloning Theorem', it is physically impossible to copy a quantum state. If you want to move quantum information, you must destroy the original to recreate it elsewhere. We use Entanglement to do this."),

        experimentBox("Teleporting a State", [
          "Open 'Quantum Teleportation' from the left panel.",
          "Adjust the 'Theta' slider to about 2.0 (this picks a random state to teleport). Click Run.",
          "Use the Step Controller to go back to Step 0. Notice the arrow on q0 (Alice's message). q2 (Bob) is empty.",
          "Step forward through Alice's gates (CNOT and H). She entangles her message with a Bell pair.",
          "Step past Alice's measurements. Her qubit (q0) collapses and is destroyed.",
          "Step to the very end. Observe Bob's Bloch sphere (q2). It now perfectly matches Alice's original state! The message teleported across the circuit."
        ]),

        warningNote("Teleportation does not happen faster than light. Bob's state is garbage until Alice measures her qubits and sends the classical results (the two lines) to Bob for correction."),

        // ════════════ LAB 6 ════════════
        h1("Lab 6: BB84 Quantum Cryptography"),
        para("Quantum Mechanics allows us to make unbreakable codes. If Alice sends Bob quantum keys, any eavesdropper (Eve) who tries to look at the keys will accidentally 'Measure' them. As we learned in Lab 3, measurement collapses and destroys the state, leaving obvious fingerprints."),

        experimentBox("Catching Eve in the Act", [
          "Open 'BB84 Quantum Key Distribution'.",
          "Ensure 'Eve Present' is toggled OFF. Click Run.",
          "Look at the Result panel. The Quantum Bit Error Rate (QBER) will be 0%. The channel is secure.",
          "Now, toggle 'Eve Present' to ON and click Run again.",
          "Look at the Result panel. The QBER is heavily spiked to around ~25%. Alice and Bob instantly know their line is tapped and will abort the key generation. The laws of physics guarantee Eve is caught."
        ]),
        pageBreak(),

        // ════════════ LAB 7 ════════════
        h1("Lab 7: Deutsch-Jozsa Algorithm"),
        para("This algorithm proves that a quantum computer can solve certain problems exponentially faster than a classical computer. Imagine a black box function. You need to know if it's 'Constant' (always outputs the same thing) or 'Balanced' (outputs half 0s, half 1s). Classically you'd test it multiple times. Quantumly, we do it in one shot."),

        experimentBox("Quantum Parallelism", [
          "Open the Deutsch-Jozsa algorithm.",
          "Set Qubits to 3 and Oracle to 'Balanced'. Click Run.",
          "Switch the bottom panel to '◎ Disks' mode and step backward.",
          "Notice how all inputs are fed into the oracle at the exact same time in a massive superposition.",
          "The 'Oracle' encodes the function's output not as 0s or 1s, but as 'Phase' (changing the direction of the clock hands in the disks).",
          "Step to the end. The final Hadamard gates force those phases to interfere. Because the function was balanced, the opposite phases cancel each other out perfectly, forcing a 100% measurement on a single 'Balanced' indicator state!"
        ]),

        // ════════════ LAB 8 ════════════
        h1("Lab 8: Grover's Search"),
        para("If you must search an unsorted database of 1,000,000 items, a classical computer checks 500,000 on average. A quantum computer uses 'Amplitude Amplification' to find it in just 1,000 steps."),

        experimentBox("Amplitude Amplification", [
          "Open Grover's Search Algorithm.",
          "Set Qubits to 4. Set Target to 11. Click Run.",
          "Use the Step Controller to step backwards and watch the histogram.",
          "Unlike a classical computer which searches one bar at a time, the quantum computer mathematically 'reflects' all the probabilities simultaneously. With each step of Grover's iteration, you can literally watch the incorrect bars shrink, and the correct target bar (11) violently grow to nearly 100%."
        ])

      ],
    },
  ],
});

const buffer = await Packer.toBuffer(doc);
fs.writeFileSync("Interactive_Quantum_Lab_Manual.docx", buffer);
console.log("Created: Interactive_Quantum_Lab_Manual.docx");
