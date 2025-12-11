#!/usr/bin/env python3
"""
Cliente MediaControl adaptado para IceGrid con múltiples servidores.
Soporta 2 MediaServers y 2 MediaRenders con balanceo simple.
"""

import sys
from time import sleep
import random

import Ice

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402


def get_proxy_via_locator(ic, identity, interface_class, optional=False):
    """
    Obtiene un proxy a través del IceGrid Locator.
    
    Args:
        ic: Ice communicator
        identity: Identity del objeto (ej: "mediaServer1")
        interface_class: Clase del proxy (ej: Spotifice.MediaServerPrx)
        optional: Si True, no falla si no encuentra el servicio
    """
    try:
        # Crear proxy indirecto usando la identidad
        base_proxy = ic.stringToProxy(identity)
        
        # Intentar conectar con reintentos
        for attempt in range(3):
            try:
                base_proxy.ice_ping()
                break
            except (Ice.ConnectionRefusedException, Ice.NoEndpointException):
                if attempt < 2:
                    sleep(0.5)
                else:
                    if optional:
                        return None
                    raise RuntimeError(f'No se pudo conectar a {identity}')
        
        # Cast al tipo correcto
        proxy = interface_class.checkedCast(base_proxy)
        if proxy is None:
            if optional:
                return None
            raise RuntimeError(f'Invalid proxy for {identity}')
        
        return proxy
    except Exception as e:
        if optional:
            return None
        raise


def discover_servers(ic):
    """Descubre todos los MediaServers disponibles."""
    servers = []
    for i in range(1, 5):  # Intentar hasta 4 servidores
        proxy = get_proxy_via_locator(
            ic, f'mediaServer{i}', Spotifice.MediaServerPrx, optional=True)
        if proxy:
            servers.append((i, proxy))
    return servers


def discover_renders(ic):
    """Descubre todos los MediaRenders disponibles."""
    renders = []
    for i in range(1, 5):  # Intentar hasta 4 renders
        proxy = get_proxy_via_locator(
            ic, f'mediaRender{i}', Spotifice.MediaRenderPrx, optional=True)
        if proxy:
            renders.append((i, proxy))
    return renders


def main(ic):
    print("=" * 60)
    print("  Cliente Spotifice con IceGrid - Nivel Intermedio")
    print("  Descubrimiento automático de múltiples servidores")
    print("=" * 60)
    print()
    
    # Descubrir todos los servidores disponibles
    print("🔍 Descubriendo MediaServers...")
    servers = discover_servers(ic)
    if not servers:
        print("✗ No se encontraron MediaServers")
        return
    
    print(f"✓ Encontrados {len(servers)} MediaServer(s):")
    for idx, _ in servers:
        print(f"  - mediaServer{idx}")
    print()
    
    print("🔍 Descubriendo MediaRenders...")
    renders = discover_renders(ic)
    if not renders:
        print("✗ No se encontraron MediaRenders")
        return
    
    print(f"✓ Encontrados {len(renders)} MediaRender(s):")
    for idx, _ in renders:
        print(f"  - mediaRender{idx}")
    print()

    # Usar el primer servidor para obtener la lista de pistas
    server_idx, server = servers[0]
    print(f"📀 Usando mediaServer{server_idx} para obtener biblioteca...")
    
    tracks = server.get_all_tracks()
    print(f"✓ Pistas disponibles: {len(tracks)}")
    for i, t in enumerate(tracks[:5], 1):
        print(f"  {i}. {t.title}")
    
    if len(tracks) > 5:
        print(f"  ... y {len(tracks) - 5} más")
    print()

    if not tracks:
        print("No hay pistas disponibles.")
        return

    # Demostración con balanceo: usar diferentes renders
    print("=" * 60)
    print("  Demostración de balanceo entre múltiples renders")
    print("=" * 60)
    print()
    
    for demo_num in range(min(2, len(renders))):
        render_idx, render = renders[demo_num]
        server_idx, server = random.choice(servers)
        
        print(f"▶ Demo {demo_num + 1}: usando mediaRender{render_idx} + mediaServer{server_idx}")
        
        # Enlazar render con server
        render.bind_media_server(server)
        print(f"  ✓ Render enlazado")
        
        # Cargar una pista aleatoria
        track = random.choice(tracks[:10])
        render.load_track(track.id)
        print(f"  ✓ Cargada: {track.title}")
        
        # Reproducir brevemente
        render.play()
        print(f"  ♪ Reproduciendo en render{render_idx}...")
        sleep(3)
        
        render.stop()
        print(f"  ⏹ Detenido\n")
        sleep(1)
    
    print("=" * 60)
    print("  Demostración de playlists")
    print("=" * 60)
    print()
    
    # Usar el primer server y render para playlists
    server_idx, server = servers[0]
    render_idx, render = renders[0]
    
    print(f"📝 Obteniendo playlists desde mediaServer{server_idx}...")
    playlists = server.get_all_playlists()
    
    if playlists:
        print(f"✓ Playlists disponibles: {len(playlists)}")
        for i, pl in enumerate(playlists[:3], 1):
            print(f"  {i}. {pl.name} ({len(pl.track_ids)} canciones)")
        print()
        
        # Cargar primera playlist
        playlist = playlists[0]
        print(f"🎵 Cargando playlist: {playlist.name}")
        render.bind_media_server(server)
        render.load_playlist(playlist.id)
        print(f"  ✓ Playlist cargada")
        
        render.play()
        print(f"  ♪ Reproduciendo playlist...")
        sleep(5)
        
        render.stop()
        print(f"  ⏹ Detenido")
    else:
        print("No hay playlists disponibles.")
    
    print()
    print("=" * 60)
    print("  ✓ Demostración completada")
    print(f"  Total: {len(servers)} MediaServer(s), {len(renders)} MediaRender(s)")
    print("=" * 60)


if __name__ == "__main__":
    props = Ice.createProperties(sys.argv)
    props.setProperty('Ice.Default.Locator', 
                      'SpotificeGrid/Locator:tcp -h localhost -p 4061')
    
    init_data = Ice.InitializationData()
    init_data.properties = props
    
    with Ice.initialize(init_data) as ic:
        try:
            main(ic)
        except KeyboardInterrupt:
            print("\n\n⏸ Interrumpido por el usuario")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
