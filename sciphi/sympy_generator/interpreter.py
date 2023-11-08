import io
import contextlib
import multiprocessing

TIMEOUT_SECONDS = 5


def execute_code_in_process(code, output_pipe, vars_to_extract):
    """The function to execute the provided code; to be run in a separate process."""
    output_buffer = io.StringIO()
    extracted_variables = {}
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code, {}, extracted_variables)
        extracted_values = {
            var: extracted_variables[var]
            for var in vars_to_extract
            if var in extracted_variables
        }
        output_pipe.send((output_buffer.getvalue(), extracted_values))
    except Exception as e:
        output_pipe.send((f"Execution failed with error: {e}", {}))
    finally:
        output_pipe.close()


class PyInterpreter:
    """A simple Python code interpreter that can execute Python code extracted from markdown."""

    SUCCESS_STRING = "Execution successful."

    def __init__(self, timeout_seconds=TIMEOUT_SECONDS):
        self.source_code = ""
        self.timeout_seconds = timeout_seconds

    def __repr__(self) -> str:
        return f"PyInterpreter(source_code={self.source_code})"

    def _execute_code(self, code: str, vars_to_extract: list) -> str:
        """Executes the provided code in a separate process, captures its output, and extracts specified variables."""
        output_pipe_parent, output_pipe_child = multiprocessing.Pipe()
        process = multiprocessing.Process(
            target=execute_code_in_process,
            args=(code, output_pipe_child, vars_to_extract),
        )

        process.start()
        process.join(self.timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join()
            return "Execution timed out.", {}

        if output_pipe_parent.poll():
            return output_pipe_parent.recv()
        else:
            return "No output received from execution.", {}

    def update_and_run_env(
        self, markdown_code: str, vars_to_extract: list = None
    ) -> tuple:
        """Updates the environment with the provided markdown code, executes it, and returns specified variables."""
        if vars_to_extract is None:
            vars_to_extract = ["FINAL_SOLUTION"]  # Ensure this is a list
        self.source_code = self._extract_code(markdown_code)
        exec_result, extracted_vars = self._execute_code(
            self.source_code, vars_to_extract
        )
        return exec_result, extracted_vars

    @staticmethod
    def _extract_code(markdown_code: str) -> str:
        """Extracts executable code from the markdown formatted string."""
        if "```python" in markdown_code:
            markdown_code = markdown_code.split("```python")[1]
        return markdown_code.split("```")[0].strip()

    # import io
    # import contextlib

    # class PyInterpreter:
    #     """A simple Python code interpreter that can execute Python code extracted from markdown."""

    #     SUCCESS_STRING = "Execution successful."

    #     def __init__(self):
    #         self.source_code = ""
    #         self.extracted_variables = {}

    #     def __repr__(self) -> str:
    #         return f"PyInterpreter(source_code={self.source_code})"

    #     def _execute_code(
    #         self, code: str, output_buffer: io.StringIO, vars_to_extract: list
    #     ) -> str:
    #         """Executes the provided code, captures its output, and extracts specified variables."""
    #         try:
    #             with contextlib.redirect_stdout(output_buffer):
    #                 exec(code, {}, self.extracted_variables)
    #             extracted_values = {
    #                 var: self.extracted_variables[var]
    #                 for var in vars_to_extract
    #                 if var in self.extracted_variables
    #             }
    #             return output_buffer.getvalue(), extracted_values
    #         except Exception as e:
    #             return f"Execution failed with error: {e}", {}

    #     def update_and_run_env(
    #         self, markdown_code: str, vars_to_extract: list = None
    #     ) -> tuple:
    #         """Updates the environment with the provided markdown code, executes it, and returns specified variables."""
    #         if vars_to_extract is None:
    #             vars_to_extract = ["FINAL_SOLUTION"]  # Ensure this is a list
    #         self.source_code = self._extract_code(markdown_code)
    #         output_buffer = io.StringIO()
    #         exec_result, extracted_vars = self._execute_code(
    #             self.source_code, output_buffer, vars_to_extract
    #         )
    #         return exec_result, extracted_vars

    #     @staticmethod
    #     def _extract_code(markdown_code: str) -> str:
    #         """Extracts executable code from the markdown formatted string."""
    #         if "```python" in markdown_code:
    #             markdown_code = markdown_code.split("```python")[1]
    #         return markdown_code.split("```")[0].strip()
