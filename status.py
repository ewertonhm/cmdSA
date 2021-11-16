from datetime import datetime
from sa import SistemaAtivacao, Integra_SA_ERP
from args import Argumentos
from configs import Credentials, find_path
from btv import Erp
from netbox import NetBox
import asyncio
import threading
import getpass
import busca_olt
import os.path
import sys
import version_control
from circuit_search import BuscaCircuito


def main():
    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()
    CAs = args.getCAs()
    IPs = args.getIPs()
    SNs = args.getSNs()
    OLT = args.getOLT()
    Interfaces = args.getInterfaces()
    Ativacao = args.getAtivacao()
    AllCircuitos = args.getAllCircuitos()
    Codigos = args.getCodigos()
    Sinais = args.getSinais()
    SinaisCaixa = args.getSinaisCaixa()

    credenciais = Credentials()

    s = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())
    #s.verificar_circuitos_id(['JVE-1346A','JVE-1347A','JVE-1347B'])

    # status -c
    if type(Circuitos) == list and Circuitos[0] != 'pppoe':
        s.verificar_circuitos(Circuitos, verf_sinal=False)

    # status -sc
    elif type(Sinais) == list:
        s.verificar_circuitos(Sinais, verf_sinal=True)

    # status -all
    elif type(AllCircuitos) == list and AllCircuitos[0] != 'pppoe':
        c = BuscaCircuito()
        search_term = []
        for circ in AllCircuitos:
            result = c.search_circuit(circ)
            for r in result:
                search_term.append(r)
        print(f'Circuitos encontrados: {search_term}')
        s.verificar_circuitos(search_term)

    # status -c pppoe -p
    elif type(Logins) == list and type(Circuitos) == list and Circuitos[0] == 'pppoe':
        for login in Logins:
            circuito = s.verificar_status_login_get_circuito(login)

            if circuito != False:
                s.verificar_circuitos([circuito])
    # status -p
    elif type(Logins) == list and type(Circuitos) != list:
        s.paralel_verificar_status_login(Logins)

    # status -ca
    elif type(CAs) == list:
        credenciais.check_erp_credentials()
        e = Erp(credenciais.getErpLogin(),credenciais.getErpSenha())
        integra = Integra_SA_ERP()

        for circuito in CAs:
            CAs = e.buscar_cas(circuito)
            StatusClientes = s.raw_verificar_circuito(circuito)
            integra.status_ca(CAs, StatusClientes, False)

    # status -sca
    elif type(SinaisCaixa) == list:
        credenciais.check_erp_credentials()
        e = Erp(credenciais.getErpLogin(),credenciais.getErpSenha())
        integra = Integra_SA_ERP()

        for circuito in SinaisCaixa:
            CAs = e.buscar_cas(circuito)
            StatusClientes = s.raw_verificar_circuito(circuito)
            integra.status_ca(CAs, StatusClientes, True)

    # status -ip
    elif type(IPs) == list:
        n = NetBox(credenciais.getLogin()[:-20],credenciais.getSenha())
        threads = []
        for i in range(len(IPs)):
            threads.append(threading.Thread(target=n.search_ip,args=(IPs[i],)))
            threads[i].start()

        for th in threads:
            if th.is_alive(): th.join()

    # status -sn
    elif type(SNs) == list:
        for sn in SNs:
            s.verificar_status_sn(sn)

    # status -o
    elif type(OLT) == list:
        # -i
        if type(Interfaces) == list:
            for interface in Interfaces:
                s.verificar_status_olt_interface(OLT[0],interface)
        # -id
        elif type(Codigos) == list:
            for codigo in Codigos:
                s.verificar_status_id(OLT[0],codigo)
        else:
            s.verificar_status_olt(OLT[0])

    # status -a
    elif type(Ativacao) == list:
        s.print_onus_disponiveis_ativacao(Ativacao[0])

    # no option set
    else:
        olts_path = find_path() + 'olts.ini'
        if not os.path.isfile(olts_path):
            print('Lista de OLTs (olts.ini) não encontrada, gostaria de criar agora? (pode levar vários minutos)')
            resposta = input('y or n:')
            if resposta == 'y':
                print('Para prosseguir é necessário ter o arquivo chromedriver.exe salvo em seu computador')
                print('O mesmo pode ser baixado em: https://chromedriver.chromium.org/downloads')
                print('O arquivo deve ser salvo no diretório do script')
                busca_olt.start_driver()
                busca_olt.sa_site_login(credenciais.getLogin(), credenciais.getSenha())
                busca_olt.lista_olts()
        else:
            print('Lista de OLTs (olts.ini) já está criada, gostaria de atualizar a lista? (pode levar vários minutos)')
            resposta = input('y or n:')
            if resposta == 'y':
                print('Para prosseguir é necessário ter o arquivo chromedriver.exe salvo em seu computador')
                print('O mesmo pode ser baixado em: https://chromedriver.chromium.org/downloads')
                print('O arquivo deve ser salvo no diretório do script')
                busca_olt.start_driver()
                busca_olt.sa_site_login(credenciais.getLogin(), credenciais.getSenha())
                busca_olt.lista_olts()

    #debbug place:


if __name__ == '__main__':
    # Debug
    #begin_time = datetime.now()

    # Run
    main()
    version_control.get_online_version()

    #stats.print_stats()
    # Debug
    #print("Tempo de execução:", datetime.now() - begin_time)



