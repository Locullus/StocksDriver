"""Ici sont réunies toutes les classes et fonctions utiles au programme principal"""

import pickle
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
    except FileNotFoundError:
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
        maxi = [element[3] for element in data]     # liste pour récupérer tous les plus hauts quotidiens à l'index[3]
        if len(maxi) != 0:
            return max(maxi)                            # on retourne le plus haut
        else:
            return "Pas de nouveau plus haut identifié."
    except NameError:
        return "Exception levée : la liste est peut-être vide !"


def reformate_data(data):
    """ reformatage des données et conversion du type string vers float """
    return float(data.replace(".", "").replace(",", "."))


def buy_limit(value, target, leverage):
    """fonction qui calcule un objectif cible en pourcentage ajusté d'un levier"""
    return round(value - (((value * target) / 100) * leverage), 2)


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
        with Chrome(executable_path=r"C:\Users\bin\chromedriver.exe", options=self.options) as self.driver:
            if self.loop == "loop":
                try:
                    self.driver.get(self.url)
                    self.driver.implicitly_wait(2)
                    self.datas = self.parsing_method()
                except WebDriverException:
                    print("Problème avec le WebDriver, vérifiez la connnexion.")
            else:
                try:
                    self.driver.get(self.url)
                    self.driver.implicitly_wait(2)
                    self.datas = self.parse_array(self.x_path, self.index1, self.index2)
                except WebDriverException:
                    print("Problème avec le WebDriver, vérifiez la connnexion.")

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
        self.date = my_date
        self.sign = sign
        self.quantity = quantity
        self.stock = stock
        self.price = price
        self.px = px
        self.deadline = deadline

    def check_position(self, last_low_px1):
        """fonction qui vérifie si une position attend d'être prise"""
        if self.sign == "+":
            print("Cette position n'a pas encore été ouverte, elle attend que les cours la touchent.")
        else:
            print("Cette position est ouverte et attend que les cours atteignent son objectif pour être soldée.")
        if self.px >= last_low_px1:
            print("Le cours a été touché, la position est passée !")
            print("Il faut maintenant créer une nouvelle instance, de vente cette fois.")
