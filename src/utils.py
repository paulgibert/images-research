import subprocess


def bash(cmd: str) -> str:
    bytes = subprocess.check_output(cmd, shell=True)
    return bytes.decode("utf-8")[:-1]