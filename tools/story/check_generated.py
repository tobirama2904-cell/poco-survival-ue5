#!/usr/bin/env python3
import subprocess,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];path=root/'Source/PocoSurvival/Private/Core/CityContent.cpp';before=hashlib.sha256(path.read_bytes()).hexdigest()
subprocess.run(['python3',str(root/'tools/story/compile_city.py')],check=True)
assert hashlib.sha256(path.read_bytes()).hexdigest()==before,'Authored city.json and checked-in native content disagree. Run the compiler and commit both.'
