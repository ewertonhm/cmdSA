import argparse

class Argumentos:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Cliente CMD para o Sistema de Ativação.\r\n Criado por Ewerton H. Marschalk')
        self.parser.add_argument('-c', '--circuito', nargs='+')
        self.parser.add_argument('-p', '--pppoe', nargs='+')
        self.parser.add_argument('-ca', '--caixa_atendimento', nargs='+')
        self.parser.add_argument('-ip', '--ip', nargs='+')
        self.parser.add_argument('-sn', '--serial', nargs='+')
        self.parser.add_argument('-o', '--olt', nargs='+')
        self.parser.add_argument('-i', '--interface', nargs='+')
        self.parser.add_argument('-a', '--ativacao', nargs='+')
        self.parser.add_argument('-all', '--all_circuitos', nargs='+')
        self.parser.add_argument('-cod', '--codigo', nargs='+')
        self.parser.add_argument('-sc', '--sinalcircuito', nargs='+')
        self.parser.add_argument('-sca', '--sinalcaixa', nargs='+')
        args = self.parser.parse_args()

        # recuperando parâmetros
        self.Circuitos = args.circuito
        self.Logins = args.pppoe
        self.CAs = args.caixa_atendimento
        self.IPs = args.ip
        self.SNs = args.serial
        self.OLT = args.olt
        self.Interfaces = args.interface
        self.ATV = args.ativacao
        self.All = args.all_circuitos
        self.Codigos = args.codigo
        self.Sinais = args.sinalcircuito
        self.SinaisCaixa = args.sinalcaixa

    def getCircuitos(self):
        return self.Circuitos

    def getLogins(self):
        return self.Logins

    def getCAs(self):
        return self.CAs

    def getIPs(self):
        return self.IPs

    def getSNs(self):
        return self.SNs

    def getOLT(self):
        return self.OLT

    def getInterfaces(self):
        return self.Interfaces

    def getAtivacao(self):
        return self.ATV

    def getAllCircuitos(self):
        return self.All

    def getCodigos(self):
        return self.Codigos

    def getSinais(self):
        return self.Sinais

    def getSinaisCaixa(self):
        return self.SinaisCaixa
