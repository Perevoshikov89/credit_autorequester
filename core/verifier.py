import subprocess as sp

def unsign_file(file_name: str):
    cmd = f"cp.bat {file_name}"
    result = sp.run(cmd, shell=True)

    if result.returncode != 0:
        raise RuntimeError("Ошибка снятия ЭЦП")