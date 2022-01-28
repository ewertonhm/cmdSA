from bs4 import BeautifulSoup
import httpx

LOCAL_VERSION = '2.12.1';

def get_online_version():
    try:
        soup = BeautifulSoup(httpx.get('https://github.com/ewertonhm/cmdSA/releases').text, 'lxml')
        div = soup.find('div', {"class": "Box-body"})
        online_version = div.find('a').text
        if online_version != LOCAL_VERSION:
            print(
                "Uma nova versão do script está disponível para baixar em: https://github.com/ewertonhm/cmdSA/releases")
    except Exception as e:
        print("Não foi possível verificar se existem atualizações disponíveis")

