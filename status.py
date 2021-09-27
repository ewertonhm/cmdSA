from datetime import datetime
from sa import SistemaAtivacao, Integra_SA_ERP
from args import Argumentos
from configs import Credentials
from btv import Erp
from netbox import NetBox
import asyncio
import threading
import getpass
import busca_olt
import os.path


def main():

    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()
    CAs = args.getCAs()
    IPs = args.getIPs()
    SNs = args.getSNs()
    OLT = args.getOLT()
    Interfaces = args.getInterfaces()

    credenciais = Credentials()

    s = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())
    #s.verificar_circuitos_id(['JVE-1346A','JVE-1347A','JVE-1347B'])


    if type(Circuitos) == list and Circuitos[0] != 'pppoe':
        s.verificar_circuitos(Circuitos)
        #s.paralel_verificar_circuito(Circuitos)
        '''
        threads = []
        for i in range(len(Circuitos)):
            sa = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())
            threads.append(threading.Thread(target=sa.verificar_circuito,args=(Circuitos[i],)))
            threads[i].start()

        for th in threads:
            if th.is_alive(): th.join()
        '''

    elif type(Logins) == list and type(Circuitos) == list and Circuitos[0] == 'pppoe':
        for login in Logins:
            circuito = s.verificar_status_login_get_circuito(login)

            if circuito != False:
                s.verificar_circuitos([circuito])

    elif type(Logins) == list and type(Circuitos) != list:
        s.paralel_verificar_status_login(Logins)

    elif type(CAs) == list:
        credenciais.check_erp_credentials()
        e = Erp(credenciais.getErpLogin(),credenciais.getErpSenha())
        integra = Integra_SA_ERP()

        for circuito in CAs:
            CAs = e.buscar_cas(circuito)
            StatusClientes = s.raw_verificar_circuito(circuito)
            integra.status_ca(CAs, StatusClientes)

    elif type(IPs) == list:
        n = NetBox(credenciais.getLogin()[:-20],credenciais.getSenha())
        threads = []
        for i in range(len(IPs)):
            threads.append(threading.Thread(target=n.search_ip,args=(IPs[i],)))
            threads[i].start()

        for th in threads:
            if th.is_alive(): th.join()

    elif type(SNs) == list:
        for sn in SNs:
            s.verificar_status_sn(sn)
    elif type(OLT) == list:
        if type(Interfaces) == list:
            for interface in Interfaces:
                s.verificar_status_olt_interface(OLT[0],interface)
        else:
            s.verificar_status_olt(OLT[0])

    else:
        if not os.path.isfile('olts.ini'):
            print('Lista de OLTs (olts.ini) não encontrada, gostaria de criar agora? (pode levar vários minutos)')
            resposta = input('y or n:')
            if resposta == 'y':
                busca_olt.lista_olts(credenciais.getLogin(), credenciais.getSenha())
            else:
                quit()
        else:
            print('Lista de OLTs (olts.ini) já está criada, gostaria de atualizar a lista? (pode levar vários minutos)')
            resposta = input('y or n:')
            if resposta == 'y':
                busca_olt.lista_olts(credenciais.getLogin(), credenciais.getSenha())
            else:
                quit()


if __name__ == '__main__':
    # Debug
    #begin_time = datetime.now()

    # Run
    main()

    #stats.print_stats()
    # Debug
    #print("Tempo de execução:", datetime.now() - begin_time)



