import base64
import configparser
import csv
import smtplib
import urllib.request

from bs4 import BeautifulSoup

cp = configparser.ConfigParser()
cp.read('config.ini')
gmail_user = cp.get('config', 'username')
gmail_password = str(base64.b64decode(cp.get('config', 'password'))).strip('\'').replace('b\'', '')
to = cp.get('config', 'to')
urls = cp.get('config', 'urls').split(',')


def send_email():
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(gmail_user, gmail_password)
        email_text = """\
From: %s
Subject: %s

%s""" % ("Novos Episódios", "%s - %s" % (nomeEP, titulo), "Acesse: %s" % hrefEP)
        server.sendmail(gmail_user, to, email_text.encode("utf-8"))
        print('email')


def escrever_arquivo():
    print('Escrever arquivo')
    with open('lastEp-%s.csv' % pathSerie, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["URL"])
        writer.writerow([hrefEP])


for urlSerie in urls:
    pathSerie = urlSerie.split('/')[-1]
    request = urllib.request.Request(
        url=urlSerie,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    html = urllib.request.urlopen(request)
    soup = BeautifulSoup(html, 'html.parser')
    listaEp = soup.find_all("div", {"class": 'lista-episodios'})
    titulo = soup.find_all("div", {"class": 'titulo-page'})[-1].text
    print(titulo)
    nomeEP = listaEp[-1].find_all("span", {"class": 'nome'})[-1].text
    hrefEP = listaEp[-1].find_all("a", {"href": True})[-1]['href']

    try:
        with open('lastEp-%s.csv' % pathSerie) as file:
            reader = csv.reader(file)
            next(reader)
            line = next(reader)
            if line[0] != hrefEP:
                try:
                    send_email()
                    escrever_arquivo()
                except:
                    print('Something went wrong...')
            else:
                escrever_arquivo()

    except (OSError, IndexError) as e:
        send_email()
        escrever_arquivo()
