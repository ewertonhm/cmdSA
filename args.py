import argparse

class Argumentos:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Verifica status dos circuitos no Sistema de Ativação.\r\n Criado por Ewerton H. Marschalk')
        self.parser.add_argument('-c', '--circuito', nargs='+')
        self.parser.add_argument('-p', '--pppoe', nargs='+')
        self.parser.add_argument('-ca', '--caixa_atendimento', nargs='+')
        args = self.parser.parse_args()

        # recuperando parâmetros
        self.Circuitos = args.circuito
        self.Logins = args.pppoe
        self.CAs = args.caixa_atendimento

    def getCircuitos(self):
        return self.Circuitos

    def getLogins(self):
        return self.Logins

    def getCAs(self):
        return self.CAs