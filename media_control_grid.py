#!/usr/bin/env python3
"""
Cliente MediaControl adaptado para IceGrid.
Se conecta a los servicios a través del IceGrid Locator.
"""

import sys
from time import sleep

import Ice

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402


def get_proxy_via_locator(ic, identity, interface_class):
    """
    Obtiene un proxy a través del IceGrid Locator.
    
    Args:
        ic: Ice communicator
        identity: Identity del objeto (ej: "mediaServer1")
        interface_class: Clase del proxy (ej: Spotifice.MediaServerPrx)
    """
    # Crear proxy indirecto usando la identidad
    base_proxy = ic.stringToProxy(identity)
    
    # Intentar conectar con reintentos
    for attempt in range(5):
        try:
            base_proxy.ice_ping()
            break
        except Ice.ConnectionRefusedException:
            if attempt < 4:
                print(f"Esperando conexión (intento {attempt + 1}/5)...")
                sleep(1)
            else:
                raise RuntimeError(f'No se pudo conectar a {identity}')
    
    # Cast al tipo correcto
    proxy = interface_class.checkedCast(base_proxy)
    if proxy is None:
        raise RuntimeError(f'Invalid proxy for {identity}')
    
    return proxy


def main(ic):
    print("=== Cliente Spotifice con IceGrid ===\n")
    
    # Obtener proxies a través de IceGrid
    print("Conectando a MediaServer...")
    server = get_proxy_via_locator(ic, 'mediaServer1', Spotifice.MediaServerPrx)
    print("✓ Conectado a MediaServer\n")
    
    print("Conectando a MediaRender...")
    render = get_proxy_via_locator(ic, 'mediaRender1', Spotifice.MediaRenderPrx)
    print("✓ Conectado a MediaRender\n")

    # Resto del código igual que media_control.py
    print("Obteniendo lista de pistas...")
    tracks = server.get_all_tracks()
    print(f"Pistas disponibles: {len(tracks)}")
    for i, t in enumerate(tracks[:5], 1):  # Mostrar solo las primeras 5
        print(f"  {i}. {t.title}")
    
    if len(tracks) > 5:
        print(f"  ... y {len(tracks) - 5} más")
    print()

    if not tracks:
        print("No hay pistas disponibles.")
        return

    print(f"Obteniendo información de la pista: {tracks[0].id}")
    track_info = server.get_track_info(tracks[0].id)
    print(f"  Título: {track_info.title}")
    print(f"  Archivo: {track_info.filename}\n")

    print("Enlazando MediaRender con MediaServer...")
    render.bind_media_server(server)
    render.stop()
    print("✓ MediaRender enlazado\n")

    print(f"Cargando pista: {tracks[0].title}")
    render.load_track(tracks[0].id)
    print("✓ Pista cargada\n")
    
    print("Reproduciendo...")
    render.play()
    print("♪ Reproduciendo durante 5 segundos...\n")
    sleep(5)

    print("Deteniendo reproducción...")
    render.stop()
    print("✓ Reproducción detenida\n")

    if len(tracks) > 1:
        print(f"Cargando segunda pista: {tracks[1].title}")
        render.load_track(tracks[1].id)
        print("Reproduciendo segunda pista...")
        render.play()
        print("♪ Segunda pista sonando...\n")
        print("(Presiona Ctrl+C para detener)")
        
        try:
            # Mantener el cliente corriendo
            ic.waitForShutdown()
        except KeyboardInterrupt:
            print("\n\nDeteniendo...")
            render.stop()


if __name__ == '__main__':
    # Configuración del cliente con IceGrid Locator
    props = Ice.createProperties()
    props.setProperty('Ice.Default.Locator', 
                      'SpotificeGrid/Locator:tcp -h localhost -p 4061')
    
    init_data = Ice.InitializationData()
    init_data.properties = props
    
    with Ice.initialize(init_data) as communicator:
        try:
            main(communicator)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
