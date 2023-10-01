# type: ignore
import textwrap

SYLLABI_CREATION_PROMPT = textwrap.dedent(
    """
Take a deep breath, then closely examine the configuration that follows. You will be asked to produce a similar configuration as part of this task, so pay close attention to the format.

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
                    - Levinson’s Theorem
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
- Attempt to match the length and specificity of the above example; add your own context if necessary to accomplish this or remove extra context.
- You should target **5-10 main topics with 6-10 subtopics each**.

### Response:
"""
)


TABLE_OF_CONTENTS_PROMPT = """
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

Notes:
- The book is being written in the popular Markdown format.
- Avoid making any factual claims or opinions without proper citations or context to support them, stick to the proposed context.
- Format ALL math equations with the $ and $$ delimiters to insert math expressions in TeX and LaTeX style syntax. This content is then rendered using the highly popular MathJax library. E.g. write inline math like `$y_j(n)$` and equations like `$$
\\Delta w = ...
$$
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
`

### Response:
"""
