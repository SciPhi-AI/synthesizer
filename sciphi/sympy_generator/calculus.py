import random
import sympy as sp  # ignore

from sciphi.sympy_generator.generators import AbstractGenerator


# Below is the template for one of the generators - DifferentiationGeneratorclass DifferentiationGenerator(AbstractGenerator):
class DifferentiationGenerator(AbstractGenerator):
    name: str = "differentiation"

    def __init__(self, config, interpreter):
        super().__init__(config, interpreter)
        self.basic_functions = [
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

    def _generate_random_function(self, x):
        # Randomly choose number of terms
        num_terms = random.randint(
            self.config["num_terms"][0], self.config["num_terms"][1]
        )  # For example, 2 to 5 terms
        # Generate a random expression
        func_expr, raw_expr = "", ""
        for _ in range(num_terms):
            # Randomly select a basic function
            func = random.choice(self.basic_functions)
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

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            x = sp.symbols("x")
            # Generate a random function string
            func_expr, raw_expr = self._generate_random_function(x)

            # Create the prompt
            prompt = (
                f"Differentiate the function {raw_expr} with respect to x."
            )

            # Executable code that SymPy can use to perform the differentiation
            exec_code = f"""
import sympy as sp
x = sp.symbols('x')
function = {func_expr}
differentiated_function = sp.diff(function, x)
simplified_result = sp.simplify(differentiated_function)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(simplified_result)
"""
            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The derivative of the function is ${result}$.",
                )
            )

        return data


class LimitCalculationGenerator(AbstractGenerator):
    name: str = "limit_calculation"

    def __init__(self, config, interpreter):
        super().__init__(config, interpreter)
        # In addition to sin, cos, etc., you may want to include log and sqrt,
        # but make sure to handle the edge cases they introduce (like log(0) or sqrt(-1)).
        self.basic_functions = [
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

    def _generate_random_function(self, x):
        num_terms = random.randint(
            self.config["num_terms"][0], self.config["num_terms"][1]
        )
        func_expr, raw_expr = "", ""

        for _ in range(num_terms):
            # Randomly select a basic function
            func = random.choice(self.basic_functions)
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

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            x = sp.symbols("x")
            # Avoiding problematic points such as division by zero or log of zero
            approach_value = int(random.uniform(-10, 10))

            if approach_value == 0:
                approach_value += random.choice([1, -1]) * 0.1

            # Generate a random function string
            func_expr, raw_expr = self._generate_random_function(x)

            # Creating the prompt
            prompt = f"Calculate the limit of {raw_expr} as x approaches {approach_value}."

            # Executable code that SymPy can use to calculate the limit
            exec_code = f"""
import sympy as sp
x = sp.symbols('x')
function = {func_expr}
limit_result = sp.limit(function, x, {approach_value})
simplified_result = sp.simplify(limit_result)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(simplified_result)
"""
            print("exec_code = ", exec_code)

            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The limit of the function as x approaches "
                    + str(approach_value)
                    + " is ${result}$.",
                )
            )

        return data


class IntegrationGenerator(AbstractGenerator):
    name: str = "integration"

    def __init__(self, config, interpreter):
        super().__init__(config, interpreter)
        # You can reuse the basic functions, but make sure they are integrable over the desired range
        self.basic_functions = [
            "sp.sin",
            "sp.cos",
            "sp.exp",
            "sp.tanh",
            "sp.cosh",
            "sp.log",
            "x",  # x represents the identity function
            "1/x",  # This represents a simple reciprocal function
            "x**2",
            "x**3",
            # Add or remove functions as needed
        ]

    def _generate_random_function(self, x):
        # Randomly choose number of terms
        num_terms = random.randint(
            self.config["num_terms"][0], self.config["num_terms"][1]
        )  # For example, 2 to 5 terms
        # Generate a random expression
        func_expr, raw_expr = "", ""
        for _ in range(num_terms):
            # Randomly select a basic function
            func = random.choice(self.basic_functions)
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

    def generate(self):
        data = []
        for _ in range(self.config["num_samples"]):
            x = sp.symbols("x")

            # Generate a random function string
            func_expr, raw_expr = self._generate_random_function(x)

            # Create the prompt
            prompt = f"Integrate the function {raw_expr} with respect to x."

            # Executable code that SymPy can use to perform the integration
            exec_code = f"""
import sympy as sp
x = sp.symbols('x')
function = {func_expr}
integrated_function = sp.integrate(function, x)
{AbstractGenerator.RESULT_SYMBOL} = sp.latex(integrated_function)
"""
            # Append the generated data
            data.append(
                self._get_formatted_output(
                    prompt,
                    exec_code,
                    "The integral of the function is ${result}$.",
                )
            )

        return data
