import vkbeautify as vkb

def format_xml(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(vkb.xml(data))