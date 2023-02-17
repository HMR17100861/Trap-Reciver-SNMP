import logging
import mysql.connector

# Receptor de trampas SNMP con Python
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv

snmpEngine = engine.SnmpEngine()

TrapAgentAddress='192.168.1.194'  # Dirección IP receptora
Port=162  # Puerto de escucha
stat_port = {0:'open',1:'close'} # Diccionario para convertir el valor de la trampa en un valor legible

# Configuración de log
logging.basicConfig(filename='received_traps.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))
logging.info('--------------------------------------------------------------------------')

print("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))

config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

# Configure community here
config.addV1System(snmpEngine, 'my-area', 'public')

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost",
    database="puertas_eventos_test",
    user="HumbertoAdmin",
    password="Admin1102Pa$$w0rd",
    auth_plugin="mysql_native_password"  # Agregado para manejar el error "Authentication plugin 'caching_sha2_password' is not supported"
)
print(conn)
cursor = conn.cursor()

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
        varBinds, cbCtx):
    print("Received new Trap message")
    logging.info("Received new Trap message")
    bandera = 0
    stat = 0
    nombrep=0
    puerto = ""
    nombre_p=""
    estado=""
    for name, val in varBinds:   
        if bandera > 5:
            if stat < 2:
                if nombrep == 0:
                    puerto= ('%s' % ( val.prettyPrint()))
                    print(puerto)
                    stat+=1
                    nombrep+=1
                else:
                        nombre_p=('%s' % ( val.prettyPrint()))
                        print(nombre_p)
                        stat+=1
            else:
                estado=('%s'% (stat_port.get(int(val.prettyPrint()))))
                print(estado)
                
        else:
            bandera+=16
    if puerto and nombre_p and estado:
        cursor.execute("""  INSERT INTO puerta_eventos (Puerto, Numero_De_Puerta, Estado,Fecha,created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW(), NOW())
                    """, (puerto, nombre_p, estado))
        conn.commit()


    logging.info("==== End of Incoming Trap ====")
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)  

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
