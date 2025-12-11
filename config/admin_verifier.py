#!/usr/bin/env python3
"""
Verificador de permisos simple para IceGrid.
Permite acceso sin contraseña para desarrollo.
"""

import sys
import Ice

Ice.loadSlice('-I{} --all {}/Glacier2/PermissionsVerifier.ice'.format(
    Ice.getSliceDir(), Ice.getSliceDir()))
import Glacier2


class PermissionsVerifierI(Glacier2.PermissionsVerifier):
    def checkPermissions(self, userId, password, reason, current=None):
        # Permitir cualquier acceso sin verificar contraseña
        # Si userId está vacío, usar "admin" como default
        if not userId or userId.strip() == "":
            userId = "admin"
        print(f"✓ Verificación de permisos: userId='{userId}' (acceso permitido)")
        return True, ""


def main():
    props = Ice.createProperties()
    props.setProperty("PermissionsVerifierAdapter.Endpoints", "tcp -p 10002")
    
    init_data = Ice.InitializationData()
    init_data.properties = props
    
    with Ice.initialize(init_data) as communicator:
        adapter = communicator.createObjectAdapter("PermissionsVerifierAdapter")
        adapter.add(PermissionsVerifierI(), 
                    communicator.stringToIdentity("AdminPermissionsVerifier"))
        adapter.activate()
        print("✓ Verificador de permisos iniciado en puerto 10002")
        communicator.waitForShutdown()


if __name__ == "__main__":
    main()
