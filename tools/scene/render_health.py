"""Fatal visual regressions found in real UE renderer logs, not pixel guesses."""
def material_failures(text):
 needles=('Failed to compile Material for platform','missing bUsedWithInstancedStaticMeshes=True','Missing Saturate input')
 return list(dict.fromkeys(line.strip() for line in text.splitlines() if any(s in line for s in needles)))
