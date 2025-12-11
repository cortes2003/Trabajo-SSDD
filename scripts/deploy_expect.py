#!/usr/bin/env python3
"""
Script para desplegar la aplicación usando pexpect con icegridadmin.
"""

import sys
import pexpect

def main():
    try:
        # Iniciar icegridadmin
        cmd = 'icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061"'
        child = pexpect.spawn(cmd, encoding='utf-8', timeout=10)
        child.logfile = sys.stdout
        
        # Esperar el prompt de user id
        child.expect('user id:')
        child.sendline('admin')
        
        # Esperar el prompt de password
        child.expect('password:')
        child.sendline('admin')
        
        # Esperar el prompt de icegridadmin
        child.expect('>>>')
        
        # Desplegar la aplicación
        print("\nDesplegando aplicación...")
        child.sendline("application add 'config/application.xml'")
        child.expect('>>>')
        
        print("✓ Aplicación desplegada exitosamente")
        
        # Los servidores con activation="always" se inician automáticamente
        print("\n✓ Servidores configurados con activation='always'")
        print("  Se iniciarán automáticamente...")
        
        # Esperar un momento para que los servidores se inicien
        import time
        time.sleep(3)
        
        # Salir
        child.sendline("exit")
        child.wait()
        
        print("\n✓ Despliegue completado")
        print("\nServidores desplegados:")
        print("  - Node 1: IcePatch2/server, MediaServer-1, MediaServer-2")
        print("  - Node 2: MediaRender-1, MediaRender-2")
        return 0
        
    except pexpect.TIMEOUT:
        print("\n✗ Timeout esperando respuesta de icegridadmin")
        return 1
    except pexpect.EOF:
        print("\n✗ icegridadmin terminó inesperadamente")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
