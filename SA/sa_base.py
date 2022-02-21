from bs4 import BeautifulSoup
import httpx
from conf.console_theme import *
import os
from conf.configs import find_path
from sys import exit

class SA:
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

        self.session = httpx.Client(follow_redirects=True)

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
        response = self.session.post(self.start_url, data=auth)
        soup = BeautifulSoup(response.text, 'lxml')
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

    def list_to_string(self, s):
        # initialize an empty string
        str1 = ""

        # traverse in the string
        for ele in s:
            str1 += ele

            # return string
        return str1

    def get_sinal_from_list_with_login(self, Lista, login):
        str_match = self.list_to_string([s for s in Lista if login in s])
        sinal = str_match[str_match.find('sinal')+6:str_match.find('(dbm)')]

        if sinal != '':
            if len(sinal) > 10:
                return 'N/A'
            else:
                return sinal
        else:
            return 'N/A'