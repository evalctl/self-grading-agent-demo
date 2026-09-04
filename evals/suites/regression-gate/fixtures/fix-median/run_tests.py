"""Runner: execute the frozen test suite in the sealed workspace.

Writes combined test output to EVALCTL_OUTPUT_FILE and exits with the test
process return code, so evalctl's exit-code and contains scorers can grade it.
"""
import os
import subprocess
import sys

workspace = os.environ.get("EVALCTL_WORKSPACE", os.getcwd())
env = dict(os.environ)
env["PYTHONPATH"] = workspace + os.pathsep + env.get("PYTHONPATH", "")

proc = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", workspace, "-v"],
    cwd=workspace,
    env=env,
    capture_output=True,
    text=True,
)

combined = proc.stdout + proc.stderr
output_file = os.environ.get("EVALCTL_OUTPUT_FILE")
if output_file:
    with open(output_file, "w") as handle:
        handle.write(combined)
sys.stdout.write(combined)
sys.exit(proc.returncode)
