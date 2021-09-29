from bs4 import BeautifulSoup
import httpx

LOCAL_VERSION = '2.7.1'

def get_online_version():
    soup = BeautifulSoup(httpx.get('https://github.com/ewertonhm/cmdSA/releases').text, 'lxml')
    div = soup.find('div', {"class": "release-header"})
    online_version = div.find('a').text
    if online_version != LOCAL_VERSION:
        print("Uma nova versão do script está disponível para baixar em: https://github.com/ewertonhm/cmdSA/releases")