# Abstract Base Class for generators
class AbstractGenerator:
    EXEC_HEADER = "import sympy as sp\n\n"

    CODE_START_SYMBOL = "<python>"
    CODE_END_SYMBOL = "<python/>"

    RESULT_START_SYMBOL = "<python_result>"
    RESULT_END_SYMBOL = "<python_result/>"

    RESULT_SYMBOL = "FINAL_RESULT"

    def __init__(self, config, interpreter):
        self.config = config
        self.interpreter = interpreter

    def generate(self):
        raise NotImplementedError(
            "Each generator must implement the generate method."
        )

    def execute(self, exec_code):
        stdout, result = self.interpreter.update_and_run_env(
            f"{AbstractGenerator.EXEC_HEADER}{exec_code}",
            vars_to_extract=[AbstractGenerator.RESULT_SYMBOL],
        )
        if stdout:
            return "None"
            # raise ValueError("Execution failed, no output captured")
        return result

    def _get_token_wrapped_code(self, exec_code):
        return f"{AbstractGenerator.CODE_START_SYMBOL}\n{exec_code}\n{AbstractGenerator.CODE_END_SYMBOL}"

    def _get_token_warpped_result(self, sympy_result):
        return f"{AbstractGenerator.RESULT_START_SYMBOL}\n{sympy_result[AbstractGenerator.RESULT_SYMBOL]}\n{AbstractGenerator.CODE_END_SYMBOL}"

    def _get_formatted_output(self, prompt, exec_code, output_template):
        print("exec_code = ", exec_code)
        sympy_result = self.execute(exec_code)

        # Prepare the output message
        output_message = output_template.format(
            result=sympy_result[AbstractGenerator.RESULT_SYMBOL]
        )

        return {
            "instruction": prompt,
            "sympy_code": self._get_token_wrapped_code(exec_code),
            "sympy_exec": self._get_token_warpped_result(sympy_result),
            "output": output_message,
            "name": self.name,
        }


# Factory for instantiating generators
class GeneratorFactory:
    generators = {}

    @classmethod
    def register_generator(cls, key, generator):
        cls.generators[key] = generator

    @classmethod
    def create(cls, key, config, interpreter):
        generator = cls.generators.get(key)
        if not generator:
            raise ValueError(key)
        return generator(config, interpreter)
