# Randomization modifiers
COURSE_TYPE = [
    "undergraduate",
    "elective",
    "specialized",
    "computer science",
    "advanced",
    "introductory",
    "high school",
    "professional development",
    "certification",
    "bootcamp",
    "seminar",
]

PROGRAMMING_PARADIGM = [
    "object-oriented",
    "functional",
    "procedural",
    "declarative",
    "logic-based",
    "event-driven",
    "modular",
    "symbolic",
    "aspect-oriented",
    "multi-paradigm",
]

ADDITIONAL_CONTEXT = [
    ""
    " Also, mention one real-world application where this concept is critical.",
    " Additionally, discuss a potential pitfall or misconception associated with this concept.",
    " Also, highlight its benefits over the alternative approach.",
    " Also, compare this concept with its predecessor.",
    " Additionally, share its significance in modern computing.",
    " Also, provide a historical context or origin of this concept.",
    " Also, mention one real-world application where this concept is critical.",
    " Additionally, discuss a potential pitfall or misconception associated with this concept.",
    " Also, highlight its benefits over the alternative approach.",
    " Also, compare this concept with its predecessor.",
    " Additionally, share its significance in modern computing.",
    " Also, provide a historical context or origin of this concept.",
    " Besides, can you recommend any books or resources for further reading?",
    " Also, how does this concept relate to recent trends in technology?",
    " Additionally, provide a visualization or diagram explaining this concept.",
    " Also, mention any notable personalities or experts associated with this concept.",
    " In addition, discuss the scalability aspects of this concept.",
    " Also, relate this concept to a famous algorithm or software.",
]

DEPTH = [
    "in detail",
    "in simple terms",
    "in depth",
    "in a nutshell",
    "from a historical perspective",
    "from a practical perspective",
    "highlighting its pros and cons",
    "focusing on its applications",
]

PROMPT_TEMPLATES = [
    "In a {course_type} course focused on the {programming_paradigm} paradigm in Python, the topic of {concept} is crucial. Please define a different but related concept {depth} and illustrate it with Python code.{additional_context}",
    "In a {course_type} course focused on the {programming_paradigm} paradigm in Python, the topic of {concept} is crucial. Please define this concept {depth} and illustrate it with Python code.{additional_context}",
    "There are {course_type} courses touching upon {programming_paradigm} paradigm which discuss {concept}. What is it, {depth}? Also, provide a relevant Python example.{additional_context}",
    "Often {course_type} courses touch upon {programming_paradigm} paradigm in Python often discuss {concept}. Can you think of a related concept and explain it {depth}? Also, provide a relevant Python example.{additional_context}",
    "In modern {course_type} courses, the emphasis on the {programming_paradigm} paradigm in Python has grown. Explore the topic of {concept} {depth} and provide practical Python examples.{additional_context}",
    "In modern {course_type} courses, the emphasis on the {programming_paradigm} paradigm in Python has grown. Explore a related but different {concept} {depth} and provide practical Python examples.{additional_context}",
    "With a focus on {programming_paradigm} paradigm, how would you introduce the topic of {concept} in a {course_type} course? Break it down {depth}.{additional_context}",
    "With a focus on {programming_paradigm} paradigm, how would you introduce a different but related concept to {concept} to our {course_type} course? Break it down {depth}.{additional_context}",
]

CONCEPT = [
    # Basic Mathematics:
    "numerical properties: associativity, commutativity, distributivity",
    "fundamental theorem of arithmetic",
    "prime factorization",
    "GCD and LCM relationships",
    "exponential properties",
    "logarithm properties and bases",
    "complex numbers: basic operations",
    "complex numbers: polar form",
    "fraction operations: addition, subtraction, multiplication, division",
    "decimal to fraction conversions",
    "integer and fractional exponents",
    "equation properties: transitive, reflexive, symmetric",
]

input_generators = {
    "instruction": {
        "course_type": COURSE_TYPE,
        "programming_paradigm": PROGRAMMING_PARADIGM,
        "additional_context": ADDITIONAL_CONTEXT,
        "depth": DEPTH,
        "prompt_templates": PROMPT_TEMPLATES,
        "concept": CONCEPT,
    }
}
