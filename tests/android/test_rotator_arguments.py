import ast,unittest
from pathlib import Path
class RotatorCallTests(unittest.TestCase):
    def test_scene_rotators_are_named(self):
        root=Path(__file__).resolve().parents[2]
        for path in (root/'tools/scene').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='Rotator':
                    self.assertFalse(node.args,f'{path}:{node.lineno}: use named roll/pitch/yaw')
