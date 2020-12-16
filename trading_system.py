"""
    Ce programme de trading récupère les dernières données disponibles sur le net pour construire un historique
    du CAC et déterminer les niveaux d'interventions à l'achat et la vente sur un tracker du CAC, le LVC.
    Le LVC réplique les mouvements du CAC avec un levier x2. Dès lors, en rapportant les dernières données de l'indice
    et du tracker aux données historiques du CAC, le programme va être capable de fixer des objectifs relativement
    au dernier point haut significatif.
    Le dernier point haut significatif est rétrospectivement fixé par une chute des cours de 300 points : c'est cette
    chute qui met en lumière à la fois le dernier point haut et le premier niveau d'achat.
    Quand ce niveau est touché, un ordre est passé et un niveau de revente calculé. En outre, un second niveau d'achat
    est proposé 100 points sous le premier. Les positions vont ainsi s'accumuler jusqu'au renversement de la tendance.
    Les positions prises seront alors progressivement débouclées.
    Si une position est vendue elle sera reprise 300 points plus bas. Dans ce cas un nouveau plus haut local sera
    considéré comme ayant été atteint. Toutes les positions encore engagées relativement au plus haut local précédent
    attendront tranquillement d'être dénouées.
    Le programme considère qu'un nouveau point haut local a été atteint soit parce que l'indice a retracé 300 points,
    soit parce que le plus haut local a été dépassé par l'indice.
    """

# ------ importation des modules ------
import pickle

from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

# ------ affectation de la valeur et de la date du premier point haut local ------
MY_LAST_HIGH = 5555.83
MY_LAST_DATE = "23/11/2020"

# ------ déclaration des url des xpath des données à scraper ------
cac_url = 'https://www.boursorama.com/bourse/indices/cours/1rPCAC/'
cac_x_path = '//*[@id="main-content"]/div/section[1]/div[2]/article/div[1]/div[2]/div[1]/div[5]/' \
             'div[2]/div[1]/div/div/table/tbody/tr[{}]/td[{}]'

lvc_url = 'https://www.boursorama.com/bourse/trackers/cours/1rTLVC/'
lvc_x_path = '//*[@id="main-content"]/div/section[1]/div[2]/article/div[1]/div[1]/div[1]/div[6]/' \
             'div[2]/div[1]/div/div/table/tbody/tr[{}]/td[{}]'

loop_url = 'https://fr.investing.com/indices/france-40-historical-data'

loop_x_path = '//*[@id="curr_table"]/tbody/tr[{}]/td[{}]'


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
    if len(data) > 0:
        maxi = [element[3] for element in data]     # liste pour récupérer tous les plus hauts quotidiens à l'index[3]
        return max(maxi)                            # on retourne le plus haut
    else:
        try:
            return pre_web_higher
        except NameError:
            return "Il n'y a pas de plus haut dans la liste historique parce qu'elle est vide !"


def reformate_data(data):
    """ reformatage des données et conversion du type string vers float """
    return float(data.replace(".", "").replace(",", "."))


# ------ configuration de la classe WebDriver ------
class WebDriver:
    """ classe qui configure le webDriver pour récupérer des données par leur xpath """
    def __init__(self, url, x_path, index1, index2, loop=None):
        self.url = url
        self.x_path = x_path
        self.index1 = index1
        self.index2 = index2
        self.loop = loop
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
        if last_saved_date != "0":
            my_list = self.while_loop(nb)
        else:
            my_list = self.for_loop(nb)
        return my_list

    def while_loop(self, i):
        """ fonction qui collecte les données avec une boucle while """
        my_list = []
        last_date = self.parse_array(self.x_path, i, 1)
        while last_date != last_saved_date and i < 22:
            last_date = self.parse_array(self.x_path, i, 1)
            raw_lasts = self.parse_array(self.x_path, i, 2)
            last = reformate_data(raw_lasts)
            raw_opening = self.parse_array(self.x_path, i, 3)
            opening = reformate_data(raw_opening)
            raw_higher = self.parse_array(self.x_path, i, 4)
            higher = reformate_data(raw_higher)
            raw_lower = self.parse_array(self.x_path, i, 5)
            lower = reformate_data(raw_lower)
            my_list.append([last_date, last, opening, higher, lower])
            last_date = self.parse_array(self.x_path, i + 1, 1)
            print("la valeur incrémentée en fin de boucle est celle du " + last_date)
            i += 1
        return my_list

    def for_loop(self, nb):
        """ fonction qui collecte les données avec une boucle for """
        my_list = []
        for i in range(nb, 22):
            last_date = self.parse_array(self.x_path, i, 1)
            raw_lasts = self.parse_array(self.x_path, i, 2)
            last = reformate_data(raw_lasts)
            raw_opening = self.parse_array(self.x_path, i, 3)
            opening = reformate_data(raw_opening)
            raw_higher = self.parse_array(self.x_path, i, 4)
            higher = reformate_data(raw_higher)
            raw_lower = self.parse_array(self.x_path, i, 5)
            lower = reformate_data(raw_lower)
            my_list.append([last_date, last, opening, higher, lower])
        print("La boucle for a retouné : " + str(len(my_list)))
        return my_list

    def parse_array(self, x_path, index1, index2):
        """ méthode qui récupère les valeurs du CAC dans le DOM de la page """
        return self.driver.find_element_by_xpath(x_path.format(str(index1), str(index2))).text


# ------ chargement du fichier des données historiques ------
PX_datas = []
PX_datas = get_datas("PX-datas", PX_datas)
print("Voici le fichier sauvegardé : " + str(PX_datas))
print("La liste contient : " + str(len(PX_datas)) + " éléments.")
pre_web_higher = get_higher(PX_datas)

# ------ chargement du fichier du dernier plus haut local, s'il n'existe pas on le crée ------
saved_high = ()
saved_high = get_datas("saved_high", saved_high)

# ------ si le fichier est vide, on garde les valeurs de références, sinon on les actualise ------
if len(saved_high) > 0:
    MY_LAST_HIGH = saved_high[0]
    MY_LAST_DATE = saved_high[1]
else:
    MY_LAST_HIGH = MY_LAST_HIGH
    MY_LAST_DATE = MY_LAST_DATE
print("Le plus haut enregistré dans le fichier 'saved_high' vaut " + str(MY_LAST_HIGH) +
      " à la date du " + str(MY_LAST_DATE))

# ------ récupération de la date la plus récente dans le fichier enrégistré ------
if len(PX_datas) > 0:
    last_saved_date = PX_datas[0][0]
else:
    last_saved_date = "0"

print("Le dernier plus haut enregistré vaut " + str(pre_web_higher) + " points, à la date du  " + str(last_saved_date))
print()
print("Chargement du webDriver pour récupérer les dernières données...")

# ------ récupération du plus haut local depuis le dernier chargement ------
investing = WebDriver(loop_url, loop_x_path, 1, 1, "loop")
investing_result = investing.datas
print("Les données scrapées sur le site d'Investing : " + str(investing_result))
post_web_higher = get_higher(investing_result)
if post_web_higher > pre_web_higher:
    print("Un nouveau plus haut a été effectué depuis le dernier chargement : " + str(post_web_higher))
else:
    print("Aucun nouveau plus haut depuis le dernier chargement.")

# ------ récupération des plus hauts locaux ------
print()
print("Instanciation de la classe WebDriver pour récupérer les données sur le site de Boursorama...")
cac_high = WebDriver(cac_url, cac_x_path, 4, 6)
high_cac = float(cac_high.datas.replace(" ", ""))
lvc_high = WebDriver(lvc_url, lvc_x_path, 4, 6)
high_lvc = float(lvc_high.datas)
print("Les dernières valeurs disponibles du cac : " + str(high_cac) + " et du lvc : " + str(high_lvc))

# ------ fusion et sauvegarde de la liste historique (PX_datas) actualisée avec la liste scrapée (new_datas) ------
index = 0
for each_element in investing_result:
    PX_datas.insert(index, each_element)
    index += 1
save_datas("PX-datas", PX_datas)
print()
print("Fusion des listes réalisées : la sauvegarde a été actualisée.")
print("La liste contient désormais " + str(len(PX_datas)) + " éléments.")
print("FIN DU SCRAPING !!!")
print()
print("Le dernier plus haut local valait " + str(MY_LAST_HIGH) + " points à la date du " + MY_LAST_DATE)

# ------ on crée une boucle qui vérifie si un nouveau plus haut relatif a été réalisé ------
"""il faut ajouter une condition de date pour la recherche du nouveau plus haut local"""
new_high = []
for item in PX_datas:
    my_item = float(item[3])
    if my_item > MY_LAST_HIGH:
        new_high.append(my_item)
        MY_LAST_HIGH = my_item
        MY_LAST_DATE = item[0]
if len(new_high) > 0:
    print("MY_LAST_HIGH vaut maintenant : " + str(MY_LAST_HIGH) + " à la date du : " + str(MY_LAST_DATE))
else:
    print("Pas de nouveau plus haut local effectué, MY_LAST_HIGH vaut toujours " + str(MY_LAST_HIGH))

# ------ sauvegarde de la valeur du dernier plus haut local ------
saved_high = (MY_LAST_HIGH, MY_LAST_DATE)
save_datas("saved_high", saved_high)

# ------ nombre de positions engagées ------
positions = 0

# ------ détermination du premier niveau d'achat ------
achat_1 = MY_LAST_HIGH - (MY_LAST_HIGH * 0.05)
print("Le premier niveau d'achat se situe à " + str(achat_1))

"""ici il faut calculer la valeur du lvc relativement au cac actuel et au cac -5%.
Une fonction qui calcule automatiquement le prix du lvc par rapport au cac doit être développée."""

# ------ lancement d'un ordre d'achat ------
new_low = []
low_result = ""
k = 0
for item in PX_datas:
    my_item = float(item[4])
    while str(item[0]) != MY_LAST_DATE and k < len(PX_datas):
        print(str(item[0]))
        if my_item < achat_1:
            new_low.append(my_item)
            low_result = "Un niveau d'achat a été touché. A vérifier sur le site de BourseDirect."
        else:
            low_result = "Pas de niveau d'achat touché."
        k += 1
print(low_result)
print("la liste new_low : " + str(new_low))

"""il faut créer une fonction qui vérifie si, entre la date du jour et la dernière date chargée, le plus bas < achat1
cette fonction pourra prendre des arguments afin de servir à plusieurs vérifications de cet ordre

L'algorithme est le suivant :
- si position = 0:
        alors achat à last_high-5%
- si position > 0:
        alors achat à A(n-1)-2%
- si position = 0 et vente sur objectif:
        alors achat à vente-5%
- si position = 0 et nouveau plus haut:
        alors supprimer ordre non passé;
        achat à last-high-5%
        
L'idée est de traquer l'indice de référence pour se placer à l'achat dès qu'il perd 5%.
L'objectif de revente est à +5%.
Quand une ligne est prise, les ordres suivants si situent 2% plus bas.
Jusqu'à ce qu'il ne reste qu'une seule position, toutes les positions vendues seront reprises à -5%.
Quand toutes les lignes sont vendues, on recommence en traquant un nouveau plus haut sur l'indice pour acheter à -5%.
        """

quit()
