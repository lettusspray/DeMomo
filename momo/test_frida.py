#!/usr/bin/env python3
import frida

try:
    device = frida.get_usb_device()
    print(f"Device: {device.id}")
    processes = device.enumerate_processes()
    momo_procs = [p for p in processes if 'momo' in p.name.lower() or 'mtn' in p.name.lower()]
    if momo_procs:
        for p in momo_procs:
            print(f"Found: PID={p.pid}, Name={p.name}")
    else:
        print("No momo processes found. Listing all processes:")
        for p in processes[:20]:
            print(f"  {p.pid}: {p.name}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
