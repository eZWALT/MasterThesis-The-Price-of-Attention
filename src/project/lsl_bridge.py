#!/usr/bin/env python3
"""
LSL Marker Emitter — corre en Atlas.

Crea un outlet LSL "experiment_lab_pilot" y envía markers cada 2s.
Visible para actiCHamp en la red local.

Uso:
  python3 lsl_bridge.py                  # markers cada 2s
  python3 lsl_bridge.py --interval 0.5   # intervalo personalizado
"""

import sys, time, random
from pylsl import StreamInfo, StreamOutlet

OUTLET_NAME = "experiment_lab_pilot"
outlet = StreamOutlet(StreamInfo(OUTLET_NAME, "Markers", 1, 0, "string", "atlas_bridge"))

EVENTOS = [
    "CONDITION_START", "AD_SHOWN", "AD_CLICKED", "USER_MESSAGE",
    "TRIAL_END", "SURVEY_START", "STIMULUS", "RESPONSE",
]

interval = 2.0
if "--interval" in sys.argv:
    idx = sys.argv.index("--interval")
    if idx + 1 < len(sys.argv):
        interval = float(sys.argv[idx + 1])

print(f"LSL outlet \"{OUTLET_NAME}\" activo desde Atlas — marker cada {interval}s")
print(f"Visible en la red local para actiCHamp", flush=True)

i = 0
try:
    while True:
        ev = random.choice(EVENTOS)
        payload = f"{ev}|{i:03d}"
        outlet.push_sample([payload])
        print(f"  >> {payload}", flush=True)
        i += 1
        time.sleep(interval)
except KeyboardInterrupt:
    print("\nDeteniendo...")
finally:
    outlet = None
