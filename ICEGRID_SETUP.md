# Guía de Despliegue IceGrid - Nivel Básico

## Estructura Creada

```
config/
├── registry.config      # Configuración del IceGrid Registry
├── node1.config        # Configuración del Nodo 1 (MediaServer)
├── node2.config        # Configuración del Nodo 2 (MediaRender)
└── application.xml     # Descriptor de la aplicación Spotifice

scripts/
├── start-all.sh        # Script maestro para iniciar todo
├── start-registry.sh   # Inicia solo el Registry
├── start-node1.sh      # Inicia solo el Nodo 1
├── start-node2.sh      # Inicia solo el Nodo 2
├── deploy-app.sh       # Despliega la aplicación
└── stop-all.sh         # Detiene toda la infraestructura

media_control_grid.py   # Cliente adaptado para IceGrid
```

## Inicio Rápido

### 1. Iniciar toda la infraestructura
```bash
./scripts/start-all.sh
```

Esto iniciará:
- ✓ IceGrid Registry (puerto 4061)
- ✓ Nodo 1 con MediaServer
- ✓ Nodo 2 con MediaRender
- ✓ Desplegará la aplicación SpotificeApp

### 2. Ejecutar el cliente
```bash
./media_control_grid.py
```

### 3. Detener todo
```bash
./scripts/stop-all.sh
```

## Inicio Manual (paso a paso)

### Terminal 1 - Registry
```bash
./scripts/start-registry.sh
```

### Terminal 2 - Node 1
```bash
./scripts/start-node1.sh
```

### Terminal 3 - Node 2
```bash
./scripts/start-node2.sh
```

### Terminal 4 - Desplegar aplicación
```bash
./scripts/deploy-app.sh
```

### Terminal 5 - Cliente
```bash
./media_control_grid.py
```

## Comandos de Administración IceGrid

### Ver estado de la aplicación
```bash
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "application describe SpotificeApp"
```

### Ver servidores activos
```bash
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "server list"
```

### Ver estado de nodos
```bash
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "node list"
```

### Iniciar/Detener servidor específico
```bash
# Iniciar
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "server start MediaServer-1"

# Detener
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "server stop MediaServer-1"
```

### Sesión interactiva de administración
```bash
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061'
```

Comandos útiles dentro de la sesión:
```
> application list
> server list
> node list
> application describe SpotificeApp
> server state MediaServer-1
> help
> quit
```

## Monitoreo de Logs

### Ver logs de MediaServer
```bash
tail -f node1_output/MediaServer-1/mediaserver1.log
```

### Ver logs de MediaRender
```bash
tail -f node2_output/MediaRender-1/mediarender1.log
```

### Ver todos los logs
```bash
tail -f node*_output/*/*.log
```

## Arquitectura del Despliegue

```
┌─────────────────────────────────────────┐
│      IceGrid Registry (puerto 4061)     │
│    Coordinador Central - Gestiona:      │
│    - Ubicación de servicios             │
│    - Estado de nodos                    │
│    - Activación de servidores           │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
   ┌───▼────┐      ┌────▼───┐
   │ Node 1 │      │ Node 2 │
   │        │      │        │
   │ Media  │      │ Media  │
   │ Server │◄─────┤ Render │
   └────────┘      └────────┘
       │                │
       └────────┬───────┘
                │
         ┌──────▼──────┐
         │   Cliente   │
         │ media_con-  │
         │ trol_grid   │
         └─────────────┘
```

## Diferencias con Despliegue Directo

### Antes (sin IceGrid):
- Inicio manual de cada servicio
- Puertos fijos en archivos .config
- Cliente se conecta directamente a puertos TCP
- Sin gestión de fallos
- Sin balanceo de carga

### Ahora (con IceGrid):
- IceGrid gestiona el ciclo de vida de servicios
- Activación bajo demanda (on-demand)
- Cliente usa Locator para encontrar servicios
- Reinicio automático en caso de fallos
- Base para escalado futuro

## Troubleshooting

### Error: "registry shutdown SpotificeGrid failed"
El Registry ya está detenido, ignorar este error al ejecutar `stop-all.sh`.

### Error: "application add ... failed"
La aplicación ya está desplegada. Eliminarla primero:
```bash
icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
  -e "application remove SpotificeApp"
```

### No se puede conectar el cliente
1. Verificar que Registry está corriendo: `pgrep -f icegridregistry`
2. Verificar que los nodos están corriendo: `pgrep -f icegridnode`
3. Verificar que la aplicación está desplegada:
   ```bash
   icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' \
     -e "application list"
   ```

### Limpiar todo y empezar de nuevo
```bash
./scripts/stop-all.sh
rm -rf registry_data/ node1_data/ node2_data/ node1_output/ node2_output/
./scripts/start-all.sh
```

## Próximos Pasos (Nivel Intermedio)

Para el nivel intermedio se necesitará:
- [ ] 2 MediaServers (replicación)
- [ ] 2 MediaRenders (múltiples clientes)
- [ ] IcePatch2 para distribución de código
- [ ] Balanceo de carga
- [ ] Configuración de replicas
