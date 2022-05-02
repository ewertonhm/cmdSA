from SA import busca_olt
from SA.status_circuito import StatusCircuito
from SA.status_onu import StatusOnu
from SA.integra_erp_sa import Integra_SA_ERP
from SA.circuit_search import BuscaCircuito
from SA.status_olt import StatusOlt
from args import Argumentos
from conf import version_control
from conf.configs import Credentials, find_path
from Bemtevi.erp import Erp
import os.path

# from datetime import datetime

# from pprint import pprint


def main():
    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()
    CAs = args.getCAs()
    # IPs = args.getIPs()
    SNs = args.getSNs()
    OLT = args.getOLT()
    Interfaces = args.getInterfaces()
    Ativacao = args.getAtivacao()
    AllCircuitos = args.getAllCircuitos()
    Codigos = args.getCodigos()
    Sinais = args.getSinais()
    SinaisCaixa = args.getSinaisCaixa()

    credenciais = Credentials()


    # status -c
    if type(Circuitos) == list and Circuitos[0] != 'pppoe':
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        s.verificar_circuitos(Circuitos, verf_sinal=False)

    # status -sc
    elif type(Sinais) == list:
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        s.verificar_circuitos(Sinais, verf_sinal=True)

    # status -all
    elif type(AllCircuitos) == list and AllCircuitos[0] != 'pppoe':
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        c = BuscaCircuito()
        search_term = []
        for circ in AllCircuitos:
            result = c.search_circuit(circ.upper())
            for r in result:
                search_term.append(r['circuito'])
        print(f'Circuitos encontrados: {search_term}')
        s.verificar_circuitos(search_term, verf_sinal=False)

    # status -c pppoe -p
    elif type(Logins) == list and type(Circuitos) == list and Circuitos[0] == 'pppoe':
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        for login in Logins:
            circuito = s.verificar_status_login_get_circuito(login)

            if circuito != False:
                s.verificar_circuitos([circuito], verf_sinal=False)
    # status -p
    elif type(Logins) == list and type(Circuitos) != list:
        s = StatusOnu(credenciais.getLogin(), credenciais.getSenha())
        s.paralel_get_status_login(Logins)

    # status -ca
    elif type(CAs) == list:
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        credenciais.check_erp_credentials()
        e = Erp(credenciais.getErpLogin(),credenciais.getErpSenha())
        integra = Integra_SA_ERP()

        for circuito in CAs:
            CAs = e.buscar_cas(circuito)
            StatusClientes = s.raw_verificar_circuito(circuito)
            integra.status_ca(CAs, StatusClientes, False)

    # status -sca
    elif type(SinaisCaixa) == list:
        s = StatusCircuito(credenciais.getLogin(), credenciais.getSenha())
        o = StatusOnu(credenciais.getLogin(), credenciais.getSenha())
        credenciais.check_erp_credentials()
        e = Erp(credenciais.getErpLogin(),credenciais.getErpSenha())
        integra = Integra_SA_ERP()

        for circuito in SinaisCaixa:
            CAs = e.buscar_cas(circuito)
            StatusClientes = s.raw_verificar_circuito(circuito)
            Sinais = o.paralel_get_status_sn(StatusClientes['Seriais'])
            integra.status_ca(CAs, StatusClientes, Sinais)

    # status -ip
    # elif type(IPs) == list:
    #    n = NetBox(credenciais.getLogin()[:-20],credenciais.getSenha())
    #    threads = []
    #    for i in range(len(IPs)):
    #        threads.append(threading.Thread(target=n.search_ip,args=(IPs[i],)))
    #        threads[i].start()
    #
    #    for th in threads:
    #        if th.is_alive(): th.join()

    # status -sn
    elif type(SNs) == list:
        s = StatusOnu(credenciais.getLogin(), credenciais.getSenha())
        for sn in SNs:
            s.get_status_sn(sn)

    # status -o
    elif type(OLT) == list:
        s = StatusOlt(credenciais.getLogin(), credenciais.getSenha())
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
        s = StatusOlt(credenciais.getLogin(), credenciais.getSenha())
        s.print_onus_disponiveis_ativacao(Ativacao[0])

    # no option set
    '''
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
    '''
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
