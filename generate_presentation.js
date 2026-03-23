const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'Quantum Simulator Team';
pres.title = 'Quantum Protocol & Algorithm Simulator';

// Midnight Executive Palette from anthropic skills guidelines
const colors = {
    primary: "1E2761",   // Navy
    secondary: "CADCFC", // Ice blue
    accent: "FFFFFF",    // White
    text: "363636",
    lightText: "F2F2F2",
    muted: "64748B"
};

// Define Master Slide
pres.defineSlideMaster({
  title: 'MASTER_SLIDE',
  background: { color: colors.primary },
  objects: [
    { rect: { x: 0, y: 0, w: "100%", h: 0.8, fill: { color: colors.secondary } } },
    { placeholder: { options: { name: 'header', type: 'title', x: 0.5, y: 0.1, w: 9, h: 0.6, fontSize: 32, fontFace: "Georgia", color: colors.primary, bold: true, margin: 0 } } }
  ]
});

// Slide 1: Title
let slide1 = pres.addSlide();
slide1.background = { color: colors.primary };
slide1.addText("Quantum Protocol & Algorithm Simulator", { 
    x: 1, y: 2, w: 8, h: 1.5, 
    fontSize: 44, fontFace: "Georgia", 
    color: colors.accent, bold: true, align: "center", breakLine: true 
});
slide1.addText("Interactive Quantum Mechanics in your Browser", { 
    x: 1, y: 3.5, w: 8, h: 0.5, 
    fontSize: 20, fontFace: "Calibri", 
    color: colors.secondary, align: "center" 
});

// Slide 2: Core Interface
let slide2 = pres.addSlide({ masterName: "MASTER_SLIDE" });
slide2.addText("Interactive Interface", { placeholder: "header" });
slide2.addText([
    { text: "4-Panel Dashboard for Maximum Visibility", options: { breakLine: true, bullet: true, bold: true, fontSize: 20, color: colors.accent } },
    { text: "Circuit Editor Canvas (Drag & Drop Gates)", options: { breakLine: true, bullet: true, color: colors.secondary } },
    { text: "Real-time Bloch Sphere rendering (WebGL)", options: { breakLine: true, bullet: true, color: colors.secondary } },
    { text: "Statevector & Probability Histograms", options: { breakLine: true, bullet: true, color: colors.secondary } },
    { text: "Temporal Execution (Step Controller)", options: { bullet: true, color: colors.secondary } }
], { x: 0.5, y: 1.5, w: 9, h: 3.5, fontFace: "Calibri", fontSize: 18, valign: "top" });

// Slide 3: Essential Quantum Gates
let slide3 = pres.addSlide({ masterName: "MASTER_SLIDE" });
slide3.addText("Essential Quantum Gates", { placeholder: "header" });

// Card 1
slide3.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.5, w: 4.25, h: 3.5, fill: { color: colors.secondary } });
slide3.addText("Single-Qubit Gates", { x: 0.7, y: 1.7, w: 3.85, h: 0.5, bold: true, fontSize: 24, fontFace: "Georgia", color: colors.primary });
slide3.addText([
  { text: "Hadamard (H): Creates superposition", options: { breakLine: true, bullet: true, color: colors.text } },
  { text: "Pauli-X, Y, Z: Core rotations", options: { breakLine: true, bullet: true, color: colors.text } },
  { text: "Rx, Ry, Rz, P: Parametric phase shifts", options: { bullet: true, color: colors.text } }
], { x: 0.7, y: 2.2, w: 3.85, h: 2.5, fontFace: "Calibri", fontSize: 16, valign: "top" });

// Card 2
slide3.addShape(pres.shapes.RECTANGLE, { x: 5.25, y: 1.5, w: 4.25, h: 3.5, fill: { color: colors.secondary } });
slide3.addText("Entanglement Gates", { x: 5.45, y: 1.7, w: 3.85, h: 0.5, bold: true, fontSize: 24, fontFace: "Georgia", color: colors.primary });
slide3.addText([
  { text: "CNOT: Fundamental 2-qubit entangler", options: { breakLine: true, bullet: true, color: colors.text } },
  { text: "CZ & SWAP: Advanced correlations", options: { breakLine: true, bullet: true, color: colors.text } },
  { text: "CCX (Toffoli): Universally classical complete", options: { bullet: true, color: colors.text } }
], { x: 5.45, y: 2.2, w: 3.85, h: 2.5, fontFace: "Calibri", fontSize: 16, valign: "top" });

// Slide 4: Algorithms
let slide4 = pres.addSlide({ masterName: "MASTER_SLIDE" });
slide4.addText("Core Quantum Algorithms", { placeholder: "header" });
slide4.addTable([
    [{ text: "Algorithm", options: { bold: true, fill: { color: colors.secondary }, color: colors.primary } }, { text: "Purpose", options: { bold: true, fill: { color: colors.secondary }, color: colors.primary } }],
    [{ text: "Deutsch-Jozsa", options: { color: colors.accent } }, { text: "Determine if an Oracle is constant/balanced in 1 query", options: { color: colors.secondary } }],
    [{ text: "Grover's Search", options: { color: colors.accent } }, { text: "O(\u221AN) quadratic speedup for unstructured search", options: { color: colors.secondary } }],
    [{ text: "Teleportation", options: { color: colors.accent } }, { text: "Transfer exact quantum states via Bell pairs", options: { color: colors.secondary } }],
    [{ text: "BB84 Protocol", options: { color: colors.accent } }, { text: "Quantum Key Distribution for crypto security", options: { color: colors.secondary } }],
    [{ text: "QRNG", options: { color: colors.accent } }, { text: "True probabilistic Random Number Generation", options: { color: colors.secondary } }]
], { x: 0.5, y: 1.5, w: 9, h: 3.5, border: { pt: 1, color: colors.secondary }, color: colors.accent, fontFace: "Calibri", fontSize: 16, rowH: [0.5, 0.6, 0.6, 0.6, 0.6, 0.6] });

pres.writeFile({ fileName: "Quantum_Simulator_Presentation.pptx" }).then(() => {
    console.log("Success! Created Quantum_Simulator_Presentation.pptx");
}).catch((err) => {
    console.error("Error creating PPTX:", err);
});
