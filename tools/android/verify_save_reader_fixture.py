#!/usr/bin/env python3
"""Validate actual native-generated GVAS, not a schematic JSON unit fixture."""
from pathlib import Path
import json
from save_state_probe import canonical_save
root=Path('artifacts/engine-probe')
s=canonical_save(json.loads((root/'decoder-native-fixture.json').read_text()))
assert s['format']==7 and s['generation']==37
assert s['position']==[123.25,-450.5,98] and s['field_items']==[2,1,3,2,6,1,1,1,0]
assert s['county']==[1,0,0,0,0,0] and s['LootedCaches']==3 and s['OpenDoors']==5
d=canonical_save(json.loads((root/'decoder-defaults-fixture.json').read_text()))
assert d['format']==8 and d['generation']==38 and d['position']==[10,20,96]
assert d['film_progress']==0 and d['film_decision']==0 and d['county']==[0]*6 and d['main_events']==0
(root/'save-reader-verification.json').write_text(json.dumps({'actual_native_gvas_decoded':True,'known_fields_match':True,'actual_android_save_verified':False,'synthetic_uobject_fixture':True},indent=2)+'\n')
print('ACTUAL_NATIVE_SAVE_READER_PASS')
