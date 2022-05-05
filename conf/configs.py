from Cryptodome.Cipher import AES
import configparser
import pathlib
import inspect
import os
import sys
import base64
import getpass
import dload
from Database import mongodb

db = mongodb.get_database()
db_collecion = db['configs']

confs = db_collecion.find_one()
LOCAL_VERSION = '3.12'
LAST_VERSION = confs['version']
secret_key = confs['secret'].encode('utf-8')


def check_updates():
    if LOCAL_VERSION != LAST_VERSION:
        print("Uma nova versão do script está disponível para baixar em: https://github.com/ewertonhm/cmdSA/releases")


def download_chromedriver():
    return dload.save_unzip(
        'https://chromedriver.storage.googleapis.com/95.0.4638.69/chromedriver_win32.zip',
        extract_path=find_path(),
        delete_after=True
    )


def find_path():
    filename = sys.argv[0]
    pythonpath = sys.executable

    path = ''

    if os.path.split(sys.argv[0])[1][-2:] == 'py':
        path = sys.executable[0:-23]
    else:
        if filename[-3:] == 'exe':
            path = pythonpath[:-len(filename)]
        else:
            path = pythonpath[:-(len(filename)+4)]
    return path


def read_file(file_name):
    f = open(file_name, 'r')
    values = f.readlines()
    return values


def write_to_file(string):
    path = find_path()
    filename = path + 'credentials.ini'
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


def add_to_file_sa_credentials(login, senha):
    write_to_file('[credentials-sa]')
    write_to_file('Login:' + login)

    msg_text = bytes(senha, 'utf-8').rjust(32)

    # never use ECB in strong systems obviously
    cipher = AES.new(secret_key, AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(msg_text))

    write_to_file('Senha:' + encoded.decode('utf-8'))


def add_to_file_erp_credentials(login, senha):
    write_to_file('[credentials-erp]')
    write_to_file('Login:' + login)

    msg_text = bytes(senha, 'utf-8').rjust(32)

    # never use ECB in strong systems obviously
    cipher = AES.new(secret_key, AES.MODE_ECB)
    encoded = base64.b64encode(cipher.encrypt(msg_text))

    write_to_file('Senha:' + encoded.decode('utf-8'))


class Credentials:
    def __init__(self):
        self.config = configparser.ConfigParser()

        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.path = find_path()

        p = pathlib.Path(str(self.path) + 'credentials.ini')
        if not p.exists():
            print('Durante a execução, desse script, o mesmo irá logar no sistema de ativação para realizar consultas;')
            print(
                "Para prosseguir, digite o seu usuário e senha do sistema de ativação; ")
            usr = input('Digite o usuário do sistema de ativação (Email):')
            # TODO: utilizar getpass
            pwd = getpass.getpass('Digite a senha:')
            p.touch()
            add_to_file_sa_credentials(usr, pwd)

        self.config.read(str(self.path) + 'credentials.ini')

    def getLogin(self):
        return self.config.get('credentials-sa', 'Login')

    def getSenha(self):
        cipher = AES.new(secret_key, AES.MODE_ECB)
        password = cipher.decrypt(base64.b64decode(
            self.config.get('credentials-sa', 'Senha').encode('utf-8')))
        password = password.decode('utf-8')
        password = password.strip()
        return password

    def ask_erp_credentials(self):
        print('Durante a execução, desse script, o mesmo irá logar no ERP para realizar consultas;')
        print("Para prosseguir, digite o seu usuário e senha do Bemtivi; ")
        usr = input('Digite o usuário do Bemtivi:')
        # TODO: utilizar getpass
        pwd = getpass.getpass('Digite a senha:')
        add_to_file_erp_credentials(usr, pwd)
        self.config.read(str(self.path) + 'credentials.ini')

    def check_erp_credentials(self):
        try:
            self.config.get('credentials-erp', 'Login')
        except:
            self.ask_erp_credentials()

    def getErpLogin(self):
        return self.config.get('credentials-erp', 'Login')

    def getErpSenha(self):
        cipher = AES.new(secret_key, AES.MODE_ECB)
        password = cipher.decrypt(base64.b64decode(
            self.config.get('credentials-erp', 'Senha').encode('utf-8')))
        password = password.decode('utf-8')
        password = password.strip()
        return password
