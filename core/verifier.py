import subprocess as sp
import shlex

CREATE_NO_WINDOW = 0x08000000

def verify_response(input_file: str):
    with open("cp_yes.baton", "r") as yesf:
        args = shlex.split(f'cp.bat {input_file}')
        sp.run(args, stdin=yesf, creationflags=CREATE_NO_WINDOW)

    return "des_" + input_file