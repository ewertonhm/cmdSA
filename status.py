from datetime import datetime
from sa import SistemaAtivacao, Integra_SA_ERP
from args import Argumentos
from configs import Credentials
from btv import Erp
from netbox import NetBox
import asyncio


def main():

    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()
    CAs = args.getCAs()
    IPs = args.getIPs()

    credenciais = Credentials()

    s = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())


    if type(Circuitos) == list and Circuitos[0] != 'pppoe':
        s.paralel_verificar_circuito(Circuitos)

    elif type(Logins) == list and type(Circuitos) == list and Circuitos[0] == 'pppoe':
        for login in Logins:
            circuito = s.verificar_status_login_get_circuito(login)

            if circuito != False:
                s.verificar_circuito(circuito)

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
        for ip in IPs:
            n.search_ip(ip)


if __name__ == '__main__':
    # Debug
    begin_time = datetime.now()

    # Run
    main()

    #stats.print_stats()
    # Debug
    print(datetime.now() - begin_time)



