from rich.table import Table
from conf.console_theme import *
from conf.configs import Credentials
from SA.status_onu import StatusOnu

class Integra_SA_ERP:

    def __init__(self):
        # Configurations
        custom_theme = Theme({
            "warning": "yellow",
            "disaster": "bold red"
        })
        self.console = Console(theme=custom_theme)

    def status_ca(self,CAs, StatusClientes, Sinais):
        s = None
        sinal = False

        try:
            if len(Sinais) > 0:
                sinal = True
        except Exception:
            pass

        if sinal:
            credenciais = Credentials()
            s = StatusOnu(credenciais.getLogin(), credenciais.getSenha())

        for i in range(len(CAs['Names'])):
            table = Table(title=CAs['Names'][i])

            table.add_column(StatusClientes['Header'][0])
            table.add_column(StatusClientes['Header'][1])
            table.add_column(StatusClientes['Header'][2])
            if sinal:
                table.add_column("Sinal")
            table.add_column(StatusClientes['Header'][3])
            table.add_column(str(StatusClientes['Header'][4]) + ' ' + str(StatusClientes['Header'][5]))
            table.add_column(str(StatusClientes['Header'][6]) + ' ' + str(StatusClientes['Header'][7]))
            table.add_column(str(StatusClientes['Header'][8]) + ' ' + str(StatusClientes['Header'][9]))

            for cs in StatusClientes['Status']:
                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')
                for c in CAs['Clientes'][i]:
                    if c == link[cod_location+11:]:
                        btv_link = '[link=' + link + ']' + link[cod_location+11:] + '[/link]'
                        dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[5].text + '[/link]'

                        if cs[2].text.strip() == 'working':
                            ont_status = cs[2].text.strip()
                        elif cs[2].text.strip() == 'LOS':
                            ont_status = "[disaster]" + cs[2].text.strip() + "[/disaster]"
                        elif cs[2].text.strip() == 'DyingGasp Sem energia':
                            ont_status = "[warning]DyingGasp[/warning]"
                        else:
                            ont_status = "[warning]" + cs[2].text.strip() + "[/warning]"
                        if sinal:
                            sin = s.get_sinal_from_list_with_login(Sinais,cs[5].text)
                            table.add_row(cs[0].text, cs[1].text, ont_status, sin, cs[3].text, btv_link, dalo_link, cs[6].text)
                        else:
                            table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text)
            self.console.print(table)