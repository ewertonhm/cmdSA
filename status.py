from datetime import datetime
from rich import print
from rich.console import Console
from rich.theme import Theme
from sa import SistemaAtivacao
from args import Argumentos
from configs import Credentials
from rich.table import Table

def main():
    args = Argumentos()
    Circuitos = args.getCircuitos()
    Logins = args.getLogins()

    credenciais = Credentials()
    s = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())

    if type(Logins) == list:
        for login in Logins:
            ## create table
            table = Table()

            data = s.verificar_pppoe_data(login)

            if data != False:
                data = data.split('|')
                table.add_column(login)
                table.add_row(s.verificar_onu(data[0]))
            else:
                table.add_column(login)
                table.add_row('Login não encontrado')
            console.print(table)
            print()

            if type(Circuitos) == list and Circuitos[0] == 'pppoe':
                console.print(s.verificar_circuito(data[1]))
                print()

    if type(Circuitos) == list:
        # para cada circuito na lista Circuitos,
        # pega as informações do
        for circuito in Circuitos:
            if circuito != 'pppoe':
                console.print(s.verificar_circuito(circuito))
                print()


if __name__ == '__main__':
    # Debug
    #begin_time = datetime.now()

    # Configurations
    custom_theme = Theme({
        "warning": "yellow",
        "disaster": "bold red"
    })
    console = Console(theme=custom_theme)

    # Run
    main()

    # Debug
    #print(datetime.now() - begin_time)



