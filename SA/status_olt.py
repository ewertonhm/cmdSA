from bs4 import BeautifulSoup
import httpx
from rich.table import Table
import concurrent.futures
import SA.busca_olt as busca_olt
from SA.sa_base import SA
from SA.status_onu import StatusOnu


# import time
# from rich import style
from pprint import pprint

class StatusOlt(SA):

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
        soup = BeautifulSoup(self.session.post(url, data=post, timeout=30).text, 'lxml')

        form = soup.find('form', attrs={'name': 'aa'})
        onus = form.find_all('option')
        uncg_onus = []
        for onu in onus:
            uncg_onus.append(onu.text)
        return uncg_onus

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

    def print_onus_disponiveis_ativacao(self, olt):
        table = Table(title="ONU disponíveis para ativação na OLT: {0}.".format(olt))
        circuitos = self.get_circuit_ids(olt)
        if len(circuitos)>0:
            table.add_column('ONU')
            table.add_column('Circuito')

            data = {
                "index": [],
                "thread": [],
                "circuito_id": [],
                "circuito": []
            }
            counter = 0
            for circuito in circuitos:
                circ = circuito.split('|')
                data['index'].append(counter)
                data['circuito_id'].append(circuito)
                data['circuito'].append(circ[1])

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    data['thread'].append(executor.submit(self.verificar_onus_disponiveis_ativacao_circuito, circuito))

                counter = counter+1

            for index in data['index']:
                uncf_onu = data['thread'][index].result()
                if len(uncf_onu)>0:
                    for onu in uncf_onu:
                        table.add_row(onu, data['circuito'][index])

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

                if cs[2].text.strip() == 'working':
                    ont_status = cs[2].text.strip()
                    working += 1
                elif cs[2].text.strip() == 'LOS':
                    ont_status = "[disaster]" + cs[2].text.strip() + "[/disaster]"
                elif cs[2].text.strip() == 'DyingGasp Sem energia':
                    ont_status = "[warning]DyingGasp[/warning]"
                else:
                    ont_status = "[warning]" + cs[2].text.strip() + "[/warning]"

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

    def verificar_status_olt(self, olt):
        ## Busca IDs da OLT e Interface
        db_olts = busca_olt.OLTs()
        slots = db_olts.get_olt_slots(olt)
        for i in range (1, len(slots)):
            self.verificar_status_olt_interface(olt,slots[i][0])