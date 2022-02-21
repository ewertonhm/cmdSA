from bs4 import BeautifulSoup
from rich.table import Table
from concurrent.futures.thread import ThreadPoolExecutor as Executor
import concurrent.futures
from SA.sa_base import SA


class StatusOnu(SA):

    def verificar_onu(self, sn):
        """
        Busca o status de um serial number no sistema de ativação e retorna
        :param sn: String
        :return: String
        """
        ## get status
        post = {"sn": sn, "pesquisar": "Ver Status"}
        soup = BeautifulSoup(self.session.post(self.verificar_status, data=post, timeout=45).text, 'lxml')
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

    def get_status_sn(self, sn):
        table = Table()
        if sn != False:
            table.add_column(sn)
            table.add_row(f'Serial: {sn}, {self.verificar_onu(sn)}')
        else:
            table.add_column(sn)
            table.add_row('SN não encontrado')
        self.console.print(table)

    def raw_get_status_from_sn(self, sn):
        if sn != False:
            s = StatusOnu(self.login, self.senha)
            return s.verificar_onu(sn)
        else:
            return 'N/A'


    def paralel_get_status_sn(self, SNs):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sinais = [executor.submit(self.raw_get_status_from_sn, sn) for sn in SNs]

        sinais_result = [s.result() for s in sinais]

        return sinais_result


    def get_status_login(self, login):
        data = self.get_sn_and_circuit_from_login(login)
        data = data.split('|')
        sn = data[0]
        circuito = data[1]

        table = Table()
        if sn != False:
            table.add_column(login)
            table.add_row(f'Serial: {sn}, {self.verificar_onu(sn)[4:]}, circuito: {circuito}')
        else:
            table.add_column(login)
            table.add_row('Login não encontrado')
        self.console.print(table)

    def paralel_get_status_login(self, Logins):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sinais = [executor.submit(self.get_status_login, login) for login in Logins]

        sinais_result = [s.result() for s in sinais]

    def get_sn_from_login(self, login):
        ## get data
        post = {"login": login, "pesquisar": "Pesquisar Login"}
        soup = BeautifulSoup(self.session.post(self.outras_verificacoes, data=post).text, 'lxml')

        data = soup.find_all('td')
        if len(data) > 0:
            sn = data[3].text
            return sn
        else:
            return False


    def get_sn_and_circuit_from_login(self, login):
        ## get data
        post = {"login": login, "pesquisar": "Pesquisar Login"}
        soup = BeautifulSoup(self.session.post(self.outras_verificacoes, data=post, timeout=30).text, 'lxml')

        data = soup.find_all('td')
        if len(data) > 0:
            sn = data[3].text
            circuito = data[7].text
            return sn + '|' + circuito
        else:
            return False