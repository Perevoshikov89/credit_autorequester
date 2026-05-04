import vkbeautify as vkb

def build_ko(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        xml = f.read()

    formatted = vkb.xml(xml)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(formatted)