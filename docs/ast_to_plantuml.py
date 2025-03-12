import ast
import os


def parse_classes_from_file(filepath):
    with open(filepath, encoding="utf-8") as file:
        tree = ast.parse(file.read())

    classes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            classes[class_name] = bases
    return classes


def generate_plantuml(classes):
    uml = "@startuml\n"
    for cls, bases in classes.items():
        uml += f"class {cls}\n"
        for base in bases:
            uml += f"{base} <|-- {cls}\n"
    uml += "@enduml"
    return uml


def traverse_directory_and_generate_uml(directory):
    all_classes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                file_classes = parse_classes_from_file(filepath)
                all_classes.update(file_classes)
    return generate_plantuml(all_classes)


if __name__ == "__main__":
    directory = "../backend"  # Adjust this path as needed
    uml_output = traverse_directory_and_generate_uml(directory)
    with open("auto_generated_uml.puml", "w", encoding="utf-8") as f:
        f.write(uml_output)
