"""
ici sont rassemblées toutes les fonctions utilitaires
"""

import os
import re
import requests
from requests_html import HTMLSession
from zipfile import ZipFile
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import pickle
from datetime import date, timedelta


# ------ quelques fonctions statiques ------
def get_datas(my_file, data):
    """ fonction qui récupère les données d'un fichier s'il existe et qui le crée sinon """
    try:
        with open(my_file, "rb") as file:
            get_data = pickle.Unpickler(file)
            result = get_data.load()
            return result
    except (FileNotFoundError, EOFError):   # EOFError concerne les fichiers existants mais vides
        save_datas(my_file, data)


def save_datas(my_file, data):
    """ fonction qui enregistre les données dans un fichier externe """
    with open(my_file, "wb") as file:
        write_data = pickle.Pickler(file)
        write_data.dump(data)
        return data


def get_higher(data):
    """ retour du plus haut d'une liste de listes si elle n'est pas vide, sinon plus haut de l'historique """
    try:
        maxi = [element[3] for element in data]  # liste pour récupérer tous les plus hauts quotidiens à l'index[3]
        if len(maxi) != 0:
            return max(maxi)  # on retourne le plus haut
        return "Pas de nouveau plus haut identifié."
    except NameError:
        return "Exception levée : la liste est peut-être vide !"


def reformate_data(data):
    """ reformatage des données et conversion du type string vers float """
    return float(data.replace(".", "").replace(",", "."))


def buy_limit(value, target, leverage):
    """fonction qui calcule un objectif cible en pourcentage ajusté d'un levier"""
    return round(value - (((value * target) / 100) * leverage), 2)


def reformate_datetime(data, deadline=None):
    """fonction qui renvoie les dates dans un format unique"""
    if isinstance(data, date):
        if deadline is not None:
            data = data + timedelta(days=deadline)
        my_month = data.month
        my_day = data.day
        if my_month < 10:
            my_month = f"0{my_month}"
        if my_day < 10:
            my_day = f"0{my_day}"
        return f"{my_day}/{my_month}/{data.year}"
    if isinstance(data, str):
        data = data.split("/")
        date_object = date(int(data[2]), int(data[1]), int(data[0]))
        if deadline is not None:
            date_object = date_object + timedelta(days=deadline)
        my_month = date_object.month
        my_day = date_object.day
        if my_month < 10:
            my_month = f"0{my_month}"
        if my_day < 10:
            my_day = f"0{my_day}"
        return f"{my_day}/{my_month}/{date_object.year}"


def set_delta(high_cac, MY_LAST_HIGH, high_lvc):
    """fonction qui calcule le prix d'un actif à effet de levier par rapport à son sous-jacent"""
    if high_cac > MY_LAST_HIGH:
        delta = abs(((MY_LAST_HIGH * 100) / high_cac) - 100) * 2
        lvc = high_lvc - ((high_lvc * delta) / 100)
    else:
        delta = abs(((high_cac * 100) / MY_LAST_HIGH) - 100) * 2
        lvc = abs(high_lvc + ((high_lvc * delta) / 100))
    return lvc


def driver_update():
    """fonction qui met à jour le chromedriver en lien avec la version du navigateur"""

    # on vérifie le numéro de version de chrome
    # TODO : la question est de savoir si le webdriver se lancera lorsque l'exception sera levée...
    options = Options()
    options.headless = True
    with Chrome(executable_path="chromedriver.exe", options=options) as driver:
        if 'browserVersion' in driver.capabilities:
            version = driver.capabilities['browserVersion'].split(".")[0]
            print(f"le numéro de version de chrome est {version}")  # 92
        else:
            print(driver.capabilities['version'])

    # on fait une requête pour récupérer le numéro de version du dernier chromedriver
    url = "http://chromedriver.chromium.org/downloads"

    # on fetch l'url que l'on traite comme une string que l'on split à chaque fin de ligne (ici du JS, donc ";")
    response = requests.get(url).text.split(";")

    # on passe toutes les lignes en revue pour lister toutes les occurences d'une classe CSS
    target = 'class="XqQF9c"'
    link = [row for row in response if target in row]

    # on itère la liste pour trouver une correspondance avec le numéro de version actuel de chromium
    current_version = [row for row in link if version in row][0]

    # on crée une regex pour en rechercher la première occurence (l'url de la dernière version du chromedriver)
    regex = re.search("https://.+path=[0-9.]+/", current_version).group()
    print(f"le regex me renvoie {regex}")  # https://chromedriver.storage.googleapis.com/index.html?path=92.0.4515.107/

    # je relance une requête sur l'url regex, cette fois avec le module requests-html qui permet d'exécuter le code JS
    session = HTMLSession()
    response = session.get(regex)

    # on appelle la méthode render() afin d'exécuter le javascript de la page
    response.html.render(sleep=2, timeout=8)

    # on récupère le premier élément de la liste renvoyée par la méthode xpath()
    url = response.html.xpath("/html/body/table/tbody/tr[7]/td[2]/a")[0]

    # on extrait le href de l'élément précédent
    url = url.absolute_links

    # on convertit le set 'result' en liste pour en extraire le premier élément
    url = list(url)[0]
    print(
        f"l'url de téléchargement est {url}"
    )  # https://chromedriver.storage.googleapis.com/93.0.4577.15/chromedriver_win32.zip

    # on fait une requête vers le fichier distant
    response = session.get(url)

    # on enregistre localement l'archive zippée
    save_datas('chromedriver.zip', response)

    # on supprime la version obsolète de 'chromedriver.exe' pour éviter les conflits de namespace
    if os.path.isfile('chromedriver.exe'):
        os.remove('chromedriver.exe')
    else:
        print("impossible d'effacer le fichier 'chromedriver.exe : fichier introuvable")

    # on extrait le fichier chromedriver de l'archive zippée dans le répertoire courant
    with ZipFile('chromedriver.zip', 'r') as zipped_file:
        zipped_file.extract('chromedriver.exe')

    # on supprime l'archive après l'extraction du chromedriver
    if os.path.isfile('chromedriver.zip'):
        os.remove('chromedriver.zip')
    else:
        print("impossible d'effacer le fichier 'chromedriver.zip : ce fichier n'existe pas")
