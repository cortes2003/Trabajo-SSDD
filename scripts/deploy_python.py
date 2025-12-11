#!/usr/bin/env python3
"""
Script para desplegar la aplicación Spotifice en IceGrid sin usar icegridadmin.
"""

import sys
import Ice

# Cargar todos los slices necesarios de IceGrid
slice_dir = Ice.getSliceDir()
Ice.loadSlice('-I{} --all {}/IceGrid/Registry.ice'.format(slice_dir, slice_dir))
import IceGrid


def main():
    props = Ice.createProperties()
    props.setProperty('Ice.Default.Locator', 'SpotificeGrid/Locator:tcp -h localhost -p 4061')
    
    init_data = Ice.InitializationData()
    init_data.properties = props
    
    with Ice.initialize(init_data) as communicator:
        # Conectar al Registry
        try:
            registry_proxy = communicator.stringToProxy('SpotificeGrid/Registry')
            registry = IceGrid.RegistryPrx.checkedCast(registry_proxy)
            
            if not registry:
                print("✗ No se pudo conectar al Registry")
                return 1
            
            print("✓ Conectado al Registry")
        except Exception as e:
            print(f"✗ Error conectando al Registry: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        # Crear sesión de administración con credenciales "admin"
        try:
            session = registry.createAdminSession("admin", "admin")
            admin = session.getAdmin()
            print("✓ Sesión de administración creada exitosamente")
        except Exception as e:
            print(f"✗ Error creando sesión: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        try:
            # Leer el archivo XML de la aplicación
            with open('config/application.xml', 'r') as f:
                xml_content = f.read()
            
            # Parsear el XML a ApplicationDescriptor usando el FileParser
            descriptor = IceGrid.parseDescriptor(xml_content, Ice.getCurrentProperties())
            
            # Desplegar la aplicación
            admin.addApplication(descriptor)
            print("✓ Aplicación 'SpotificeApp' desplegada exitosamente")
            
            # Iniciar los servidores
            print("\nIniciando servidores...")
            
            try:
                admin.startServer("MediaServer-1")
                print("✓ MediaServer-1 iniciado")
            except Exception as e:
                print(f"  MediaServer-1: {e}")
            
            try:
                admin.startServer("MediaRender-1")
                print("✓ MediaRender-1 iniciado")
            except Exception as e:
                print(f"  MediaRender-1: {e}")
            
            print("\n✓ Despliegue completado")
            return 0
            
        except IceGrid.DeploymentException as e:
            if "already exists" in str(e):
                print("✗ La aplicación 'SpotificeApp' ya existe")
                print("  Elimínala primero para volver a desplegar")
                return 1
            else:
                raise
        except Exception as e:
            print(f"✗ Error desplegando aplicación: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            try:
                session.destroy()
            except:
                pass


if __name__ == "__main__":
    sys.exit(main())
