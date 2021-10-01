import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import configparser
import pathlib
import inspect
import os, sys
import time
from configs import find_path


def create_olt_file():
    path = find_path()
    filename = path + 'olts.ini'
    f=open(filename, "w")
    f.close()

def create_circuitos_file():
    path = find_path()
    filename = path + 'circuitos.ini'
    f=open(filename, "w")
    f.close()
    write_to_circuitos_file('[circuitos]')

def write_to_circuitos_file(string):
    path = find_path()
    filename = path + 'circuitos.ini'

    # Open the file in append & read mode ('a+')
    with open(filename, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(string)

def write_to_olt_file(string):
    path = find_path()
    filename = path + 'olts.ini'

    # Open the file in append & read mode ('a+')
    with open(filename, "a+") as file_object:
        # Move read cursor to the start of file.
        file_object.seek(0)
        # If file is not empty then append '\n'
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        # Append text at the end of file
        file_object.write(string)

def add_olt_to_file(olt_name,olt_id):
    write_to_olt_file('[{0}]'.format(olt_name))
    write_to_olt_file('id:' + olt_id)

def add_slots_to_file(slot,id):
    write_to_olt_file('{0}:{1}'.format(slot,id))

def add_olt_circuitos_to_file(olt_name):
    write_to_olt_file('[CIRCUITOS-{0}]'.format(olt_name))

def add_circuito_to_file(circuito,id):
    write_to_olt_file('{0}:{1}'.format(circuito, id))
    write_to_circuitos_file('{0}:{1}'.format(circuito, id))


def start_driver():
    path = find_path()
    filename = path + 'chromedriver.exe'

    print('aguarde...')
    options = selenium.webdriver.chrome.options.Options()
    options.headless = True
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # path do webdriver, o mesmo pode ser baixado em: https://chromedriver.chromium.org/downloads
    driver = selenium.webdriver.Chrome(executable_path=r"{0}".format(filename), options=options)

    return driver

def sa_site_login(login, senha):
    driver = start_driver()

    logo = None
    driver.get("http://ativacaofibra.redeunifique.com.br/")
    try:
        logo = driver.find_element_by_id("centro").find_element_by_tag_name("img").get_attribute("src")
    except:
        driver.find_element_by_name("login").send_keys(login)
        driver.find_element_by_name("senha").send_keys(senha)
        driver.find_element_by_id("entrar").click()

    if logo == 'http://ativacaofibra.redeunifique.com.br/cadastro/img/logo2017.png':
        return driver
    else:
        try:
            logo = driver.find_element_by_id("centro").find_element_by_tag_name("img").get_attribute("src")
            if logo == 'http://ativacaofibra.redeunifique.com.br/cadastro/img/logo2017.png':
                return driver
        except:
            print('FALHA AO REALIZAR LOGIN NO SISTEMA DE ATIVAÇÃO')
            exit()

def lista_olts(login, senha):
    # TODO: Verificar a possibilidade de refazer utilizando requests com a rotina http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados (Outras Verificações - Verificar ID/SN cadastrados.)

    print('Criando lista de OLTs... aguarde...')

    driver = sa_site_login(login, senha)

    driver.get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status")
    driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    lista = driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[2]/div')
    olts = lista.find_elements_by_class_name('option')

    create_olt_file()
    create_circuitos_file()

    for olt in olts:
        name = olt.text
        id = olt.get_attribute('data-value')

        print("OLT:{0}, id={1}".format(name, id))

        add_olt_to_file(name,id)

        interfaces = lista_interfaces(name, login, senha)
        if interfaces != None:
            for i in range(1,len(interfaces['nome'])):
                print("Interface:{0}, id={1}".format(interfaces['nome'][i], interfaces['id'][i]))
                add_slots_to_file(interfaces['nome'][i],interfaces['id'][i])
        else:
            print("Nenhuma interface cadasrada nessa OLT.")

        ## VERIFICA CIRCUITOS DA OLT
        add_olt_circuitos_to_file(name)
        circuitos = lista_circuito(name, login, senha)

        if circuitos != None:
            for i in range(0, len(circuitos['nome'])):
                print("Circuito:{0}, id={1}".format(circuitos['nome'][i], circuitos['id'][i]))
                add_circuito_to_file(circuitos['nome'][i], circuitos['id'][i])
        else:
            print("Nenhuma interface cadasrada nessa OLT.")
    quit(driver)

def lista_circuito(olt, login, senha):

    driver = sa_site_login(login, senha)

    driver.get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/verificar_sinal_circ")
    driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.BACKSPACE)
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(olt)
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.ENTER)
    try:
        driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/input').click()

        driver.find_element_by_xpath("/html/body/div/div/div[2]/table/tbody/tr/td/form/div/div[1]").click()
        circs = driver.find_elements_by_class_name('option')

        circuitos = {'nome':[],'id':[]}

        for circ in circs:
            circuitos['nome'].append(circ.text[10:])
            circuitos['id'].append(circ.get_attribute('data-value'))
    except:
        circuitos = None
    finally:
        quit(driver)

    return circuitos

def lista_interfaces(olt, login, senha):
    driver = sa_site_login(login, senha)

    driver.get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status")
    driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.BACKSPACE)
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(olt)
    driver.find_element_by_xpath('//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.ENTER)
    try:
        driver.find_element_by_xpath('/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/input').click()

        driver.find_element_by_xpath("//*[@id='centro']/form/div[1]/div[1]").click()
        slots = driver.find_elements_by_class_name('option')

        interfaces = {'nome':[],'id':[]}

        for slot in slots:
            interfaces['nome'].append(slot.text)
            interfaces['id'].append(slot.get_attribute('data-value'))
    except:
        interfaces = None
    finally:
        quit(driver)

    return interfaces

def quit(driver):
    # close webdriver
    driver.quit()
    driver = None

class OLTs:
    def __init__(self):
        self.config = configparser.ConfigParser()

        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.path = find_path()

        p = pathlib.Path(str(self.path) + 'olts.ini')
        if not p.exists():
            print('Lista de OLTs (olts.ini) não encontrada, execute o script novamente sem nenhum atributo e siga as instruções para criar a lista.')
            quit()

        self.config.read(str(self.path) + 'olts.ini')

    def get_olt_id(self, olt):
        if olt[:3] == 'OLT':
            olt_name = olt.upper()
        else:
            olt_name = 'OLT-GPON-{0}'.format(olt.upper())

        return self.config.get(olt_name,'id')

    def get_olt_slot_id(self, olt, slot):
        if olt[:3] == 'OLT':
            olt_name = olt.upper()
        else:
            olt_name = 'OLT-GPON-{0}'.format(olt.upper())

        if slot[:4] == 'gpon':
            olt_slot = slot
        else:
            olt_slot = 'gpon-olt_{0}'.format(slot)

        return self.config.get(olt_name,olt_slot)

    def get_olt_slots(self, olt):
        if olt[:3] == 'OLT':
            olt_name = olt
        else:
            olt_name = 'OLT-GPON-{0}'.format(olt)

        return self.config.items(olt_name)

    def get_olt_circuitos(self, olt):
        if olt[:3] == 'OLT':
            olt_name = 'CIRCUITOS-{0}'.format(olt)
        else:
            olt_name = 'CIRCUITOS-OLT-GPON-{0}'.format(olt)

        return self.config.items(olt_name)
