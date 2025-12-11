# Despliegue con IceGrid

## Nivel Básico: 2 Nodos

Este proyecto implementa un despliegue básico de Spotifice usando IceGrid con 2 nodos:
- **Node 1**: MediaServer (gestiona biblioteca de música y playlists)
- **Node 2**: MediaRender (controla reproducción de audio)

## Componentes

### Infraestructura IceGrid
- **Registry** (puerto 4061): Coordinador central del sistema
- **Node 1**: Ejecuta MediaServer
- **Node 2**: Ejecuta MediaRender
- **Permissions Verifier** (puerto 10002): Verificador de credenciales simplificado

### Configuración
- `config/registry.config`: Configuración del Registry con LMDB
- `config/node1.config`: Configuración del nodo 1
- `config/node2.config`: Configuración del nodo 2
- `config/application.xml`: Descriptor de la aplicación Spotifice
- `config/admin_verifier.py`: Servidor de verificación de permisos

### Scripts
- `scripts/start-all.sh`: Inicia todo el sistema (verifier, registry, nodes, deploy)
- `scripts/stop_python.py`: Detiene todos los servicios IceGrid
- `scripts/deploy_expect.py`: Despliega la aplicación usando pexpect
- `scripts/redeploy.py`: Remueve y redespliega la aplicación

## Uso

### Iniciar el sistema
```bash
./scripts/start-all.sh
```

Este script:
1. Inicia el verificador de permisos
2. Inicia el IceGrid Registry
3. Inicia los dos nodos (node1 y node2)
4. Despliega la aplicación SpotificeApp
5. Los servidores se inician automáticamente (activation="always")

### Verificar estado
```bash
# Ver logs de los servidores
cat mediaserver1.log
cat mediarender1.log

# Ver procesos
pgrep -fa icegrid
```

### Probar el cliente
```bash
./media_control_grid.py
```

El cliente usa `Ice.Default.Locator` para descubrir los servicios a través del Registry.

### Detener el sistema
```bash
./scripts/stop_python.py
```

## Arquitectura

```
                    ┌──────────────┐
                    │   Registry   │
                    │  (port 4061) │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────┐              ┌────▼────┐
         │  Node 1 │              │  Node 2 │
         └────┬────┘              └────┬────┘
              │                        │
     ┌────────▼────────┐      ┌───────▼────────┐
     │  MediaServer-1  │      │ MediaRender-1  │
     │                 │      │                │
     │ - MusicLibrary  │      │ - AudioPlayer  │
     │ - StreamManager │      │ - GstPlayer    │
     │ - Playlists     │      │                │
     └─────────────────┘      └────────────────┘
              ▲                        │
              │      ┌─────────────────┘
              │      │
         ┌────┴──────▼────┐
         │ media_control  │
         │  (cliente con  │
         │    Locator)    │
         └────────────────┘
```

## Características Implementadas

✓ Despliegue en 2 nodos IceGrid  
✓ Registro automático de adaptadores  
✓ Descubrimiento de servicios vía Locator  
✓ Verificación de permisos simplificada  
✓ Activación automática de servidores (activation="always")  
✓ Scripts automatizados de gestión  
✓ Cliente adaptado para usar IceGrid  

## Credenciales

El sistema usa un verificador de permisos simplificado que acepta cualquier credencial:
- **Usuario**: admin (o cualquier otro)
- **Contraseña**: admin (o cualquier otra)

## Troubleshooting

### Los servidores no inician
- Verificar que el directorio `media/` existe: `make media`
- Revisar logs: `cat mediaserver1.log` y `cat mediarender1.log`

### Error de conexión
- Verificar que el Registry está corriendo: `pgrep icegridregistry`
- Verificar que los nodos están corriendo: `pgrep icegridnode`

### Redesplegar aplicación
```bash
./scripts/redeploy.py
```

### Limpiar todo y reiniciar
```bash
./scripts/stop_python.py
rm -rf registry_data/ node*_data/ *.log
./scripts/start-all.sh
```
