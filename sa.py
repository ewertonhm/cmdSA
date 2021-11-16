from bs4 import BeautifulSoup
import httpx
from rich.table import Table
from rich import style
from concurrent.futures.thread import ThreadPoolExecutor as Executor
import time
import concurrent.futures
from console_theme import *
import os
import busca_olt
from configs import find_path
from sys import exit
from configs import Credentials

class SistemaAtivacao:
    start_url = 'http://ativacaofibra.redeunifique.com.br/auth.php'
    verificar_status = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status'
    outras_verificacoes = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados'
    ids_cadastrados = 'http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados'

    def __init__(self, login, senha):
        """
        Estância um client da biblioteca httpx
        Tenta realizar o login no sistema de ativação com a função do_login()
        Se não conseguir realizar login, imprime um aviso na tela, exclui o usuário e senha salvos e finaliza

        :param login: login do sistema de ativação
        :param senha: senha do sistema de ativação
        """
        self.login = login
        self.senha = senha
        self.acao = 'Entrar'

        self.session = httpx.Client()

        logged = self.do_login()

        if not logged:
            print("Falha ao realizar Login no Sistema de Ativação")
            print("Verifique a senha!")
            print("Senha salva foi deletada, necessário rodar o script novamente para reconfigurar a senha.")
            credentials_path = find_path() + 'credentials.ini'
            os.remove(credentials_path)
            exit()

        self.console = CONSOLE

    def do_login(self):
        """
        Tenta realizar login no sistema de ativação, caso consiga retona True, do contrário False

        :return: boolean
        """
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        soup = BeautifulSoup(self.session.post(self.start_url, data=auth).text, 'lxml')
        if soup.find(id='logout') != None:
            return True
        else:
            return False

    def split(self, a, n):
        """
        TODO: documentar

        :param a:
        :param n:
        :return:
        """
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    def list_to_array(self, List):
        """
        Transforma uma lista em um string com os valores divididos por virgula
        :param List: Lista de circuitos
        :return: String
        """
        f = ''
        for l in List:
            f = "{0},{1}".format(f,l)
        return f[1:]

    def verificar_circuitos(self, Circuitos, verf_sinal):
        """
        Recebe uma lista de circuitos, consulta seus IDs no sistema de ativação,
        Passa os IDs para a função print_circuito() executar de forma asyncrona.
        :param Circuitos: Lista de strings com os nomes dos circuitos
        :param verf_sinal: Boolean que define se irá verificar o sinal do circuito
        :return: Sem retorno
        """
        post = {"circ": self.list_to_array(Circuitos), "pesquisar":"Pesquisar Circuito"}
        soup = BeautifulSoup(self.session.post(self.verificar_status,data=post).text, 'lxml')
        input_tag = soup.find_all(attrs={'name':'circ_id[]'})

        if verf_sinal:
            with Executor() as executor:
                [executor.submit(self.print_circuito_sinal, tag) for tag in input_tag]
        else:
            with Executor() as executor:
                [executor.submit(self.print_circuito, tag) for tag in input_tag]

    def print_circuito(self,circ_id):
        """
        recebe um id do circuito, consulta esse circuito no sistema de ativação, monta uma tabela com os dados e imprime na tela.

        :param circ_id: string gerado pela função verificar_circuitos()
        :return: Exibe na tela
        """
        circuito = str(circ_id['value']).split('|')[1]
        ## create table
        table = Table(title=circuito)

        session = httpx.Client()
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        session.post(self.start_url, data=auth, timeout=30)

        ## get circ_status
        post = {"circ_id[]": circ_id['value'], "pesquisar": "Status circuito"}
        soup = BeautifulSoup(session.post(self.verificar_status, data=post, timeout=30).text, 'lxml')

        #soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')

        thead = soup.find('thead')
        try:
            Header = thead.text.split()
            table.add_column(Header[0])
            table.add_column(Header[1])
            table.add_column(Header[2])
            table.add_column(Header[3])
            table.add_column(str(Header[4]) + ' ' + str(Header[5]))
            table.add_column(str(Header[6]) + ' ' + str(Header[7]))
            table.add_column(str(Header[8]) + ' ' + str(Header[9]))

            tbody = soup.find_all('tbody')

            total = len(tbody)
            working = 0

            for t in tbody:
                cs = t.find_all('td')

                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                btv_link = '[link=' + link + ']' + link[cod_location+11:] + '[/link]'
                dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[
                    5].text + '[/link]'

                if cs[2].text == 'working':
                    ont_status = cs[2].text
                    working += 1
                elif cs[2].text == 'LOS':
                    ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                else:
                    ont_status = "[warning]" + cs[2].text + "[/warning]"

                table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text)
        except Exception as e:
            table.add_column(circuito)
            table.add_row('Circuito não encontrado ou não existem ONUs cadastradas nesse circuito.')
        finally:
            table.caption = str('Working: {0}/{1}'.format(working, total))
            self.console.print(table)
            print()

    def print_circuito_sinal(self,circ_id):
        """
        recebe um id do circuito, consulta esse circuito no sistema de ativação, monta uma tabela com os dados e imprime na tela.

        :param circ_id: string gerado pela função verificar_circuitos()
        :return: Exibe na tela
        """
        circuito = str(circ_id['value']).split('|')[1]
        ## create table
        table = Table(title=circuito)

        session = httpx.Client()
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        session.post(self.start_url, data=auth, timeout=30)

        ## get circ_status
        post = {"circ_id[]": circ_id['value'], "pesquisar": "Status circuito"}
        soup = BeautifulSoup(session.post(self.verificar_status, data=post, timeout=30).text, 'lxml')

        #soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')

        thead = soup.find('thead')
        try:
            Header = thead.text.split()
            table.add_column(Header[0])
            table.add_column(Header[1])
            table.add_column(Header[2])
            table.add_column("Sinal")
            table.add_column(Header[3])
            table.add_column(str(Header[4]) + ' ' + str(Header[5]))
            table.add_column(str(Header[6]) + ' ' + str(Header[7]))
            table.add_column(str(Header[8]) + ' ' + str(Header[9]))

            tbody = soup.find_all('tbody')

            total = len(tbody)
            working = 0

            for t in tbody:
                cs = t.find_all('td')

                sinal = self.verificar_onu_array(cs[3].text)

                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                btv_link = '[link=' + link + ']' + link[cod_location+11:] + '[/link]'
                dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[
                    5].text + '[/link]'

                if cs[2].text == 'working':
                    ont_status = cs[2].text
                    working += 1
                elif cs[2].text == 'LOS':
                    ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                else:
                    ont_status = "[warning]" + cs[2].text + "[/warning]"

                table.add_row(cs[0].text, cs[1].text, ont_status, sinal['sinal'], cs[3].text, btv_link, dalo_link, cs[6].text)
        except Exception as e:
            table.add_column(circuito)
            table.add_row('Circuito não encontrado ou não existem ONUs cadastradas nesse circuito.')
        finally:
            table.caption = str('Working: {0}/{1}'.format(working, total))
            self.console.print(table)
            print()

    def raw_verificar_circuito(self, circuito):
        """
        Consulta um circuito e retorna uma Lista com os valores
        :param circuito: string
        :return: Lista
        """
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
        """
        TODO: verificar se ainda é utilizado em alguma parte do código
        :param Circuitos:
        :return:
        """
        threads = min(self.MAX_THREADS, len(Circuitos))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.verificar_circuito, Circuitos)

    def verificar_onu(self, sn):
        """
        Busca o status de um serial number no sistema de ativação e retorna
        :param sn: String
        :return: String
        """
        ## get status
        post = {"sn": sn, "pesquisar": "Ver Status"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')
        status = str().join(soup.find('p').text.splitlines())
        return status

    def verificar_onu_array(self, sn):
        """
        Busca o status de um serial number no sistema de ativação e retorna
        :param sn: String
        :return: String
        """
        ## get status
        post = {"sn": sn, "pesquisar": "Ver Status"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')
        onu = soup.find('p').text.splitlines()
        sinal = 'N/A'
        status = 'N/A'
        try:
            status_pos = onu[0].find(' está ')
            status = onu[0][status_pos + 6:]


            if status == 'working':
                sinal_pos = onu[1].find('com sinal ')
                sinal = onu[1][sinal_pos + 10:]
        except Exception:
            pass

        return {"status":status,"sinal":sinal}

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

    def verificar_status_sn(self, sn):
        table = Table()
        if sn != False:
            table.add_column(sn)
            table.add_row(self.verificar_onu(sn))
        else:
            table.add_column(sn)
            table.add_row('SN não encontrado')
        self.console.print(table)

    def verificar_status_olt(self, olt):
        ## Busca IDs da OLT e Interface
        db_olts = busca_olt.OLTs()
        slots = db_olts.get_olt_slots(olt)
        for i in range (1, len(slots)):
            self.verificar_status_olt_interface(olt,slots[i][0])

    def get_circuit_ids(self, olt):
        """
        Recebe o nome de uma OLT e retorna o circ_id de todos os cricuitos dessa OLT

        :param olt: String com o nome da OLT
        :return: Lista com os circ_ids
        """
        db_olts = busca_olt.OLTs()
        circuitos = db_olts.get_olt_circuitos(olt)
        Circuitos = []
        for circuito in circuitos:
            Circuitos.append(circuito[0])

        post = {"circ": self.list_to_array(Circuitos), "pesquisar": "Pesquisar Circuito"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')
        input_tag = soup.find_all(attrs={'name': 'circ_id[]'})

        circ_ids = []
        for c in input_tag:
            circ_ids.append(c['value'])
        return circ_ids

    def reorganize_circ_id_ativ(self, circ_id):
        """
        reorganiza o circ_id coletado no status para ser usado na ativação
        :param circ_id: String
        :return: String
        """
        dados = circ_id.split("|")
        circ_id = dados[0]
        circ_name = dados[1]
        olt_id = dados[2]
        slot = dados[3]
        slot_id = dados[4]

        dados_new = '{0}|{1}|{2}|{3}|{4}|ativo'.format(olt_id, slot_id, circ_name, slot, circ_id)

        return dados_new

    def verificar_onus_disponiveis_ativacao_circuito(self, circ_id):
        """
        http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=novos_cadastros/ativar_onu
        Verifica se existe alguma ONU disponível para ativação no circuito.

        :param circ_id:
        :return:
        """
        url = "http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=novos_cadastros/ativar_onu"
        circuito = self.reorganize_circ_id_ativ(circ_id)
        post = {"circ_id": circuito, "botao": "Verificar ONU disponíveis para ativação "}
        soup = BeautifulSoup(self.session.post(url, data=post).text, 'lxml')

        form = soup.find('form', attrs={'name': 'aa'})
        onus = form.find_all('option')
        uncg_onus = []
        for onu in onus:
            uncg_onus.append(onu.text)
        return uncg_onus

    def print_onus_disponiveis_ativacao(self, olt):
        table = Table(title="ONU disponíveis para ativação na OLT: {0}.".format(olt))

        circuitos = self.get_circuit_ids(olt)
        if len(circuitos)>0:
            table.add_column('ONU')
            table.add_column('Circuito')

            for circuito in circuitos:
                uncf_onus = self.verificar_onus_disponiveis_ativacao_circuito(circuito)
                circ = circuito.split('|')
                for onu in uncf_onus:
                    table.add_row(onu,circ[1])
        else:
            table.add_row('Não há ONU sem configuração.')

        self.console.print(table)

    def verificar_status_id(self, olt, cod_cli):
        title = str('Status ONUs na OLT {0}, com o Client ID {1}:'.format(olt, cod_cli))
        ## create table
        table = Table(title=title)

        ## Criar sessão e logar
        timeout = httpx.Timeout(10.0, connect=60.0)
        session = httpx.Client(timeout=timeout)
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        session.post(self.start_url, data=auth)

        ## Busca IDs da OLT e Interface
        db_olts = busca_olt.OLTs()
        olt_id = db_olts.get_olt_id(olt)
        #interface_id = db_olts.get_olt_slot_id(olt, interface)

        ## get circ_status
        post = {"pesquisar": "Listar todos ID dessa OLT", "id_olt": olt_id}
        soup = BeautifulSoup(session.post(self.ids_cadastrados, data=post).text, 'lxml')

        thead = soup.find('thead')
        total = 0

        try:
            Header = thead.text.split()

            # interface
            table.add_column(Header[0])
            # id
            table.add_column(Header[1])
            #SN
            table.add_column(Header[2])
            # status
            table.add_column("Status")
            # sinal
            table.add_column("Sinal")
            # codigo cliente
            table.add_column(str(Header[3]) + ' ' + str(Header[4]))
            # login pppoe
            table.add_column(str(Header[5]) + ' ' + str(Header[6]))
            # senha pppoe
            #table.add_column(str(Header[7]) + ' ' + str(Header[8]))
            # circuito
            table.add_column(Header[9])
            # voip usuario p1
            #table.add_column(str(Header[10]) + ' ' + str(Header[11]) + ' ' + str(Header[12]))
            # senha p1 voip
            #table.add_column(str(Header[13]) + ' ' + str(Header[14]) + ' ' + str(Header[15]))
            #coip usuario p2
            #table.add_column(str(Header[16]) + ' ' + str(Header[17]) + ' ' + str(Header[18]))
            # senha p2 void
            #table.add_column(str(Header[19]) + ' ' + str(Header[20]) + ' ' + str(Header[21]))
            # iptv
            #table.add_column(Header[22])
            # vlan
            table.add_column(Header[23])
            # inner vlan
            table.add_column(str(Header[24]) + ' ' + str(Header[25]))
            # modo de config
            #table.add_column(str(Header[26]) + ' ' + str(Header[27]) + ' ' + str(Header[28]))
            # bridge - vlans
            #table.add_column(str(Header[29]) + ' ' + str(Header[30]) + ' ' + str(Header[31]))
            # bridge - portas utilizáveis
            #table.add_column(str(Header[32]) + ' ' + str(Header[33]) + ' ' + str(Header[34]) + ' ' + str(Header[35]))
            # modelo onu
            #table.add_column(str(Header[36]) + ' ' + str(Header[37]))
            # data cadastro
            #table.add_column(str(Header[38]) + ' ' + str(Header[39]))
            # usuario resp ativação
            #table.add_column(str(Header[40]) + ' ' + str(Header[41]) + ' ' + str(Header[42]))

            tbody = soup.find_all('tbody')

            for t in tbody:
                cs = t.find_all('td')
                link = cs[3].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                if link[cod_location + 11:] == cod_cli:

                    btv_link = '[link=' + link + ']' + link[cod_location + 11:] + '[/link]'
                    dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[4].text + ']' + cs[4].text + '[/link]'

                    sinal = 'N/A'
                    status = 'N/A'

                    onu_status = self.verificar_onu_array(cs[2].text)

                    sinal = onu_status['sinal']
                    status = onu_status['status']

                    table.add_row(
                        cs[0].text,
                        cs[1].text,
                        cs[2].text,
                        status,
                        sinal,
                        btv_link,
                        dalo_link,
                        cs[6].text,
                        # cs[7].text,
                        # cs[8].text,
                        # cs[9].text,
                        # cs[10].text,
                        # cs[11].text,
                        cs[12].text,
                        cs[13].text
                        # cs[14].text,
                        # cs[15].text
                    )
                    total = total + 1
        except Exception as e:
            table.add_column(olt)
            table.add_row('ID não encontrado ou não existem ONUs cadastradas com esse ID.')
            '''
            print('#' * 20)
            pprint.pprint(e)
            pprint.pprint(thead)

            print('#' * 20)
            pprint.pprint(soup)
            print('#' * 20)
            print()
            '''
        finally:
            if total == 0:
                table.add_row('N/A','N/A','N/A','N/A','N/A','N/A','N/A','N/A')
            self.console.print(table)
            print()

    def verificar_status_olt_interface(self, olt, interface):
        title = str('Status ONUs na interface {0}, da OLT {1}:'.format(interface, olt))
        ## create table
        table = Table(title=title)

        ## Criar sessão e logar
        timeout = httpx.Timeout(10.0, connect=60.0)
        session = httpx.Client(timeout=timeout)
        auth = {"login": self.login, "senha": self.senha, "acao": self.acao}
        session.post(self.start_url, data=auth)

        ## Busca IDs da OLT e Interface
        db_olts = busca_olt.OLTs()
        olt_id = db_olts.get_olt_id(olt)
        interface_id = db_olts.get_olt_slot_id(olt, interface)

        ## get circ_status
        post = {"id_olt": olt_id, "int_name": interface_id, "circ_id[]": "selecione", "pesquisar":"Continuar"}
        soup = BeautifulSoup(session.post(self.verificar_status, data=post).text, 'lxml')

        # soup = BeautifulSoup(self.session.post(self.verificar_status, data=post).text, 'lxml')

        thead = soup.find('thead')

        total = None
        working = None

        try:
            Header = thead.text.split()
            table.add_column(Header[0])
            table.add_column(Header[1])
            table.add_column(Header[2])
            table.add_column(Header[3])
            table.add_column(str(Header[4]) + ' ' + str(Header[5]))
            table.add_column(str(Header[6]) + ' ' + str(Header[7]))
            table.add_column(str(Header[8]) + ' ' + str(Header[9]))
            table.add_column(Header[12])


            tbody = soup.find_all('tbody')

            total = len(tbody)
            working = 0

            for t in tbody:
                cs = t.find_all('td')

                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                btv_link = '[link=' + link + ']' + link[cod_location + 11:] + '[/link]'
                dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[
                    5].text + '[/link]'

                if cs[2].text == 'working':
                    ont_status = cs[2].text
                    working += 1
                elif cs[2].text == 'LOS':
                    ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                else:
                    ont_status = "[warning]" + cs[2].text + "[/warning]"

                table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text, cs[8].text)
        except Exception as e:
            table.add_column(interface)
            table.add_row('Interface/olt não encontrado ou não existem ONUs cadastradas nesse circuito.')
            '''
            print('#' * 20)
            pprint.pprint(e)
            pprint.pprint(thead)

            print('#' * 20)
            pprint.pprint(soup)
            print('#' * 20)
            print()
            '''
        finally:
            table.caption = str('Working: {0}/{1}'.format(working, total))
            self.console.print(table)
            print()

class Integra_SA_ERP:

    def __init__(self):
        # Configurations
        custom_theme = Theme({
            "warning": "yellow",
            "disaster": "bold red"
        })
        self.console = Console(theme=custom_theme)

    def status_ca(self,CAs,StatusClientes, sinal):
        s = None
        if sinal:
            credenciais = Credentials()
            s = SistemaAtivacao(credenciais.getLogin(), credenciais.getSenha())

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

                        if cs[2].text == 'working':
                            ont_status = cs[2].text
                        elif cs[2].text == 'LOS':
                            ont_status = "[disaster]" + cs[2].text + "[/disaster]"
                        else:
                            ont_status = "[warning]" + cs[2].text + "[/warning]"
                        if sinal:
                            sin = s.verificar_onu_array(cs[3].text)
                            table.add_row(cs[0].text, cs[1].text, ont_status, sin['sinal'], cs[3].text, btv_link, dalo_link, cs[6].text)
                        else:
                            table.add_row(cs[0].text, cs[1].text, ont_status, cs[3].text, btv_link, dalo_link, cs[6].text)
            self.console.print(table)

