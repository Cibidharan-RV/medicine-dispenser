import os
import re

directory = r"d:\projects\medicine-dispenser\backend\models"

def replace_match(match):
    table_name = match.group(2)
    if table_name == "USER":
        return f"{match.group(1)}{table_name}{match.group(3)}"
    else:
        return f"{match.group(1)}{table_name.lower()}{match.group(3)}"

for root, _, files in os.walk(directory):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r") as file:
                content = file.read()
                
            new_content = re.sub(r'(ForeignKey\(")([A-Z_]+)(\.)', replace_match, content)
            new_content = re.sub(r'(\[")([A-Z_]+)(\.)', replace_match, new_content)
            
            if content != new_content:
                with open(path, "w") as file:
                    file.write(new_content)
                print(f"Updated {f}")
