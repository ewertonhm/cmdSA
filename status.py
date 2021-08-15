from datetime import datetime
from sa import SistemaAtivacao
from args import Argumentos
from configs import Credentials


def main():
    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()

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



if __name__ == '__main__':
    # Debug
    #begin_time = datetime.now()

    # Run
    main()

    # Debug
    #print(datetime.now() - begin_time)



