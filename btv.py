from bs4 import BeautifulSoup
import httpx

class Erp:
    ERP_LOGIN = 'http://erp.redeunifique.com.br/login/Lw=='
    cm_gerenciar_caixa = 'http://erp.redeunifique.com.br/engenharia/cm_gerenciar_caixa/'
    cm_gerenciar_caixa_json = 'http://erp.redeunifique.com.br/ajax/cm_gerenciar_caixa_json.php?ajax=true'


    def __init__(self, login, senha):
        self.login = login
        self.senha = senha

        self.session = httpx.Client()

        auth = {"login": self.login, "senha": self.senha}

        self.session.post(self.ERP_LOGIN, data=auth)


    def buscar_cas(self, circuito):
        ca = 'CA-' + circuito[:-1] + '-' + circuito[-1:]

        post = {
            "cm_cod_cidade":"",
            "cm_cod_predio":"",
            "cm_caixa":ca,
            "cm_logradouro":"",
            "cm_protocolo":"",
            "cm_descricaoPortaNome":"",
            "cm_circuitoIDD":"",
            "cm_latitude":"",
            "cm_longitude":""
        }

        soup = BeautifulSoup(self.session.post(self.cm_gerenciar_caixa, data=post).text, 'lxml')
        buttons = soup.find_all('button', {"class": "btn_editarCaixa"})
        names = soup.find_all('button', {"class":"btn_historicoCaixa"})

        Names = []
        IDs = []

        for i in range(len(buttons)):
            IDs.append(self.pegar_ids_ca(buttons[i]['data-componentid'], buttons[i]['data-designation']))
            Names.append(names[i]['data-caixa'])

        CAs = {"Names":Names,"Clientes":IDs}
        return CAs


    def pegar_ids_ca(self,ComponentID,DesignationID):
        post = {
            "paramComponentID":ComponentID,
            "paramDesignationID":DesignationID,
            "ajax":"true",
            "acao":"retornarCaixa"
        }
        soup = BeautifulSoup(self.session.post(self.cm_gerenciar_caixa_json, data=post).text, 'lxml')
        links = soup.find_all('a', href=True)
        IDs = []
        for link in links:
            position = str(link['href']).find('codCliente=')
            IDs.append(link['href'][position+11:-2])
        return IDs


class Bemtevi:
    BTV_LOGIN = 'http://tio.redeunifique.com.br/login/index.php'

    def __init__(self):
        pass


