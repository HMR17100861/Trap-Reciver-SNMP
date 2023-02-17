from pysnmp.hlapi import *

target = '192.168.1.63' # Dirección IP del dispositivo dataProbe iPIO-8
oid = '.1.3.6.1.4.1.1418.5.6' # OID que deseas mostrar la tabla, oid se muestran todos los valores de la tabla desde valores que se asignan por defecto hasta los asignados por el administrador]
stat_port = {0:'open',1:'close'}
table_port = []
table_update = []

def print_table(oid):
    bandera = 0
    
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData('public'),
                                                                        UdpTransportTarget((target, 161)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(oid)),
                                                                        lexicographicMode=False):
        bandera+= 1
        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                
                if bandera < 17:
                    
                    print('%s' % (varBind[1].prettyPrint()))
                    table_port.append(varBind[1].prettyPrint())
                    
                elif bandera > 80:
                    print('%s' % (stat_port.get(int(varBind[1].prettyPrint()), varBind[1].prettyPrint())))
                    table_port.append(stat_port.get(int(varBind[1].prettyPrint()), varBind[1].prettyPrint()))
                

print_table(oid)
