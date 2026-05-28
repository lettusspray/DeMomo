#!/usr/bin/env python3
"""
Deploy Frida script to MoMo PSB via Python API
"""
import frida
import sys

def main():
    # Connect to USB device
    try:
        device = frida.get_usb_device()
        print(f"[✓] Connected to device: {device.id}")
    except Exception as e:
        print(f"[✗] Failed to connect to USB device: {e}")
        sys.exit(1)
    
    # Attach to the running MoMo process  
    try:
        # Get the process
        process = device.attach(4184)  # Direct PID
        print(f"[✓] Attached to MoMo PSB (PID: 4184)")
    except Exception as e:
        print(f"[✗] Failed to attach: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Load the script
    try:
        with open(r"c:\Users\HP\momo\frida_okhttp_interceptor.js", "r") as f:
            script_code = f.read()
    except Exception as e:
        print(f"[✗] Failed to read script: {e}")
        sys.exit(1)
    
    # Create and load the script
    try:
        script = process.create_script(script_code)
        print(f"[✓] Script created")
        
        # Set up message handler
        def on_message(message, data):
            if message["type"] == "send":
                print(message["payload"])
            elif message["type"] == "error":
                print(f"[ERROR] {message['stack']}", file=sys.stderr)
        
        script.on("message", on_message)
        script.load()
        print(f"[✓] Script loaded and running. Capturing HTTP traffic...\n")
        
        # Keep running
        try:
            frida.idle()
        except KeyboardInterrupt:
            print("\n[*] Script terminated by user")
    
    except Exception as e:
        print(f"[✗] Failed to load script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
