
from Database import mongodb
from pprint import pprint

class BuscaCircuito:
    def __init__(self):
        db = mongodb.get_database()
        self.collection = db['olts']

    def search_circuit(self, param):
        """
        Procura na lista de circuitos quais se encaixam com os termos digitados e retorna uma lista com os mesmos
        :param param: String, parametro de pesquisa
        :return: Lista, lista com os restultados
        """

        query = [
                    {
                        '$match': {
                            'circuitos': {
                                '$elemMatch': {
                                    'nome': {
                                        '$regex': f'.*{param}.*'
                                    }
                                }
                            }
                        }
                    }, {
                        '$unwind': {
                            'path': '$circuitos'
                        }
                    }, {
                        '$project': {
                            '_id': 0,
                            'circuito': '$circuitos.nome',
                            'id': '$circuitos.id'
                        }
                    }, {
                        '$match': {
                            'circuito': {
                                '$regex': f'.*{param}.*'
                            }
                        }
                    }
                ]



        result = self.collection.aggregate(query)

        return result