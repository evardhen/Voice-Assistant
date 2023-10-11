import os
import re

with open('installed_packages.txt', 'r') as f:
    installed_packages = f.read()

# Assuming your project is in a folder named 'my_project'
project_path = 'my_project'
used_packages = set()

for dirpath, dirnames, filenames in os.walk(project_path):
    for filename in filenames:
        if filename.endswith('.py'):
            with open(os.path.join(dirpath, filename), 'r') as f:
                content = f.read()
                imports = re.findall(r'^\s*import\s+(\S+)', content, re.MULTILINE)
                imports += re.findall(r'^\s*from\s+(\S+)\s+import', content, re.MULTILINE)
                used_packages.update(imports)

unused_packages = [pkg for pkg in installed_packages.split('\n') if pkg.split('=')[0].strip() not in used_packages]

print('Unused packages:')
for pkg in unused_packages:
    print(pkg)
