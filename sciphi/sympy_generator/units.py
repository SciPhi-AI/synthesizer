import random
import sympy as sp

from sciphi.sympy_generator.generators import AbstractGenerator


class UnitEqGenerator(AbstractGenerator):
    name = "unit_generator"

    def _generate_add(self, x, y):
        prompt = f"What is {x} plus {y}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = {x} + {y}"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The sum equals {x + y}.",
        )

    def _generate_sub(self, x, y):
        prompt = f"What is {x} minus {y}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = {x} - {y}"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The difference equals {x - y}.",
        )

    def _generate_mul(self, x, y):
        prompt = f"What is {x} times {y}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = {x} * {y}"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The product equals {x * y}.",
        )

    def _generate_div(self, x, y):
        prompt = f"What is {x} divided by {y}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = {x} / {y}"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The quotient equals {x / y}.",
        )

    def _generate_sqrt(self, x):
        prompt = f"Can you simplify the square root of {x}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.sqrt({x})"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The square root equals {result}.",
        )

    def _generate_expand(self, a, b):
        prompt = f"Can you expand (x+{a})(x+{b})?"
        exec_code = f"x = sp.symbols('x')\nexpr = (x + {a}) * (x + {b})\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.expand(expr))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The expanded term is {result}.",
        )

    def _generate_power(self, x, n):
        prompt = f"What is {x} to the power of {n}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = {x} ** {n}"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"{x} to the power of {n} equals " + "{result}.",
        )

    def _generate_factor(self, a, b):
        prompt = f"Can you factor x^2 + {a}x + {b}?"
        exec_code = f"x = sp.symbols('x')\nexpr = x**2 + {a}*x + {b}\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.factor(expr))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The factored form is {result}.",
        )

    def _generate_simplify_frac(self, a, b):
        prompt = f"Can you simplify the fraction {a}/{b}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.Rational({a}, {b}).simplify()"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The simplified fraction is {result}.",
        )

    def _generate_prime_factor(self, x):
        prompt = f"What is the prime factorization of {x}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.factorint({x})"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The prime factors of {x} are " + "{result}.",
        )

    def _generate_solve_eq(self, a, b, c):
        prompt = f"What is the solution to the equation {a}x + {b} = {c}?"
        exec_code = f"x = sp.symbols('x')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solve({a}*x + {b} - {c}, x))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The solution is x = {result}.",
        )

    def _generate_derivative(self, func_expr, raw_expr):
        prompt = f"What is the derivative of {raw_expr} with respect to x?"
        exec_code = f"x = sp.symbols('x')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.diff({func_expr}, x))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The derivative is {result}.",
        )

    def _generate_integral(self, func_expr, raw_expr):
        prompt = f"What is the integral of {raw_expr} with respect to x?"
        exec_code = f"x = sp.symbols('x')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.integrate({func_expr}, x))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The integral is {result}.",
        )

    def _generate_limit(self, func_expr, raw_expr):
        point = random.randint(1, 10)
        prompt = f"What is the limit of {raw_expr} as x approaches {point}?"
        exec_code = f"x = sp.symbols('x')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.limit({func_expr}, x, {point}))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The limit is {result}.",
        )

    def _generate_series_expansion(self, func_expr, raw_expr, n_terms=3):
        point = random.randint(1, 10)
        prompt = f"What is the series expansion of {raw_expr} around {point} to {n_terms} terms?"
        exec_code = f"x = sp.symbols('x')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.series({func_expr}, x, {point}, {n_terms}).removeO())"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The series expansion is {result}.",
        )

    def _generate_solve_system(self, equations):
        prompt = "Solve the system of equations: " + ", ".join(
            [str(eq) for eq in equations]
        )
        exec_code = f"x, y, z = sp.symbols('x y z')\n{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solve({equations}, (x, y, z)))"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The solutions are {result}.",
        )

    def _generate_matrix_det(self, matrix):
        prompt = f"What is the determinant of the matrix {matrix}?"
        exec_code = f"M = sp.Matrix({matrix})\n{AbstractGenerator.RESULT_SYMBOL} = M.det()"
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The determinant is {result}.",
        )

    def _generate_complex_add(self, z1, z2):
        prompt = f"What is the sum of the complex numbers {z1} and {z2}?"
        exec_code = f"{AbstractGenerator.RESULT_SYMBOL} = sp.Add({z1}, {z2})"
        return self._get_formatted_output(
            prompt,
            exec_code,
            f"The sum of the complex numbers is {z1 + z2}.",
        )

    def _generate_find_zeros(self, coeffs):
        # Create a polynomial expression from the coefficients
        x = sp.symbols("x")
        expr = sum(c * x**i for i, c in enumerate(coeffs[::-1]))

        # Check for non-zero coefficients and generate polynomial term strings
        terms = []
        for i, coeff in enumerate(coeffs):
            if coeff != 0:
                if i == 0:
                    terms.append(f"{coeff}")
                elif i == 1:
                    terms.append(f"{coeff}*x")
                else:
                    terms.append(f"{coeff}*x**{i}")

        # Join terms to create the polynomial expression string
        result = " + ".join(reversed(terms))

        # Generate the prompt
        prompt = f"Find the zeros of the polynomial {result}."

        # Generate the exec_code, making sure to sympify the string expression
        exec_code = f"""
import sympy as sp
x = sp.symbols('x')
expr = sp.sympify("{result}")
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(sp.solve(expr, x))
"""
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The zeros of the polynomial are {result}.",
        )

    def _generate_random_ode(self):
        x = sp.symbols("x")
        f = sp.Function("f")

        # Generate a simple first-order ODE for demonstration purposes.
        # This can be expanded to generate more complex ODEs.
        ode_order = random.randint(1, 2)  # First or second order for example
        ode = f(x).diff(x, ode_order) + random.randint(1, 3) * f(x)
        return ode

    def _generate_ode_solver(self, ode=None, func="f", var="x"):
        if ode is None:
            ode = (
                self._generate_random_ode()
            )  # Generate a random ODE if none provided

        prompt = (
            f"Solve the differential equation {ode} with respect to {var}."
        )
        exec_code = (
            f"f = sp.Function('{func}')\n"
            f"{var} = sp.symbols('{var}')\n"
            f"ode_sol = sp.dsolve({ode}, f({var}))\n"
            f"{AbstractGenerator.RESULT_SYMBOL} = sp.latex(ode_sol)"
        )
        print("exec_code = ", exec_code)
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The solution to the differential equation is {result}.",
        )

    def _generate_matrix_inv(self, matrix):
        prompt = f"What is the inverse of the matrix {matrix}?"
        exec_code = (
            f"M = sp.Matrix({matrix})\n"
            f"if M.det() != 0:\n"
            f"    {AbstractGenerator.RESULT_SYMBOL} = sp.latex(M.inv())\n"
            f"else:\n"
            f"    {AbstractGenerator.RESULT_SYMBOL} = 'Matrix is not invertible.'"
        )
        return self._get_formatted_output(
            prompt,
            exec_code,
            "The inverse of the matrix is {result}.",
        )

    def _generate_trig_solve(self):
        # Define possible trigonometric functions and their coefficients
        trig_funcs = ["sin", "cos", "tan"]
        # We define coefficients as strings for sympify to parse correctly
        coefficients = [
            "1",
            "-1",
            "1/2",
            "-1/2",
            "sqrt(2)",
            "-sqrt(2)",
            "sqrt(3)",
            "-sqrt(3)",
        ]

        # Generate a random trigonometric function with a random coefficient
        trig_func = random.choice(trig_funcs)
        coefficient = random.choice(coefficients)
        constant_term = random.choice(coefficients)

        # Generate a random coefficient for x
        x_coefficient = random.choice(coefficients)

        # Create the string representation of the trigonometric equation
        eq_str = f"{coefficient} * {trig_func}({x_coefficient} * x) + {constant_term}"

        # Generate the prompt using LaTeX for better readability
        prompt = f"Solve the trigonometric equation \\({eq_str} = 0\\)."

        # Generate the exec_code
        # We wrap the sympify in a try-except block in case of parsing errors.
        exec_code = f"""
import sympy as sp
x = sp.symbols('x')
# Define the equation as a string and convert to sympy equation
eq = sp.sympify("{eq_str}")
solutions = sp.solve(eq, x)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(solutions)
"""

        return self._get_formatted_output(
            prompt, exec_code, "The solutions to the equation are {result}."
        )

    def _generate_random_function(self, x="x"):
        basic_functions = [
            "sp.sin",
            "sp.cos",
            "sp.exp",
            "sp.tanh",
            "sp.cosh",
            "sp.log",
            "sp.sqrt",
            "x",
            "1/x",  # This represents a simple reciprocal function
            "x**2",
            "x**3",
        ]

        num_terms = random.randint(2, 3)
        func_expr, raw_expr = "", ""

        for _ in range(num_terms):
            # Randomly select a basic function
            func = random.choice(basic_functions)
            # Apply it to a random coefficient times x
            coeff = random.randint(
                1, 3
            )  # Coefficients between 1 and 3 for simplicity
            operator = random.choice(["+", "-", "*", "/"])
            func_expr += (
                f"{func}({coeff} * {x}) " + operator + " "
                if "sp" in func
                else f"{coeff} * {func} " + operator + " "
            )
            raw_expr += (
                f"{func[3:]}({coeff}{x}) " + operator + " "
                if "sp" in func
                else f"{coeff} * {func} " + operator + " "
            )

        return func_expr[:-3], raw_expr[:-3].replace("1x", "x")

    def _generate_random_matrix(self, size=(3, 3)):
        """Generates a random matrix of the given size."""
        return [
            [random.randint(1, 10) for _ in range(size[1])]
            for _ in range(size[0])
        ]

    def _generate_random_system(self, num_equations=3):
        """Generates a random system of linear equations."""
        x, y, z = sp.symbols("x y z")
        equations = []
        for _ in range(num_equations):
            coefficients = [random.randint(1, 10) for _ in range(3)]
            rhs = random.randint(1, 20)
            equation = (
                coefficients[0] * x
                + coefficients[1] * y
                + coefficients[2] * z
                - rhs
            )
            equations.append(equation)
        return equations

    def generate(self):
        operations = {
            "add": self._generate_add,
            "sub": self._generate_sub,
            "mul": self._generate_mul,
            "div": self._generate_div,
            "sqrt": self._generate_sqrt,
            "expand": self._generate_expand,
            "power": self._generate_power,
            "factor": self._generate_factor,
            "simplify_frac": self._generate_simplify_frac,
            "prime_factor": self._generate_prime_factor,
            "solve_eq": self._generate_solve_eq,
            "derivative": self._generate_derivative,
            "integral": self._generate_integral,
            "limit": self._generate_limit,
            "series_expansion": self._generate_series_expansion,
            "solve_system": self._generate_solve_system,
            "matrix_det": self._generate_matrix_det,
            "complex_add": self._generate_complex_add,
            "matrix_inv": self._generate_matrix_inv,
            "trig_solve": self._generate_trig_solve,
            # "ode_solver": self._generate_ode_solver,
            "find_zeros": self._generate_find_zeros,
        }

        data = []
        for _ in range(self.config["num_samples"]):
            x, y = random.randint(1_000, 1_000_000), random.randint(
                1_000, 1_000_000
            )
            a, b, c = (
                random.randint(1, 1_000_000),
                random.randint(1, 1_000_000),
                random.randint(1, 1_000_000),
            )
            generator = random.choice(list(operations.keys()))
            func_expr, raw_expr = self._generate_random_function()

            print("generator = ", generator)
            # Some generators require only one or two numbers, adjust the arguments accordingly.
            if generator in ["sqrt", "prime_factor"]:
                problem_data = operations[generator](x)
            elif generator == "find_zeros":
                # Generate random coefficients for the polynomial
                degree = random.randint(2, 4)  # Choose degree of polynomial
                coeffs = [random.randint(-10, 10) for _ in range(degree + 1)]
                problem_data = operations[generator](coeffs)
            elif generator in [
                "expand",
                "factor",
                "sub",
                "div",
                "simplify_frac",
                "complex_add",
                "add",
                "mul",
            ]:
                problem_data = operations[generator](a, b)
            elif generator == "solve_eq":
                problem_data = operations[generator](a, b, c)
            elif generator == "power":
                n = random.randint(2, 5)
                problem_data = operations[generator](x, n)
            elif generator in [
                "derivative",
                "integral",
                "limit",
                "series_expansion",
            ]:
                problem_data = operations[generator](func_expr, raw_expr)
            elif generator == "solve_system":
                # Generate a set of random equations for the system
                equations = self._generate_random_system()
                problem_data = operations[generator](equations)
            elif generator in ["matrix_det", "matrix_inv"]:
                # Generate a random matrix
                matrix = self._generate_random_matrix()
                problem_data = operations[generator](matrix)
            elif generator == "ode_solver":
                raise NotImplementedError("ODE solver is not implemented yet.")
            else:
                problem_data = operations[generator]()

            data.append(problem_data)
        return data
