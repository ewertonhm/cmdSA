from bs4 import BeautifulSoup
import httpx
from rich.table import Table
from concurrent.futures.thread import ThreadPoolExecutor as Executor
from SA.sa_base import SA
from SA.status_onu import StatusOnu

class StatusCircuito(SA):
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
        working = 0
        total = None

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

            for t in tbody:
                cs = t.find_all('td')

                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                btv_link = '[link=' + link + ']' + link[cod_location+11:] + '[/link]'
                dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[
                    5].text + '[/link]'

                if cs[2].text.strip() == 'working':
                    ont_status = cs[2].text.strip()
                    working += 1
                elif cs[2].text.strip() == 'LOS':
                    ont_status = "[disaster]" + cs[2].text.strip() + "[/disaster]"
                elif cs[2].text.strip() == 'DyingGasp Sem energia':
                    ont_status = "[warning]DyingGasp[/warning]"
                else:
                    ont_status = "[warning]" + cs[2].text.strip() + "[/warning]"

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
        working = 0
        total = None

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
            sinal = []

            s = StatusOnu(self.login, self.senha)

            SNs = []
            for t in tbody:
                cs = t.find_all('td')
                SNs.append(cs[3].text)
                #sinal.append(s.verificar_onu_array(cs[3].text))

            status = s.paralel_get_status_sn(SNs)

            counter = 0
            for t in tbody:
                cs = t.find_all('td')

                link = cs[4].find('a')
                link = link['href']
                cod_location = str(link).find('codCliente=')

                btv_link = '[link=' + link + ']' + link[cod_location+11:] + '[/link]'
                dalo_link = '[link=https://dashboard.redeunifique.com.br/dash_cliente.php?item=' + cs[5].text + ']' + cs[5].text + '[/link]'
                if cs[2].text.strip() == 'working':
                    ont_status = cs[2].text.strip()
                    working += 1
                elif cs[2].text.strip() == 'LOS':
                    ont_status = "[disaster]" + cs[2].text.strip() + "[/disaster]"
                elif cs[2].text.strip() == 'DyingGasp Sem energia':
                    ont_status = "[warning]DyingGasp[/warning]"
                else:
                    ont_status = "[warning]" + cs[2].text.strip() + "[/warning]"

                sinal = self.get_sinal_from_list_with_login(status, cs[5].text)
                table.add_row(cs[0].text, cs[1].text, ont_status, sinal, cs[3].text, btv_link, dalo_link, cs[6].text)
                counter = counter+1

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
            SNs = []
            for t in tbody:
                data = t.find_all('td')
                SNs.append(data[3].text)
                StatusClientes.append(data)


            SC = {'Header':Header,'Status':StatusClientes, 'Seriais': SNs}
            return SC

    def verificar_status_login_get_circuito(self, login):
        s = StatusOnu(self.login, self.senha)

        data = s.get_sn_and_circuit_from_login(login)

        table = Table()
        if data != False:
            data = data.split('|')
            table.add_column(login)
            table.add_row(s.verificar_onu(data[0]))
            circuito = data[1]
        else:
            table.add_column(login)
            table.add_row('Login não encontrado')
            circuito = False
        self.console.print(table)
        return circuito

    '''

    '''

    '''

    '''

