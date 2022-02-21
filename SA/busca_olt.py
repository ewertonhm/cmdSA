import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import configparser
import pathlib
import inspect
from conf.configs import find_path
from tqdm import tqdm

__DRIVER = []

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
    s = Service(filename)

    print('aguarde...')
    options = selenium.webdriver.chrome.options.Options()
    options.headless = False
    options.add_argument('log-level=3')
    #options.setPageLoadStrategy(PageLoadStrategy.NONE);
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])


    # path do webdriver, o mesmo pode ser baixado em: https://chromedriver.chromium.org/downloads
    __DRIVER.append(webdriver.Chrome(service=s, options=options))

def sa_site_login(login, senha):
    logo = None
    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/index.php")
    print('Realizando Login no sistema de ativação...')
    __DRIVER[0].find_element(By.NAME, "login").send_keys(login)
    __DRIVER[0].find_element(By.NAME, "senha").send_keys(senha)
    __DRIVER[0].find_element(By.ID, "entrar").click()
    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php")

    try:
        logo = __DRIVER[0].find_element(By.ID, "centro").find_element(By.TAG_NAME, "img").get_attribute("src")
    except:
        __DRIVER[0].find_element(By.NAME, "login").send_keys(login)
        __DRIVER[0].find_element(By.NAME, "senha").send_keys(senha)
        __DRIVER[0].find_element(By.ID, "entrar").click()

    if logo == 'http://ativacaofibra.redeunifique.com.br/cadastro/img/logo2017.png':
        print('Login realizado com sucesso...')
        return True
    else:
        try:
            logo = __DRIVER[0].find_element(By.ID, "centro").find_element(By.TAG_NAME, "img").get_attribute("src")
            if logo == 'http://ativacaofibra.redeunifique.com.br/cadastro/img/logo2017.png':
                print('Login realizado com sucesso...')
                return True
        except:
            print('FALHA AO REALIZAR LOGIN NO SISTEMA DE ATIVAÇÃO')
            exit()

def lista_olts():
    # TODO: Verificar a possibilidade de refazer utilizando requests com a rotina http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados (Outras Verificações - Verificar ID/SN cadastrados.)

    print('Criando lista de OLTs... aguarde...')

    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status")
    __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    lista = __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[2]/div')
    olts = lista.find_elements(By.CLASS_NAME, 'option')
    data = {'name': [], 'id': []}
    for olt in olts:
        data['name'].append(olt.text)
        data['id'].append(olt.get_attribute('data-value'))

    create_olt_file()
    create_circuitos_file()

    olt_count = len(data['name'])

    for i in tqdm(range(0, olt_count), unit='olt'):
        name = data['name'][i]
        id = data['id'][i]

        #print("OLT:{0}, id={1}".format(name, id))

        add_olt_to_file(name,id)

        ci = lista_circuitos_interfaces(name)

        if ci['interfaces'][0] != None:
            for i in range(0, len(ci['interfaces'][0]['nome'])):
                #print("Interface:{0}, id={1}".format(ci['interfaces'][0]['nome'][i], ci['interfaces'][0]['id'][i]))
                add_slots_to_file(ci['interfaces'][0]['nome'][i], ci['interfaces'][0]['id'][i])


        add_olt_circuitos_to_file(name)

        if ci['circuitos'][0] != None:
            for i in range(0, len(ci['circuitos'][0]['nome'])):
                #print("Circuito:{0}, id={1}".format(ci['circuitos'][0]['nome'][i], ci['circuitos'][0]['id'][i]))
                add_circuito_to_file(ci['circuitos'][0]['nome'][i], ci['circuitos'][0]['id'][i])

        ''' OLD
        interfaces = lista_interfaces(name)
        if interfaces != None:
            for i in range(1,len(interfaces['nome'])):
                print("Interface:{0}, id={1}".format(interfaces['nome'][i], interfaces['id'][i]))
                add_slots_to_file(interfaces['nome'][i],interfaces['id'][i])
        else:
            print("Nenhuma interface cadasrada nessa OLT.")
        ## VERIFICA CIRCUITOS DA OLT
        add_olt_circuitos_to_file(name)
        circuitos = lista_circuito(name)
        if circuitos != None:
            for i in range(0, len(circuitos['nome'])):
                print("Circuito:{0}, id={1}".format(circuitos['nome'][i], circuitos['id'][i]))
                add_circuito_to_file(circuitos['nome'][i], circuitos['id'][i])
        else:
            print("Nenhuma interface cadasrada nessa OLT.")
        '''

    quit(__DRIVER[0])

def lista_circuito(olt):

    #driver = sa_site_login(login, senha)

    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/verificar_sinal_circ")
    __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.BACKSPACE)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(olt)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.ENTER)
    try:
        __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/input').click()

        __DRIVER[0].find_element(By.XPATH, "/html/body/div/div/div[2]/table/tbody/tr/td/form/div/div[1]").click()
        circs = __DRIVER[0].find_elements(By.CLASS_NAME, 'option')

        circuitos = {'nome':[],'id':[]}

        for circ in circs:
            circuitos['nome'].append(circ.text[10:])
            circuitos['id'].append(circ.get_attribute('data-value'))
    except:
        circuitos = None

    return circuitos

def lista_interfaces(olt):
    #driver = sa_site_login(login, senha)

    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=verificacoes_onu/status")
    __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.BACKSPACE)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(olt)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.ENTER)
    try:
        __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/input').click()

        __DRIVER[0].find_element(By.XPATH, "//*[@id='centro']/form/div[1]/div[1]").click()
        slots = __DRIVER[0].find_elements(By.CLASS_NAME, 'option')

        interfaces = {'nome':[],'id':[]}

        for slot in slots:
            interfaces['nome'].append(slot.text)
            interfaces['id'].append(slot.get_attribute('data-value'))
    except:
        interfaces = None

    return interfaces

def lista_circuitos_interfaces(olt):
    __DRIVER[0].get("http://ativacaofibra.redeunifique.com.br/cadastro/interno.php?pg=interno&pg1=outras_verificacoes/ids_cadastrados")
    __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]').click()
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.BACKSPACE)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(olt)
    __DRIVER[0].find_element(By.XPATH, '//*[@id="centro"]/table/tbody/tr/td[1]/form/div/div[1]/input').send_keys(Keys.ENTER)

    data = {"interfaces":[],"circuitos":[]}
    interfaces = ''
    circuitos = ''

    try:
        __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/input').click()
    except Exception as e:
        print(e)

    # interfaces
    try:
        __DRIVER[0].find_element(By.XPATH, "/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[1]").click()
        slots = __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[1]/form/div/div[2]/div').find_elements(By.CLASS_NAME, 'option')

        interfaces = {'nome': [], 'id': []}

        for slot in slots:
            interfaces['nome'].append(slot.text)
            interfaces['id'].append(slot.get_attribute('data-value'))

        __DRIVER[0].find_element(By.XPATH, "/html/body/div/div/div[2]/h2").click()

    except Exception as e:
        #print(e)
        #print("erro ao consultar interfaces da olt {0}, verificar se existem interfaces nessa olt".format(olt))
        interfaces = None
    finally:
        data['interfaces'].append(interfaces)

    # circuitos
    try:
        __DRIVER[0].find_element(By.XPATH, "/html/body/div/div/div[2]/table/tbody/tr/td[2]/form/div/div[1]").click()
        circs = __DRIVER[0].find_element(By.XPATH, '/html/body/div/div/div[2]/table/tbody/tr/td[2]/form/div/div[2]/div').find_elements(By.CLASS_NAME, 'option')

        circuitos = {'nome': [], 'id': []}

        for circ in circs:
            circuitos['nome'].append(circ.text[10:])
            circuitos['id'].append(circ.get_attribute('data-value'))
    except Exception as e:
        #print(e)
        #print("erro aconteceu ao consultar circuitos da olt {0}, verificar se existem circuitos nessa olt".format(olt))
        circuitos = None
    finally:
        data['circuitos'].append(circuitos)

    return data

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