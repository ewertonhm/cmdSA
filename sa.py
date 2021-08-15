from bs4 import BeautifulSoup
import requests
from rich import print
from rich.console import Console
from rich.theme import Theme
from rich.table import Table

class SistemaAtivacao:
    start_url = 'http://ativacaofibra.redeunifique.com.br/auth.php'
    home = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php'
    verificar_status = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status'
    outras_verificacoes = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados'



    def __init__(self, login, senha):
        self.login = login
        self.senha = senha
        self.acao = 'Entrar'

        self.session = requests.session()

        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        self.session.post(self.start_url, auth)

        home = self.session.get(self.home)
        # Configurations
        custom_theme = Theme({
            "warning": "yellow",
            "disaster": "bold red"
        })
        self.console = Console(theme=custom_theme)

    def verificar_circuito(self, circuito):
        ## get circ_id
        post = {"circ": circuito, "pesquisar":"Pesquisar Circuito"}
        soup = BeautifulSoup(self.session.post(self.verificar_status,post).text, 'lxml')
        input_tag = soup.find_all(attrs={'name':'circ_id'})

        ## create table
        table = Table(title=circuito)

        if len(input_tag) > 0:
            circ_id = input_tag[0]['value']

            ## get circ_status
            post = {"circ_id":circ_id,"pesquisar":"Status circuito"}
            soup = BeautifulSoup(self.session.post(self.verificar_status,post).text, 'lxml')

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

    def verificar_onu(self, sn):
        ## get status
        post = {"sn": sn, "pesquisar": "Ver Status"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, post).text, 'lxml')
        status = str().join(soup.find('p').text.splitlines())
        return status


    def verificar_pppoe_data(self, login):
        ## get data
        post = {"login": login, "pesquisar": "Pesquisar Login"}
        soup = BeautifulSoup(self.session.post(self.outras_verificacoes, post).text, 'lxml')

        data = soup.find_all('td')
        if len(data) > 0:
            sn = data[3].text
            circuito = data[7].text
            return sn + '|' + circuito
        else:
            return False



