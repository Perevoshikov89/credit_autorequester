import subprocess as sp

def sign_file(file_name: str):
    cmd = f"ecp.bat {file_name}"
    result = sp.run(cmd, shell=True)

    if result.returncode != 0:
        raise RuntimeError("Ошибка ЭЦП подписи")