#!/usr/bin/env python3
"""
Script para detener servicios IceGrid sin usar icegridadmin.
"""

import subprocess
import signal
import time

def stop_process(name):
    """Detiene un proceso por nombre usando pkill."""
    try:
        result = subprocess.run(['pkill', '-f', name], capture_output=True)
        if result.returncode == 0:
            print(f"✓ {name} detenido")
            return True
        else:
            print(f"  {name} no estaba ejecutándose")
            return False
    except Exception as e:
        print(f"✗ Error deteniendo {name}: {e}")
        return False

def main():
    print("=== Deteniendo IceGrid ===")
    
    # Detener nodos (esto detendrá automáticamente los servidores)
    print("\nDeteniendo nodos...")
    stop_process('icegridnode.*node1')
    stop_process('icegridnode.*node2')
    time.sleep(2)
    
    # Detener registry
    print("\nDeteniendo registry...")
    stop_process('icegridregistry')
    time.sleep(1)
    
    # Detener verificador
    print("\nDeteniendo verificador de permisos...")
    stop_process('admin_verifier.py')
    
    print("\n✓ Todos los servicios detenidos")

if __name__ == "__main__":
    main()
