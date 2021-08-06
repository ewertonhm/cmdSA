from time import sleep
import selenium
from selenium import webdriver
import argparse
import configparser
import pathlib
import inspect
import os, sys
import txt_rw
import base64
from Cryptodome.Cipher import AES
from colorama import init, Fore, Back, Style
from termcolor import colored
from pprint import pprint
from rich import print
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({
    "warning": "yellow",
    "disaster": "bold red"
})

# initialize colorama
init(convert=True)


# pip install selenium
# maquina que executar o script PRECISA ter um navegador instalado
# necessário ter o chromedriver compátivel com a versão do chrome instalada na maquina, salva no diretório do script (pode ser em outro diretório, mas dai precisa declarar o path na declaração do objeto driver)
# https://chromedriver.storage.googleapis.com/index.html


# configurações do parser, responsável por receber os parâmetros na hora de rodar o script
parser = argparse.ArgumentParser(description='Verifica status dos circuitos no Sistema de Ativação.\r\n Criado por Ewerton H. Marschalk')
parser.add_argument('-c', '--circuito', nargs='+', required=True)
args = parser.parse_args()

# recuperando parâmetros
Circuitos = args.circuito

# criando objeto da biblioteta responsável por ler os credenciais do arquivo .ini
config = configparser.ConfigParser()

# setando nome e caminho do arquivo com as credenciais
filename = inspect.getframeinfo(inspect.currentframe()).filename
path = os.path.abspath(os.path.dirname(sys.argv[0]))

# criando objeto da biblioteca pathlib com o caminho do arquivo credentials.ini
p = pathlib.Path(str(path) + '\.credentials.ini')

# verifica se o arquivo credentials existe, se não, cria ele com o testo padrão
if not p.exists():
    p.touch()
    txt_rw.empty_credentials()

# lê o arquivo credentials.ini
config.read(str(path) + '\.credentials.ini')

# se o arquivo estiver com o seu padrão, exibe instruções para preencher ele e da quit
if config.get('credentials-sa', 'Login') == 'usuario@redeunifique.com.br' and config.get('credentials-sa',
                                                                                         'Senha') == 'senha':
    print(
        'Durante a execução, desse script, o mesmo irá necessitar logar no sistema de ativação para realizar consultas;')
    print('Para prosseguir, insira suas credenciais no arquivo: {0}'.format(p.absolute()))

    print('Por questões de segurança, a senha deve ser primeiramente criptografada usando o script: cripto.exe')
    sys.exit()

# verifica se o arquivo webdriver se encontra na pasta certa, se não, exibe instruções para baixar ele
if not pathlib.Path("C:\webdriver\chromedriver.exe").exists():
    print("Para prosseguir, faça o download do chromedriver e salve no diretorio: 'C:/webdriver/chomedriver.exe'")
    print("Baixe o arquivo em: https://chromedriver.storage.googleapis.com/index.html")
    print("Baixe da mesma versão que o google chrome instalado no seu computador para evitar erros")
    sys.exit()

# verificar o caminho do chromedriver
executable_path = config.get('options','chromedriver_executable_path')

# define opções padrões e instancia o webdriver
options = selenium.webdriver.chrome.options.Options()
Keys = selenium.webdriver.common.keys.Keys
options.headless = True
options.add_argument('log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = selenium.webdriver.Chrome(executable_path=executable_path, options=options)


# realiza o login no sistema de ativação
def sa_site_login():
    login = config.get('credentials-sa', 'Login')

    # descriptografa a senha
    secret_key = b''
    cipher = AES.new(secret_key, AES.MODE_ECB)
    password = cipher.decrypt(base64.b64decode(config.get('credentials-sa', 'Senha').encode('utf-8')))
    password = password.decode('utf-8')
    password = password.strip()

    driver.get("http://ativacaofibra.redeunifique.com.br/")
    driver.find_element_by_name("login").send_keys(login)
    driver.find_element_by_name("senha").send_keys(password)
    driver.find_element_by_id("entrar").click()


# consulta o circuito e retorna uma String com o resultado
def verificar_circuito(circuito):
    driver.get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status")

    driver.find_element_by_name("circ").send_keys(circuito)
    driver.find_element_by_name("circ").send_keys(Keys.ENTER)
    value = None
    try:
        driver.find_element_by_name("circ_id").send_keys(Keys.SPACE)
        driver.find_element_by_name("pesquisar").click()
        value = driver.find_element_by_id("maintable").text
    except:
        value = 'error'
    return value


# Realiza login no sistema de ativação
sa_site_login()

# para cada circuito na lista Circuitos,
# pega as informações do
for circuito in Circuitos:
    sc = verificar_circuito(circuito)

    if sc == 'error':
        console.print(circuito + ': circuito não encontrado ou não existem ONUs cadastradas nesse circuito.')
    else:
        table = Table(title=circuito)
        circuito = sc.splitlines()
        Header = circuito[0].split()
        circuito.pop(0)


        table.add_column(Header[0])
        table.add_column(Header[1])
        table.add_column(Header[2])
        table.add_column(Header[3])
        table.add_column(str(Header[4]) + ' ' + str(Header[5]))
        table.add_column(str(Header[6]) + ' ' + str(Header[7]))
        table.add_column(str(Header[8]) + ' ' + str(Header[9]))

        for c in circuito:
            cs = c.split()

            btv_link = '[link=http://tio.redeunifique.com.br/cadastros/planos_lista.php?codCliente=' + str(cs[4]) + ']' + str(cs[4]) + '[/link]'
            dalo_link = '[link=http://189.45.192.17/daloinfo/index.php?username=' + str(cs[5]) + ']' + str(cs[5]) + '[/link]'

            if cs[2] == 'working':
                ont_status = str(cs[2])
            elif cs[2] == 'LOS':
                ont_status = "[disaster]" + str(cs[2]) + "[/disaster]"
            else:
                ont_status = "[warning]" + str(cs[2]) + "[/warning]"

            table.add_row(str(cs[0]), str(cs[1]), ont_status, str(cs[3]), btv_link, dalo_link, str(cs[6]))

        console = Console(theme=custom_theme)
        console.print(table)
        print()


driver.quit()
driver = None
