import busca_olt
from configs import find_path
import configparser
import pathlib
import inspect

class BuscaCircuito:
    def __init__(self):
        self.config = configparser.ConfigParser()

        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.path = find_path()

        p = pathlib.Path(str(self.path) + 'circuitos.ini')
        if not p.exists():
            print('Lista de Circuitos (circuitos.ini) não encontrada, execute o script novamente sem nenhum atributo e siga as instruções para criar a lista.')
            quit()

        # for debbuging:
        #self.config.read('circuitos.ini')

        self.config.read(str(self.path) + 'circuitos.ini')

    def search_circuit(self, param):
        """
        Procura na lista de circuitos quais se encaixam com os termos digitados e retorna uma lista com os mesmos
        :param param: String, parametro de pesquisa
        :return: Lista, lista com os restultados
        """
        circuitos = self.config.items('circuitos')
        circ = []
        for c in circuitos:
            circ.append(c[0].upper())

        result = list(filter(lambda x: param.upper() in x, circ))
        return result

