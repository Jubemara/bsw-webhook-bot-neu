# 🔍 helpers_checker.py – Analyse-Skript für deinen helpers-Ordner
import os
import ast
from pathlib import Path

HELPERS_DIR = Path("helpers")

# Alle Python-Dateien im helpers-Ordner
py_files = list(HELPERS_DIR.glob("*.py"))

used_imports = set()
defined_functions = {}
used_functions = set()

# Hilfsfunktion zur Analyse einer Datei
def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    tree = ast.parse(content)
    
    # Funktionen sammeln
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defined_functions[node.name] = filepath.name
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                used_functions.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                used_functions.add(node.func.attr)
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                used_imports.add(alias.name)
        if isinstance(node, ast.Import):
            for alias in node.names:
                used_imports.add(alias.name)

# Alle Dateien analysieren
for file in py_files:
    analyze_file(file)

# Ungenutzte Funktionen finden
dead_functions = [name for name in defined_functions if name not in used_functions]

print("\n✅ Analyse abgeschlossen:")
print(f"🔎 Untersuchte Dateien: {[f.name for f in py_files]}")

if dead_functions:
    print("\n⚠️ Möglicherweise ungenutzte Funktionen:")
    for name in dead_functions:
        print(f"  - {name} (in {defined_functions[name]})")
else:
    print("\n✅ Keine ungenutzten Funktionen gefunden.")

# Zirkuläre Imports grob erkennen
if "texttools" in used_imports and any("texttools.py" in str(f) for f in py_files):
    print("\n🚨 Verdacht auf zirkulären Import in texttools.py")

print("\n💡 Tipp: Dead Code bitte manuell prüfen, ob versehentlich nicht aufgerufen.")
