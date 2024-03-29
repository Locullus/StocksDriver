"""Ici sont réunies toutes les classes et fonctions utiles au programme principal"""

import pickle
from datetime import date, timedelta
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


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


# ------ configuration de la classe WebDriver ------
class WebDriver:
    """ classe qui configure le webDriver pour récupérer des données par leur xpath """

    def __init__(self, url, x_path, index1, index2, loop=None, last_saved_date=None):
        self.url = url
        self.x_path = x_path
        self.index1 = index1
        self.index2 = index2
        self.loop = loop
        self.last_saved_date = last_saved_date
        self.options = Options()
        self.options.headless = True
        self.options.page_load_strategy = 'normal'

        # ATTENTION : l'argument 'executable_path' doit pointer vers l'exécutable du webdriver installé
        # TODO : il faudra insérer ce gestionnaire de contexte dans un bloc try lorsqu'on connaîtra l'exception levée
        # TODO : on créera alors une fonction pour la mise à jour du ChromeDriver puis une relance de celui-ci
        with Chrome(executable_path=r"C:\Users\bin\chromedriver.exe", options=self.options) as self.driver:
            try:
                if self.loop == "loop":
                    self.driver.get(self.url)
                    self.driver.implicitly_wait(2)
                    self.datas = self.parsing_method()
                else:
                    self.driver.get(self.url)
                    self.driver.implicitly_wait(2)
                    self.datas = self.parse_array(self.x_path, self.index1, self.index2)
            except WebDriverException:
                print("Problème avec le WebDriver, vérifiez la connection.")

    def parsing_method(self):
        """ fonction qui détermine le nombre de lignes à scraper et la boucle utilisée """
        try:
            self.driver.find_element_by_class_name("redClockBigIcon")
            nb = 1
        except NoSuchElementException:
            print("Marché ouvert : les données du jour ne seront donc pas sauvegardées car encore incomplètes.")
            nb = 2
        if self.last_saved_date != "0":
            my_list = self.while_loop(nb)
        else:
            my_list = self.for_loop(nb)
        return my_list

    def while_loop(self, i):
        """ fonction qui collecte les données avec une boucle while """
        my_list = []
        last_date = self.parse_array(self.x_path, i, 1)
        while last_date != self.last_saved_date and i < 22:
            last_date = self.parse_array(self.x_path, i, 1)
            last = self.parse_array(self.x_path, i, 2)
            last = reformate_data(last)
            opening = self.parse_array(self.x_path, i, 3)
            opening = reformate_data(opening)
            higher = self.parse_array(self.x_path, i, 4)
            higher = reformate_data(higher)
            lower = self.parse_array(self.x_path, i, 5)
            lower = reformate_data(lower)
            my_list.append([last_date, last, opening, higher, lower])
            last_date = self.parse_array(self.x_path, i + 1, 1)
            i += 1
        return my_list

    def for_loop(self, nb):
        """ fonction qui collecte les données avec une boucle for """
        my_list = []
        for i in range(nb, 22):
            last_date = self.parse_array(self.x_path, i, 1)
            last = self.parse_array(self.x_path, i, 2)
            last = reformate_data(last)
            opening = self.parse_array(self.x_path, i, 3)
            opening = reformate_data(opening)
            higher = self.parse_array(self.x_path, i, 4)
            higher = reformate_data(higher)
            lower = self.parse_array(self.x_path, i, 5)
            lower = reformate_data(lower)
            my_list.append([last_date, last, opening, higher, lower])
        print("La boucle for a retouné : " + str(len(my_list)))
        return my_list

    def parse_array(self, x_path, index1, index2):
        """ méthode qui récupère les valeurs du CAC dans le DOM de la page """
        return self.driver.find_element_by_xpath(x_path.format(str(index1), str(index2))).text


# ------ classe qui gère les positions ------
class Position:
    """classe qui gère les positions à prendre ou à solder"""

    def __init__(self, name, my_date, sign, quantity, stock, price, px, deadline):
        self.name = name
        self.date = reformate_datetime(my_date)
        self.sign = sign
        self.quantity = quantity
        self.stock = stock
        self.price = price
        self.px = px
        self.deadline = deadline

    def check_position(self, list_data):
        """fonction qui vérifie si une position a été exécutée"""
        my_list = []

        # dans un premier temps on récupère dans une liste toutes les données disponibles depuis le dernier ordre passé
        # la liste est classée dans l'ordre chronologique
        # on sort de la boucle dès que la date du dernier ordre est rencontrée
        for element in list_data:
            if element[0] != self.date:
                my_list.insert(0, element)
            else:
                break

        # dans un second temps on vérifie si prix de l'élément de liste précèdente <= prix de la position pour 2 cas :
        # cas 1 : la position attend d'être passée
        if self.sign == "+":
            for element in my_list:
                if float(element[4]) <= self.price:
                    print(f"le niveau a été touché sur le cours de {element[4]} au prix de {self.price} sur le lvc.")
                    self.date = element[0]
                    self.deadline = reformate_datetime(self.date, 90)
                    self.px *= 1.05
                    self.price *= 1.1
                    self.sign = "-"
                    return \
                        self.name, self.date, self.sign, self.quantity, self.stock, self.price, self.px, self.deadline
            print("La position n'a pas encore été prise.")
            return self.name, self.date, self.sign, self.quantity, self.stock, self.price, self.px, self.deadline

        # cas 2 : la position attend d'être soldée
        if self.sign == "-":
            for element in my_list:
                if float(element[4]) >= self.price:
                    print(f"La position a été soldée sur le cours de {element[4]} au prix de {self.price}.")
                print("La position n'a pas encore été soldée.")


"""
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: 
This version of ChromeDriver only supports Chrome version 89
Current browser version is 91.0.4472.77 with binary path C:
\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe

Lors de la levée de cette exception il faut charger le chrome driver correspondant à la version de Chrome.
Le chromedriver peut être chargé à cette adresse : "https://chromedriver.chromium.org/"
Il faut sélectionner la dernière version stable et la sauvegarder ici : "C:/Users/bin/chromedriver.exe"

On pourra automatiser ce processus en utilisant selenium et le xpath de cette version stable.
Il faudra créer une fonction qui se connectera à l'adresse et installera le nouveau driver pour ensuite relancer
le programme une fois l'exception gérée.
"""
