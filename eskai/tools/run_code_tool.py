import subprocess
from typing import Tuple


class RunCodeTool:
    """
    Tool for executing code snippets in a safe subprocess.
    """

    def __init__(self, name: str, python_executable: str = "python"):
        self.name = name
        self.python_executable = python_executable

    def run_code(self, code: str) -> Tuple[int, str, str]:
        """
        Execute Python code in a subprocess and capture output.
        """
        process = subprocess.Popen(
            [self.python_executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = process.communicate()
        return process.returncode, out, err
    
if __name__ == "__main__":
    code_tool = RunCodeTool(name="CodeExecutor")
    return_code, output, error = code_tool.run_code("print('Hello, World!')")
    print(f"Return Code: {return_code}\nOutput: {output}\nError: {error}")
