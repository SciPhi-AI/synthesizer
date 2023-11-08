import random
import sympy as sp  # ignore

from sciphi.sympy_generator.generators import AbstractGenerator


# Subclass for Linear Equations
class LinearEqGenerator(AbstractGenerator):
    name = "lin_eq"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generation logic specific to linears
            m, b = [
                random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )
                for _ in range(2)
            ]

            # Make sure the coefficient m is not zero
            while m == 0:
                m = random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )

            plaintext_expr = f"{m}x"
            if b > 0:
                plaintext_expr += f" + {b}"
            elif b < 0:
                plaintext_expr += f" - {-b}"

            # Create the prompt
            prompt = f"Solve the linear equation {plaintext_expr} = 0 for x."

            # Source code using SymPy to solve the equation
            exec_code = f"x = sp.symbols('x')\nequation = sp.Eq({m}*x + {b}, 0)\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solve(equation, x)[0])"

            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The solution to the equation is $x = {result}$.",
                )
            )
        return data


# Subclass for Quadratic Equations
class QuadraticEqGenerator(AbstractGenerator):
    name = "quad_eq"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generation logic specific to quadratics
            a, b, c = [
                random.randint(
                    self.config["range"][0], self.config["range"][1]
                )
                for _ in range(3)
            ]
            # Ensure a is not zero to be a quadratic
            while a == 0:
                a = random.randint(
                    self.config["range"][0], self.config["range"][1]
                )

            plaintext_expr = ""
            formatted_expr = ""

            if a != 0:
                plaintext_expr += f"{a if a != 1 else ''}x^2"
                formatted_expr += f"{a} * x**2"
            if b != 0:
                plaintext_expr += f" + {b if b != 1 else ''}x"
                formatted_expr += f" + {b} * x"
            if c != 0:
                plaintext_expr += f" + {c}" if c != 0 else ""
                formatted_expr += f" + {c}" if c != 0 else ""

            # Create the prompt
            prompt = f"Factor the quadratic expression {plaintext_expr}."

            # Source code using SymPy to factor the expression
            exec_code = f"x = sp.symbols('x')\nexpr = {formatted_expr}\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.factor(expr))"

            sympy_result = self.execute(exec_code)

            x = sp.symbols("x")
            expr = a * x**2 + b * x + c
            factored_expr = sp.factor(expr)
            data.append(
                {
                    "instruction": prompt,
                    "sympy_code": self._get_token_wrapped_code(exec_code),
                    "sympy_exec": self._get_token_warpped_result(sympy_result),
                    "output": "This equation cannot be factored."
                    if str(expr) == str(factored_expr)
                    else f"The factored equation is ${sympy_result[AbstractGenerator.RESULT_SYMBOL]}$.",
                    "name": self.name,
                }
            )
        return data


# Subclass for Systems of Linear Equations
class SystemOfLinearEqGenerator(AbstractGenerator):
    name = "sys_lin_eq"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generation logic specific to systems of equations
            coeffs = [
                random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )
                for _ in range(4)
            ]
            constants = [
                random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )
                for _ in range(2)
            ]

            plaintext_eqs = [
                f"{coeffs[0]}x + {coeffs[1]}y = {constants[0]}",
                f"{coeffs[2]}x + {coeffs[3]}y = {constants[1]}",
            ]

            # Create the prompt
            prompt = "Solve the following system of linear equations:\n"
            prompt += f"1) {plaintext_eqs[0]}\n"
            prompt += f"2) {plaintext_eqs[1]}"

            # Source code using SymPy to solve the system
            exec_code = f"""
x, y = sp.symbols('x y')
eq1 = sp.Eq({coeffs[0]}*x + {coeffs[1]}*y, {constants[0]})
eq2 = sp.Eq({coeffs[2]}*x + {coeffs[3]}*y, {constants[1]})
solution = sp.solve((eq1, eq2), (x, y))
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(solution)
"""

            sympy_result = self.execute(exec_code)

            output_message = f"The solution to the system of equations is ${sympy_result[AbstractGenerator.RESULT_SYMBOL]}$"
            data.append(
                {
                    "instruction": prompt,
                    "sympy_code": self._get_token_wrapped_code(exec_code),
                    "sympy_exec": self._get_token_warpped_result(sympy_result),
                    "output": output_message,
                    "name": self.name,
                }
            )
        return data


# Subclass for Polynomial Long Division
class PolynomialLongDivGenerator(AbstractGenerator):
    name = "poly_long_div"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generation logic specific to polynomial long division
            # Create a random polynomial of degree n and a binomial divisor
            n = random.randint(
                self.config["poly_degree_min"], self.config["poly_degree_max"]
            )
            coefficients = [
                random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )
                for _ in range(n + 1)
            ]
            # Ensure leading coefficient is not zero
            coefficients[0] = coefficients[0] if coefficients[0] != 0 else 1
            poly = sp.Poly(coefficients, sp.symbols("x"))
            divisor_coeff = random.randint(
                self.config["coeff_range"][0], self.config["coeff_range"][1]
            )
            divisor = sp.Poly([1, -divisor_coeff], sp.symbols("x"))

            # Create the plaintext expression of the polynomial and the divisor
            plaintext_poly = (
                " + ".join(
                    [
                        f"{coeff}*x**{i}" if coeff != 0 else ""
                        for i, coeff in enumerate(reversed(coefficients))
                    ]
                )
                .replace("x**1 ", "x ")
                .replace(" 1*x", " x")
                .strip()
            )
            plaintext_divisor = f"x - {divisor_coeff}"

            # Create the prompt
            prompt = f"Divide the polynomial {plaintext_poly} by the binomial {plaintext_divisor}."

            # Source code using SymPy to perform the long division
            exec_code = f"""
x = sp.symbols('x')
dividend, divisor = sp.Poly({plaintext_poly}), sp.Poly({plaintext_divisor})
quotient, remainder = sp.div(dividend, divisor)
{AbstractGenerator.RESULT_SYMBOL} = (sp.latex(quotient.as_expr()), sp.latex(remainder.as_expr()))
"""

            sympy_result = self.execute(exec_code)

            quotient, remainder = sympy_result[AbstractGenerator.RESULT_SYMBOL]

            print("sympy_result = ", sympy_result)
            # Prepare the output message
            if remainder == "0":
                output_message = f"The quotient is ${quotient}$."
            else:
                output_message = f"The quotient is ${quotient}$ with a remainder of ${remainder}$."

            # Append the generated data
            data.append(
                {
                    "instruction": prompt,
                    "sympy_code": self._get_token_wrapped_code(exec_code),
                    "sympy_exec": self._get_token_warpped_result(sympy_result),
                    "output": output_message,
                    "name": self.name,
                }
            )
        return data


# Subclass for Simplifying Exponential Expressions
class SimplifyExponentExprGenerator(AbstractGenerator):
    name = "simplify_exponent"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generation logic specific to simplifying exponential expressions
            base = random.randint(
                self.config["base_range"][0], self.config["base_range"][1]
            )
            exp1 = random.randint(
                self.config["exp_range"][0], self.config["exp_range"][1]
            )
            exp2 = random.randint(
                self.config["exp_range"][0], self.config["exp_range"][1]
            )
            op = random.choice(["*", "/", "**"])  # Choose operation type

            execution_expr = ""
            if op == "**":
                # Power of a power (a^b)^c
                plaintext_expr = f"({base}^{exp1})^{exp2}"
                execution_expr = f"({base}**{exp1})**{exp2}"
            elif op == "*":
                # Product of powers a^b * a^c
                plaintext_expr = f"{base}^{exp1} * {base}^{exp2}"
                execution_expr = f"{base}**{exp1} * {base}**{exp2}"
            elif op == "/":
                # Quotient of powers a^b / a^c
                plaintext_expr = f"{base}^{exp1} / {base}^{exp2}"
                execution_expr = f"{base}**{exp1} / {base}**{exp2}"

            # Create the prompt
            prompt = f"Simplify the expression {plaintext_expr}."

            # Source code using SymPy to simplify the expression
            exec_code = f"""
expr = sp.sympify('{execution_expr}')
simplified_expr = sp.simplify(expr)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(simplified_expr)
"""

            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The simplified expression is ${result}$.",
                )
            )

        return data


# Subclass for GCD and LCM of Integers
class GcdLcmGenerator(AbstractGenerator):
    name = "gcd_lcm"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generate two random integers within the specified range
            num1 = random.randint(
                self.config["int_range"][0], self.config["int_range"][1]
            )
            num2 = random.randint(
                self.config["int_range"][0], self.config["int_range"][1]
            )

            # Create the prompt for GCD
            prompt = f"Calculate the greatest common divisor (GCD) of {num1} and {num2}."

            # Source code using SymPy to calculate the GCD
            exec_code = f"""
num1, num2 = {num1}, {num2}
gcd_result = sp.gcd(num1, num2)
{AbstractGenerator.RESULT_SYMBOL} = gcd_result
"""

            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    f"The GCD of {num1} and {num2} is " + "{result}.",
                )
            )

            # Create the prompt for LCM
            prompt = f"Calculate the least common multiple (LCM) of {num1} and {num2}."

            # Source code using SymPy to calculate the LCM
            exec_code = f"""
num1, num2 = {num1}, {num2}
lcm_result = sp.lcm(num1, num2)
{AbstractGenerator.RESULT_SYMBOL} = lcm_result
"""

            # Append the generated data
            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    f"The LCM of {num1} and {num2} is " + "{result}.",
                )
            )

        return data


# Subclass for Simplifying Algebraic Expressions
class SimplifyAlgebraicExprGenerator(AbstractGenerator):
    name = "simplify_algebraic_expr"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Generate random coefficients and exponents
            terms = []
            term_count = random.randint(
                self.config["min_terms"], self.config["max_terms"]
            )  # Configurable number of terms
            for _ in range(term_count):
                coefficient = random.randint(
                    self.config["coeff_range"][0],
                    self.config["coeff_range"][1],
                )
                exponent = random.randint(
                    self.config["exp_range"][0], self.config["exp_range"][1]
                )
                variable = random.choice(["x", ""])  # sometimes just a number
                term = (
                    f"{coefficient}*{variable}**{exponent}"
                    if exponent > 0 and variable
                    else f"{coefficient}"
                )
                terms.append(term)

            # Randomly decide to add or subtract terms
            expr = " + ".join(terms[:2]) + " ".join(
                random.choice([" + ", " - "]) + term for term in terms[2:]
            )

            # Format the expression for display
            plaintext_expr = (
                expr.replace("**1", "")
                .replace(" 1x", " x")
                .replace("**0", "")
                .replace("x**", "x^")
            )

            # Create the prompt
            prompt = f"Simplify the algebraic expression: {plaintext_expr}."

            # Source code using SymPy to simplify the expression
            exec_code = f"""
x = sp.symbols('x')
expr = sp.sympify('{expr}')
simplified_expr = sp.simplify(expr)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(simplified_expr)
"""

            # Append the generated data
            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The simplified expression is ${result}$.",
                )
            )
        return data


class AlgebraicEquationSolverGenerator(AbstractGenerator):
    name: str = "algebraic_equation_solver"

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            # Randomly choose an equation type
            eq_type = random.choice(self.config["equation_types"])

            # Symbols
            x = sp.symbols("x")

            # Define equation based on type
            if eq_type == "linear":
                a = random.randint(*self.config["linear_coeff_range"])
                b = random.randint(*self.config["linear_coeff_range"])
                equation = f"sp.Eq({a} * x + {b}, 0)"
                prompt = f"Solve the linear equation {a}*x + {b} = 0 for x."
            elif eq_type == "quadratic":
                a = random.randint(*self.config["quadratic_coeff_range"])
                b = random.randint(*self.config["quadratic_coeff_range"])
                c = random.randint(*self.config["quadratic_coeff_range"])
                equation = f"sp.Eq({a} * x**2 + {b} * x + {c}, 0)"
                prompt = f"Solve the quadratic equation {a}*x^2 + {b}*x + {c} = 0 for x."
            elif eq_type == "rational":
                a = random.randint(*self.config["rational_coeff_range"])
                b = random.randint(*self.config["rational_coeff_range"])
                c = random.randint(*self.config["rational_coeff_range"])
                d = random.randint(*self.config["rational_coeff_range"])
                equation = f"sp.Eq({a} / (x + {b}), {c} / (x + {d}))"
                prompt = f"Solve the rational equation {a}/(x + {b}) = {c}/(x + {d}) for x."
            elif eq_type == "exponential":
                a = random.randint(*self.config["exponential_base_range"])
                b = random.randint(*self.config["exponential_base_range"])
                equation = f"sp.Eq({a}**x, {b})"
                prompt = f"Solve the exponential equation {a}^x = {b} for x."

            # Randomly choose a solution method
            method = random.choice(self.config["solution_methods"])

            # Generate the code based on the chosen method
            if method == "solve":
                exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solve({equation}, x))"
            elif method == "solveset":
                exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solveset({equation}, x))"

            # Execute the code and format the result
            exec_code = "x = sp.symbols('x')\n" + exec_code

            # Append the generated data
            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The solution to the equation is $x = {result}$.",
                )
            )

        return data
