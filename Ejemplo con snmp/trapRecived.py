#Receptor de trampas SNMP con Python
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging

snmpEngine = engine.SnmpEngine()

TrapAgentAddress='192.168.1.194'; # Ip receptora 
Port=162;  #Puerto de escucha
stat_port = {0:'open',1:'close'} #Diccionario para convertir el valor de la trampa en un valor legible
#Configuración de log
logging.basicConfig(filename='received_traps.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))
logging.info('--------------------------------------------------------------------------')

print("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port))

config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

#Configure community here
config.addV1System(snmpEngine, 'my-area', 'public')

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
        varBinds, cbCtx):
    print("Received new Trap message")
    logging.info("Received new Trap message")
    bandera = 0
    stat = 0
    for name, val in varBinds:   
        if bandera > 5:
            if stat < 2:
                logging.info('%s' % ( val.prettyPrint()))
                print('%s' % ( val.prettyPrint()))
                stat+=1
            else:
                    logging.info (stat_port.get(int(val.prettyPrint())))
                    print('%s'% (stat_port.get(int(val.prettyPrint()))))
        else:
            bandera+=1

    logging.info("==== End of Incoming Trap ====")
ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)  

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise