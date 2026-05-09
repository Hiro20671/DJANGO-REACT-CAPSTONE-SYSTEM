import os

dirs_to_search = [
    r"c:\BACKUP CAPSTONE SYSTEM DJANGO-REACT\frontend",
    r"c:\BACKUP CAPSTONE SYSTEM DJANGO-REACT\backend\apps\core\templates"
]

replacements = {
    "Child Care Management System": "BMV3 Child Care Management System",
    "Childcare Management System": "BMV3 Child Care Management System",
    "Child Care System": "BMV3 Child Care Management System"
}

for root_dir in dirs_to_search:
    for root, dirs, files in os.walk(root_dir):
        if "node_modules" in root or ".git" in root or "dist" in root:
            continue
        for file in files:
            if file.endswith((".html", ".jsx", ".js")):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    for old, new in replacements.items():
                        content = content.replace(new, old) # temporarily revert if already applied
                        content = content.replace(old, new)
                    
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Updated {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
