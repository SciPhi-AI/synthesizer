# type: ignore
import textwrap

SYLLABI_CREATION_PROMPT = textwrap.dedent(
    """
Take a deep breath, then closely examine the configuration that follows. You will be asked to produce a similar configuration as part of this task, so pay close attention to the following YAML format.

```yaml
course:
    Quantum Physics I:
        topics:
            - Basic Features of Quantum Mechanics:
                subtopics:
                    - Linearity
                    - Complex Numbers
                    - Non-deterministic
                    - Superposition
                    - Entanglement
            - Experimental Basis of Quantum Physics:
                subtopics:
                    - Two-slit Experiments
                    - Mach-Zehnder Interferometer
                    - Elitzur-Vaidman Bombs
                    - Photoelectric Effect
                    - Compton Scattering
                    - de Broglie Wavelength
            - Wave Mechanics:
                subtopics:
                    - Galilean Transformation of de Broglie Wavelength
                    - Wave-packets and Group Velocity
                    - Matter Wave for a Particle
                    - Momentum and Position Operators
                    - Schrödinger Equation
            - Interpretation of the Wavefunction:
                subtopics:
                    - Probability Density
                    - Probability Current
                    - Current Conservation
                    - Hermitian Operators
            - Expectation Values and Uncertainty:
                subtopics:
                    - Expectation Values of Operators
                    - Time Evolution of Wave-packets
                    - Fourier Transforms
                    - Parseval Theorem
                    - Uncertainty Relation
            - Quantum Physics in One-dimensional Potentials:
                subtopics:
                    - Stationary States
                    - Boundary Conditions
                    - Particle on a Circle
                    - Infinite Square Well
                    - Finite Square Well
                    - Semiclassical Approximations
                    - Numerical Solution by the Shooting Method
                    - Delta Function Potential
                    - Simple Harmonic Oscillator
                    - Reflection and Transmission Coefficients
                    - Ramsauer Townsend Effect
                    - 1D Scattering and Phase Shifts
                    - Levinson's Theorem
            - Angular Momentum and Central Potentials:
                subtopics:
                    - Resonances and Breit-Wigner Distribution
                    - Central Potentials
                    - Algebra of Angular Momentum
                    - Legendre Polynomials
                    - Hydrogen Atom
                    - Energy Levels Diagram
                    - Virial Theorem
                    - Circular Orbits and Eccentricity
                    - Discovery of Spin
```

Given the following context, deduce the new configuration entry for the course "{course_name}". Be sure to fill in the appropriate topics and subtopics.

```md
{context}
```

Notes:
- Filter out any erroneous content like "QUIZ" or "TEST" that might appear in the syllabus. 
- Remove phrases like "UNIT" or "CHAPTER" that signal new sections.
- Attempt to match the length and specificity of the above example; add your own context if necessary to accomplish this or remove extra context.
- You should target **5-10 main topics with 6-10 subtopics each**.
- It should be valid YAML, so be sure to indent properly. Assume that the output of your response will be parsed by a YAML parser.

### Response:
"""
)


TABLE_OF_CONTENTS_DRAFT_PROMPT = """
### Instructions:
Below the course syllabus for {course_name} is shown as a yaml snippet.

```yaml
{context}
```

Pretend you are a prolific author, your task is to translate the shown syllabus into a very detailed Table of Contents for a new textbook that is meant to accompany the course.
Be sure to pick a fitting name for the textbook. Add additional topics so that the table of contents provides much more information than the original syllabus.
Return your final result in an easily parseable yaml format, your final yaml must match the above with course -> textbook, and topics -> chapters, subtopics -> sections, and an additional new key: subsubtopics -> subsections.

### Response:
"""


BOOK_FOREWARD_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the foreward for the book:

#  Title: {title}


To assist you in this task, you have been provided the context bellow:

### Related Context
```
{related_context}
```

Notes:
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for an advanced undergraduate course at MIT.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Begin your response with `## Foreward`

### Response:
"""


TABLE_OF_CONTENTS_CLEAN_PROMPT = """
### Instructions:
Below is a table of contents for the textbook "Aerodynamics of Viscous Fluids: A Comprehensive Study". This table of contents has a specified format consisting of a "textbook" key, followed by the textbook title as a key. Nested under the textbook title are the keys for chapters, sections, and subsections. The table is meant to follow a yaml format, but spacing has been removed to save space.

textbook: 
"Aerodynamics of Viscous Fluids: A Comprehensive Study":

chapters:
- Chapter 1: Fundamental Theorem of Kinematics:
sections:
- Section: 1.1 Convection:
subsections:
- 1.1a Introduction to Convection
- 1.1b Boundary Layer Convection
- 1.1c Applications of Convection

- Section: 1.2 Vorticity:
subsections:
- 1.2a Definition of Vorticity
- 1.2b Vorticity Transport Equation
- 1.2c Vorticity Generation

- Section: 1.3 Strain:
subsections:
- 1.3a Introduction to Strain
- 1.3b Strain Rate Tensor
- 1.3c Rate of Deformation Tensor

- Chapter 2: Eulerian vs. Lagrangian Description:
sections:
- Section: 2.1 Convection Relations:
subsections:
- 2.1a Eulerian and Lagrangian Descriptions
- 2.1b Material Derivative
- 2.1c Applications and Differences

- Section: 2.2 Frame of Reference:
subsections:
- 2.2a Fixed Frame
- 2.2b Moving Frame
- 2.2c Advantages and Limitations

- Section: 2.3 Mathematical Representations:
subsections:
- 2.3a Transformation Equations
- 2.3b Jacobian Matrices
- 2.3c Use in Kinematics

- Chapter 3: Conservation Laws:
sections:
- Section: 3.1 Conservation of Mass:
subsections:
- 3.1a Continuity Equation
- 3.1b Incompressible Flow
- 3.1c Compressible Flow
- Section: 3.2 Conservation of Momentum:
subsections:
- 3.2a Navier-Stokes Equations
- 3.2b Reynolds Transport Theorem
- 3.2c Pressure and Viscous Forces
- Section: 3.3 Stress Tensor:
subsections:
- 3.3a Definition of Stress Tensor
- 3.3b Viscous and Pressure Stresses
- 3.3c Reynolds Stress Tensor

- Chapter 4: Viscosity and Newtonian Fluids:
sections:
- Section: 4.1 Vorticity and Circulation:
subsections:
- 4.1a Vorticity and Circulation Equations
- 4.1b Kelvin's Circulation Theorem
- 4.1c Vorticity Distribution
- 4.1d Circulation and Vorticity Relations
- Section: 4.2 Newtonian vs. Non-Newtonian Fluids:
subsections:
- 4.2a Definition and Characteristics
- 4.2b Models of Non-Newtonian Fluids
- 4.2c Applications and Differences
- Section: 4.3 Shear and Bulk Viscosity:
subsections:
- 4.3a Definitions and Differences
- 4.3b Measurement Techniques
- 4.3c Importance in Fluid Mechanics

- Chapter 5: Navier-Stokes Equations:
sections:
- Section: 5.1 Physical Parameters:
subsections:
- 5.1a Dimensionless Parameters
- 5.1b Reynolds Number
- 5.1c Mach Number
- Section: 5.2 Dynamic Similarity:
subsections:
- 5.2a Scaling Laws
- 5.2b Model Testing
- 5.2c Similarity Criteria

- Chapter 6: Dimensional Analysis:
sections:
- Section: 6.1 Dominant Balance:
subsections:
- 6.1a Balance of Forces
- 6.1b Balance of Stresses
- Section: 6.2 Viscous Flow Classification:
subsections:
- 6.2a Laminar Flow
- 6.2b Turbulent Flow
- Section: 6.3 Buckingham's Pi Theorem:
subsections:
- 6.3a Introduction and Theory
- 6.3b Application in Fluid Mechanics
- 6.3c Examples and Case Studies

- Chapter 7: Thin Shear Layer Equations:
sections:
- Section: 7.1 TSL Coordinates:
subsections:
- 7.1a Definition of TSL Coordinates
- 7.1b TSL Navier-Stokes Equations
- Section: 7.2 Boundary Conditions:
subsections:
- 7.2a No-Slip Condition
- 7.2b Impermeability Condition
- 7.2c Kutta Condition
- Section: 7.3 Shear Layer Categories:
subsections:
- 7.3a Blasius Shear Layer
- 7.3b Falkner-Skan Shear Layer
- 7.3c Displacement Shear Layer

- Chapter 8: Local Scaling:
sections:
- Section: 8.1 Falkner-Skan Flows:
subsections:
- 8.1a Introduction to Falkner-Skan Flows
- 8.1b Boundary Layer Equations
- 8.1c Solution Techniques

- Section: 8.2 Scaling Laws in Fluid Mechanics:
subsections:
- 8.2a Basic Principles of Scaling
- 8.2b Applications in Different Flow Regimes
- 8.2c Limitations and Challenges

- Section: 8.3 Similarity Solutions:
subsections:
- 8.3a Introduction to Similarity Solutions
- 8.3b Methods to Achieve Similarity
- 8.3c Examples in Fluid Dynamics

- Chapter 9: ODE's, PDE's, and Boundary Conditions:
sections:
- Section: 9.1 Well-Posedness:
subsections:
- 9.1a Definition of Well-Posedness
- 9.1b Initial and Boundary Conditions
- Section: 9.2 Partial Differential Equations:
subsections:
- 9.2a Classification of PDEs
- 9.2b Elliptic, Parabolic, and Hyperbolic Equations
- Section: 9.3 Boundary Conditions:
subsections:
- 9.3a Dirichlet Boundary Condition
- 9.3b Neumann Boundary Condition
- 9.3c Mixed Boundary Condition

- Chapter 10: Numerical Methods for ODE's:
sections:
- Section: 10.1 Discretization:
subsections:
- 10.1a Finite Difference Method
- 10.1b Finite Element Method
- 10.1c Finite Volume Method
- Section: 10.2 Stability:
subsections:
- 10.2a Von Neumann Stability Analysis
- 10.2b CFL Condition
- 10.2c Implicit vs. Explicit Methods

- Chapter 11: Integral Methods:
sections:
- Section: 11.1 Integral Momentum Equation:
subsections:
- 11.1a Integral Boundary Layer Equations
- 11.1b Blasius Solution
- 11.1c Falkner-Skan Solution
- Section: 11.2 Thwaites' Method:
subsections:
- 11.2a Introduction to Thwaites' Method
- 11.2b Boundary Layer Growth
- 11.2c Thwaites' Laminar Boundary Layer Solution

- Chapter 12: Dissipation Methods:
sections:
- Section: 12.1 Integral Kinetic Energy Equation:
subsections:
- 12.1a Turbulent Dissipation
- 12.1b Shear Stress Distribution
- 12.1c Integral Energy Equation

- Section: 12.2 Turbulent Dissipation Mechanisms:
subsections:
- 12.2a Basics of Turbulence and Eddies
- 12.2b Cascade Mechanism
- 12.2c Effects on Boundary Layer

- Section: 12.3 Experimental and Numerical Techniques:
subsections:
- 12.3a Techniques for Measuring Dissipation
- 12.3b Numerical Methods and Challenges
- 12.3c Comparison of Experimental and Numerical Results

- Chapter 13: Asymptotic Perturbation Theory:
sections:
- Section: 13.1 Higher-Order Effects:
subsections:
- 13.1a Introduction to Perturbation Theory
- 13.1b Asymptotic Expansion
- 13.1c Higher-Order Corrections
- Section: 13.2 Boundary Layer Perturbation:
subsections:
- 13.2a Introduction to Boundary Layer Perturbation
- 13.2b Application in Viscous Flows
- 13.2c Challenges and Limitations
- Section: 13.3 Nonlinear Perturbations:
subsections:
- 13.3a Introduction to Nonlinear Perturbations
- 13.3b Application in Fluid Dynamics
- 13.3c Advanced Methods and Techniques

- Chapter 14: 2D Interaction Models:
sections:
- Section: 14.1 Displacement Body:
subsections:
- 14.1a Flow Past a Cylinder
- 14.1b Flow Past an Airfoil
- Section: 14.2 Transpiration:
subsections:
- 14.2a Transpiration Boundary Condition
- 14.2b Transpiration Effects on Flow Field
- Section: 14.3 Form Drag:
subsections:
- 14.3a Definition of Form Drag
- 14.3b Pressure Drag
- 14.3c Friction Drag
- Section: 14.4 Stall Mechanisms:
subsections:
- 14.4a Boundary Layer Separation
- 14.4b Flow Reattachment
- 14.4c Dynamic Stall

- Chapter 15: IBLT Solution Techniques:
sections:
- Section: 15.1 Iteration Stability:
subsections:
- 15.1a Stability Analysis
- 15.1b Convergence Criteria
- 15.1c Solution Techniques
- Section: 15.2 Fully-Coupled Iteration:
subsections:
- 15.2a Introduction to Fully-Coupled Iteration
- 15.2b Fluid-Structure Interaction
- 15.2c Aeroelasticity
- Section: 15.3 3-D IBLT:
subsections:
- 15.3a Three-Dimensional Boundary Layers
- 15.3b Transition Mechanisms in 3D Flows

- Chapter 16: Small-Perturbation Theory:
sections:
- Section: 16.1 Orr-Sommerfeld Equation:
subsections:
- 16.1a Definition of Orr-Sommerfeld Equation
- 16.1b Linear Stability Analysis
- 16.1c Growth Rates and Frequencies
- Section: 16.2 Linear Instabilities:
subsections:
- 16.2a Introduction to Linear Instabilities
- 16.2b Applications in Viscous Flows
- 16.2c Detection and Control Methods
- Section: 16.3 Perturbation in Compressible Flows:
subsections:
- 16.3a Basics of Compressible Flow Perturbations
- 16.3b Challenges in High-Speed Flows
- 16.3c Recent Advances and Developments

- Chapter 17: Boundary Conditions, Homogeneity, Solution Techniques:
sections:
- Section: 17.1 Transition Mechanisms:
subsections:
- 17.1a Laminar-Turbulent Transition
- 17.1b Transition Prediction Methods
- Section: 17.2 Transition Prediction:
subsections:
- 17.2a Stability Analysis
- 17.2b Experimental Methods
- 17.2c Computational Methods

- Chapter 18: Reynolds Averaging:
sections:
- Section: 18.1 Prandtl's Analogy:
subsections:
- 18.1a Reynolds-Averaged Navier-Stokes Equations
- 18.1b Turbulent Stresses
- 18.1c Reynolds Stress Modeling

- Chapter 19: Turbulent BL Structure:
sections:
- Section: 19.1 Wake:
subsections:
- 19.1a Wake Formation
- 19.1b Wake Characteristics
- Section: 19.2 Wall Layers:
subsections:
- 19.2a Viscous Sublayer
- 19.2b Buffer Layer
- 19.2c Overlap Layer
- Section: 19.3 Inner, Outer Variables:
subsections:
- 19.3a Velocity and Length Scales
- 19.3b Wall Coordinates
- 19.3c Outer Variables
- Section: 19.4 Effects of Roughness:
subsections:
- 19.4a Roughness Effects on Boundary Layer
- 19.4b Skin Friction and Heat Transfer

- Chapter 20: Equilibrium BL's:
sections:
- Section: 20.1 Clauser Hypothesis:
subsections:
- 20.1a Equilibrium Boundary Layer Concept
- 20.1b Clauser's Equilibrium Assumptions
- Section: 20.2 Dissipation Formulas:
subsections:
- 20.2a Turbulent Energy Dissipation
- 20.2b Dissipation in Equilibrium Boundary Layers
- Section: 20.3 Integral Closure:
subsections:
- 20.3a Reynolds Stress Closure
- 20.3b Eddy Viscosity Models
- 20.3c Mixing Length Models
...

Your task is to inspect the table of contents that is provided below and to produce a new table of contents which is formatted EXACTLY as the example above. 

{table_of_contents}

Further, if the table of contents is less than 20 chapters, or lacking sufficient detail in any given chapter, then your task is to coherently expand the table and re-arrange it so that it is 20+ chapters, with 3-4 sections and 3-4 subsections per chapter, formatted exactly as the example above.

If the table of contents is already in the correct format and complete, reproduce it as-is with the new formatting.


Notes:
- Chapters should be numbered `Chapter 1`, `Chapter 2`, etc.
- Sections should be numbered `Section 1.1`, `Section 1.2`, etc.
- Subsections should be numbered `1.1a`, `1.1b`, etc.
- The table of contents should contain no indentations.
- The table of contents should be 20 chapters or more, and have 3-4 sections and 3-4 subsections per chapter.

### Response:
"""

BOOK_BULK_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing the chapter and section shown below:

#  Title: {title}

## Chapter: {chapter}

### Section: {section}

### Subsection (optional): {subsection}

To assist you in writing the chapter, you have been provided with some related context and recent chapter contents bellow:

### Related Context
```
{related_context}
```

### Last textbook section content:
```
{book_context}
```

Notes:
- The book is being written in the popular Markdown format.
- The context may be truncated and is meant only to provide a starting point. Feel free to expand on it or take the response in any direction that fits the prompt, but keep it in a voice that is appropriate for an advanced undergraduate course at MIT.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- If starting a new section, include `### [Section Title]`
- If starting a new subsection, include `#### [Subsection Title]`
`

### Response:
"""

# Prompt for the LLM
BOOK_CHAPTER_SUMMARY_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are tasked with writing a several paragraph CONCLUSION FOR THE CHAPTER shown below:

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context bellow:

### Previously written chapter:
```
{book_context}
```

Following your authoring of the conclusion, write 5 exercises which align with the context of the chapter. Format each with a header `#### Exercise 1` etc.

Notes:
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Start the conclusion the Chapter with a header that reads `### Conclusion`, start the exercises with a header that reads `### Exercises`.

`

### Response:
"""

# Prompt for the LLM
BOOK_CHAPTER_INTRODUCTION_PROMPT = """
### Instructions:
You are a writing a book titled "{title}". You are currently writing a several paragraph introducton for the chapter shown below (avoid going into too much detail):

#  Title: {title}

## Chapter: {chapter}

To assist you in this task, you have been provided the context which will be covered in this chapter:

### Chapter section topics covered:
```
{book_context}
```

Notes:
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
- Include the chapter title at the top of your output, formatted as  `## Chapter: [Title]`,  `### Introduction` below that.
`

### Response:
"""
