import httpx
from bs4 import BeautifulSoup
from console_theme import *
from rich.table import Table


class NetBox:
    LOGIN_PAGE = 'http://netbox.cgr.unifique.net/login/?next=/'
    SEARCH_ADDRESS = 'http://netbox.cgr.unifique.net/search/?q='

    def __init__(self, usuario, senha):
        self.session = httpx.Client()
        soup = BeautifulSoup(self.session.get(self.LOGIN_PAGE).text, 'lxml')
        token = soup.find("input", {"name":"csrfmiddlewaretoken"})['value']

        post = {"csrfmiddlewaretoken":token, "next":"/","username":usuario,"password":senha}
        try:
            logged = BeautifulSoup(self.session.post(self.LOGIN_PAGE,data=post).text, 'lxml')
            logged = logged.find("div", {"class":"alert-dismissable"}).text
        except Exception:
            print('Falha no login')

        if not logged.find('Logged'):
            print('Falha no login')
            quit()


    def search_ip(self,ip):
        address = self.SEARCH_ADDRESS + ip
        soup = BeautifulSoup(self.session.get(address).text, 'lxml')
        results = soup.find_all("a", {"class":"list-group-item"})

        items = soup.find("div", {"class":"col-md-10"})

        Results = {}
        for result in results:
            Results[str(result.text).strip().splitlines()[0]] = int(str(result.text).strip().splitlines()[1][-1:])
        '''
        if Results['Aggregates'] > 0:
            td = items.find('th', text='Aggregate')
            table = td.parent.parent.parent
            list = table.find_all('td')
            print('Aggregates|' + list[0].text + '|' + list[4].text)
        '''
        if Results['Prefixes'] > 0:
            td = items.find('th', text='Prefix')
            table = td.parent.parent.parent
            body = table.find('tbody')
            lines = body.find_all('tr')

            t = Table(title=ip + ' Prefixes')
            t.add_column('Prefix')
            t.add_column('Site')
            t.add_column('VLAN')
            t.add_column('Role')
            t.add_column('Description')

            for line in lines:
                t.add_row(str(line.find_all('td')[0].text).strip(),str(line.find_all('td')[4].text).strip(),str(line.find_all('td')[5].text).strip(),str(line.find_all('td')[6].text).strip(),str(line.find_all('td')[7].text).strip())
            CONSOLE.print(t)

        if Results['IP Addresses'] > 0:
            td = items.find('th', text='IP Address')
            table = td.parent.parent.parent
            body = table.find('tbody')
            lines = body.find_all('tr')

            t = Table(title=ip + ' IP Addresses')
            t.add_column('IP ADDress')
            t.add_column('Role')
            t.add_column('DNS Name')
            t.add_column('Description')

            for line in lines:
                t.add_row(str(line.find_all('td')[0].text).strip(),str(line.find_all('td')[5].text).strip(),str(line.find_all('td')[7].text).strip(),str(line.find_all('td')[8].text).strip())
            CONSOLE.print(t)

