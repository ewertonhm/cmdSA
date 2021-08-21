from bs4 import BeautifulSoup
import httpx
import asyncio
from rich.table import Table
import concurrent.futures
from console_theme import *


class SistemaAtivacao:
    start_url = 'http://ativacaofibra.redeunifique.com.br/auth.php'
    home = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php'
    verificar_status = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status'
    outras_verificacoes = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados'
    MAX_THREADS = 10


    def __init__(self, login, senha):
        self.login = login
        self.senha = senha
        self.acao = 'Entrar'

        self.session = httpx.Client()
        self.do_login()

        ## para verificar se o login deu certo futuramente, deve retornar uma "Responsa [200]" se tiver logado:
        # print(self.session.get('http://ativacaofibra.redeunifique.com.br/auth.php'))

        self.console = CONSOLE

    def do_login(self):
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        self.session.post(self.start_url, data=auth)

    def verificar_circuito(self, circuito):
        ## get circ_id
        post = {"circ": circuito, "pesquisar":"Pesquisar Circuito"}
        soup = BeautifulSoup(self.session.post(self.verificar_status,data=post).text, 'lxml')
        input_tag = soup.find_all(attrs={'name':'circ_id[]'})

        ## create table
        table = Table(title=circuito)

        if len(input_tag) > 0:
            circ_id = input_tag[0]['value']

            ## get circ_status
            post = {"circ_id[]":circ_id,"pesquisar":"Status circuito"}
            soup = BeautifulSoup(self.session.post(self.verificar_status,data=post).text, 'lxml')

            thead = soup.find('thead')
            Header = thead.text.split()

            table.add_column(Header[0])
            table.add_column(Header[1])
            table.add_column(Header[2])
            table.add_column(Header[3])
            table.add_column(str(Header[4]) + ' ' + str(Header[5]))
            table.add_column(str(Header[6]) + ' ' + str(Header[7]))
            table.add_column(str(Header[8]) + ' ' + str(Header[9]))

            tbody = soup.find_all('tbody')

            for t in tbody:
                cs = t.find_all('td')

                btv_link = '[link=http://tio.redeunifique.com.br/cadastros/planos_lista.php?codCliente=' + cs[4].text + ']' + cs[4].text + '[/link]'
                dalo_link = '[link=http://189.45.192.17/daloinfo/index.php?username=' + cs[5].text + ']' + cs[5].text + '[/link]'

                if cs[2].text == 'working':
                    ont_status = cs[2].text
                elif cs[2].text == 'LOS':
                    ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                else:
                    ont_status = "[warning]" + cs[2].text + "[/warning]"

                table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text)
        else:
            table.add_column(circuito)
            table.add_row('Circuito não encontrado ou não existem ONUs cadastradas nesse circuito.')

        self.console.print(table)

    def raw_verificar_circuito(self, circuito):
        ## get circ_id
        post = {"circ": circuito, "pesquisar":"Pesquisar Circuito"}
        soup = BeautifulSoup(self.session.post(self.verificar_status,data=post).text, 'lxml')
        input_tag = soup.find_all(attrs={'name':'circ_id[]'})

        if len(input_tag) > 0:
            circ_id = input_tag[0]['value']

            ## get circ_status
            post = {"circ_id[]":circ_id,"pesquisar":"Status circuito"}
            soup = BeautifulSoup(self.session.post(self.verificar_status,data=post).text, 'lxml')

            thead = soup.find('thead')
            Header = thead.text.split()

            tbody = soup.find_all('tbody')
            StatusClientes = []
            for t in tbody:
                StatusClientes.append(t.find_all('td'))

            SC = {'Header':Header,'Status':StatusClientes}
            return SC


    def paralel_verificar_circuito(self, Circuitos):
        threads = min(self.MAX_THREADS, len(Circuitos))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.verificar_circuito, Circuitos)

    def verificar_onu(self, sn):
        ## get status
        post = {"sn": sn, "pesquisar": "Ver Status"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')
        status = str().join(soup.find('p').text.splitlines())
        return status

    def verificar_pppoe_sn_circuito(self, login):
        ## get data
        post = {"login": login, "pesquisar": "Pesquisar Login"}
        soup = BeautifulSoup(self.session.post(self.outras_verificacoes, data=post).text, 'lxml')

        data = soup.find_all('td')
        if len(data) > 0:
            sn = data[3].text
            circuito = data[7].text
            return sn + '|' + circuito
        else:
            return False

    def verificar_pppoe_sn(self, login):
        ## get data
        post = {"login": login, "pesquisar": "Pesquisar Login"}
        soup = BeautifulSoup(self.session.post(self.outras_verificacoes, data=post).text, 'lxml')

        data = soup.find_all('td')
        if len(data) > 0:
            sn = data[3].text
            return sn
        else:
            return False

    def verificar_status_login(self, login):
        sn = self.verificar_pppoe_sn(login)

        table = Table()
        if sn != False:
            table.add_column(login)
            table.add_row(self.verificar_onu(sn))
        else:
            table.add_column(login)
            table.add_row('Login não encontrado')
        self.console.print(table)

    def paralel_verificar_status_login(self, Logins):
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(self.verificar_status_login, Logins)

    def verificar_status_login_get_circuito(self, login):
        data = self.verificar_pppoe_sn_circuito(login)

        table = Table()
        if data != False:
            data = data.split('|')
            table.add_column(login)
            table.add_row(self.verificar_onu(data[0]))
            circuito = data[1]
        else:
            table.add_column(login)
            table.add_row('Login não encontrado')
            circuito = False
        self.console.print(table)
        return circuito

class Integra_SA_ERP:

    def __init__(self):
        # Configurations
        custom_theme = Theme({
            "warning": "yellow",
            "disaster": "bold red"
        })
        self.console = Console(theme=custom_theme)

    def status_ca(self,CAs,StatusClientes):
        for i in range(len(CAs['Names'])):
            table = Table(title=CAs['Names'][i])

            table.add_column(StatusClientes['Header'][0])
            table.add_column(StatusClientes['Header'][1])
            table.add_column(StatusClientes['Header'][2])
            table.add_column(StatusClientes['Header'][3])
            table.add_column(str(StatusClientes['Header'][4]) + ' ' + str(StatusClientes['Header'][5]))
            table.add_column(str(StatusClientes['Header'][6]) + ' ' + str(StatusClientes['Header'][7]))
            table.add_column(str(StatusClientes['Header'][8]) + ' ' + str(StatusClientes['Header'][9]))

            for cs in StatusClientes['Status']:
                for c in CAs['Clientes'][i]:
                    if c == cs[4].text:
                        btv_link = '[link=http://tio.redeunifique.com.br/cadastros/planos_lista.php?codCliente=' + cs[4].text + ']' + cs[4].text + '[/link]'
                        dalo_link = '[link=http://189.45.192.17/daloinfo/index.php?username=' + cs[5].text + ']' + cs[5].text + '[/link]'

                        if cs[2].text == 'working':
                            ont_status = cs[2].text
                        elif cs[2].text == 'LOS':
                            ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                        else:
                            ont_status = "[warning]" + cs[2].text + "[/warning]"

                        table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text)
            self.console.print(table)

