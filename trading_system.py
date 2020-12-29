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
            return "Pas de plus haut trouvé : la liste est peut-être vide !"


def reformate_data(data):
    """ reformatage des données et conversion du type string vers float """
    return float(data.replace(".", "").replace(",", "."))


def buy_limit(value, target, leverage):
    """fonction qui calcule un objectif cible en pourcentage ajusté d'un levier"""
    return round(value - (((value * target) / 100) * leverage), 2)


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


# ------ chargement du fichier des données historiques ------
PX_datas = []
PX_datas = get_datas("PX-datas", PX_datas)
try:
    if len(PX_datas) > 0:
        print("Voici le fichier sauvegardé : " + str(PX_datas))
        print("La liste contient : " + str(len(PX_datas)) + " éléments.")
    else:
        print("Aucune donnée sauvegardée. Le fichier est vide.")
except TypeError:
    print("Exception levée. Le fichier est vide, aucune donnée sauvegardée.")

# ------ récupération de la valeur et de la date du dernier plus haut dans le fichier enrégistré ------
pre_web_higher = get_higher(PX_datas)
if len(PX_datas) > 0:
    last_saved_date = PX_datas[0][0]
else:
    last_saved_date = "0"

print("Le dernier plus haut enregistré vaut " + str(pre_web_higher) + " points, à la date du  " + str(last_saved_date))

# ------ chargement du fichier du dernier plus haut local, s'il n'existe pas on le crée ------
saved_high = ()
saved_high = get_datas("saved_high", saved_high)

# ------ si le fichier est vide, on garde les valeurs de références, sinon on les actualise ------
try:
    if len(saved_high) > 0:
        MY_LAST_HIGH = saved_high[0]
        MY_LAST_DATE = saved_high[1]
        print("Le plus haut enregistré dans le fichier 'saved_high' vaut " + str(MY_LAST_HIGH) +
              " à la date du " + str(MY_LAST_DATE))
except TypeError:
    print("Le fichier est vide. Aucun plus haut trouvé.")

# ------ chargement du fichier de sauvegarde des positions ------
positions_list = []
positions_list = get_datas("positions_list", positions_list)

# ------ nombre de positions engagées que l'on récupère dans le fichier ------
try:
    if len(positions_list) > 0:
        print("Voici vos positions :" + str(positions_list))
    else:
        print("Vous n'avez pas de positions.")
except TypeError:
    print("Le fichier est vide. Aucune position n'a encore été prise.")

# ------ mise à jour des dernières données du cac disponibles sur Investing ------
print("\nChargement du webDriver pour récupérer les dernières données...")
investing = WebDriver(loop_url, loop_x_path, 1, 1, "loop")
investing_datas = investing.datas
print("Les données scrapées sur le site d'Investing : " + str(investing_datas))

# ------ on vérifie si un nouveau plus haut a été réalisé ------
post_web_higher = get_higher(investing_datas)
if post_web_higher > pre_web_higher:
    print("Un nouveau plus haut a été effectué depuis le dernier chargement : " + str(post_web_higher))
else:
    print("Aucun nouveau plus haut depuis le dernier chargement.")

# ------ récupération de la dernière valeur disponible du cac et du lvc sur Boursorama ------
print("\nInstanciation de la classe WebDriver pour récupérer les données sur le site de Boursorama...")
cac_high = WebDriver(cac_url, cac_x_path, 4, 6)
high_cac = float(cac_high.datas.replace(" ", ""))
lvc_high = WebDriver(lvc_url, lvc_x_path, 4, 6)
high_lvc = float(lvc_high.datas)
print("Les dernières valeurs disponibles du cac : " + str(high_cac) + " et du lvc : " + str(high_lvc))

# ------ fusion et sauvegarde de la liste historique (PX_datas) actualisée et de la liste scrapée (new_datas) ------
index = 0
for each_element in investing_datas:
    PX_datas.insert(index, each_element)
    index += 1
save_datas("PX-datas", PX_datas)
print("\nFusion des listes réalisées : la sauvegarde a été actualisée.")
print("La liste contient désormais " + str(len(PX_datas)) + " éléments.")
print("FIN DU SCRAPING !!!")
print("\nLe dernier plus haut local valait " + str(MY_LAST_HIGH) + " points à la date du " + MY_LAST_DATE)

# ------ on crée une boucle qui vérifie si un nouveau plus haut relatif a été réalisé ------
msg = ""
try:
    if len(PX_datas) > 0:
        new_high = []
        for item in PX_datas:
            if item[0] != MY_LAST_DATE:
                my_item = float(item[3])
                if my_item > MY_LAST_HIGH:
                    new_high.append(my_item)
                    MY_LAST_HIGH = my_item
                    MY_LAST_DATE = item[0]
                    msg = "MY_LAST_HIGH vaut maintenant : " + str(MY_LAST_HIGH) + " à la date du " + str(MY_LAST_DATE)
                else:
                    msg = "Pas de nouveau plus haut local effectué, MY_LAST_HIGH vaut toujours " + str(MY_LAST_HIGH)
            else:
                break
except TypeError:
    msg = "Le fichier est vide..."
finally:
    print(msg)

# ------ sauvegarde de la valeur et de la date du dernier plus haut local ------
saved_high = (MY_LAST_HIGH, MY_LAST_DATE)
save_datas("saved_high", saved_high)

# ------ prise en compte du leverage x2 : calcul du delta ------
if high_cac > MY_LAST_HIGH:
    delta = abs(((MY_LAST_HIGH * 100) / high_cac) - 100) * 2
    lvc = high_lvc - ((high_lvc * delta) / 100)
else:
    delta = abs(((high_cac * 100) / MY_LAST_HIGH) - 100) * 2
    lvc = abs(high_lvc + ((high_lvc * delta) / 100))

# ------ détermination du premier niveau d'achat arrondi sur le LVC, avec objectif +5% et levier x2 ------
PX_A1 = buy_limit(MY_LAST_HIGH, 5, 1)
A1 = buy_limit(lvc, 5, 2)
print("\nLe premier niveau d'achat se situe à " + str(PX_A1) + " points, ce qui équivaut à " + str(A1) + " sur le lvc.")

"""

creuser les assertions en python (assert) qui semblent proches de try except pour lever des erreurs.

pre_web_higher, post_web_higher et même fonction get_higher() sont peut-être inutiles.
Je n'ai pas besoin de connaître les plus hauts historiques en remontant trop loin, ce qu'il me faut c'est déterminer
le dernier plus haut depuis la dernière revente. Donc quand POSITIONS = 0, traquer le NEW_HIGH et acheter à -5%.
Les lignes concernées sont 64-75, 174-180 et 215-221."""


"""il faut créer une fonction qui vérifie si, entre la date du jour et la dernière date chargée, le plus bas < achat1
cette fonction pourra prendre des arguments afin de servir à plusieurs vérifications de cet ordre

L'algorithme est le suivant :

A L'ACHAT :
1-  IF POSITION = 0:
        +A1 à LAST_HIGH-5%
        +A2 à A1-2%
        +A3 à A2-2%
2-   IF POSITION = 0 AND NEW_HIGH:
        ANNULATION A1 A2 A3
        +A1 à NEW_HIGH-5%
        +A2 à A1-2%
        +A3 à A2-2%
3-  IF POSITION > 0:
        +A à (A-1)-2%
        DONC SI A7 => ACHAT à A6-2%
APRES LA VENTE :
3-   IF POSITION > 0:
        +A à -5%
4-   IF POSITION = 0:
        RETOUR à 1
        
L'idée est de traquer l'indice de référence pour se placer à l'achat dès qu'il perd 5%.
L'objectif de revente est à +5%.
Quand une ligne est prise, les ordres suivants se situent 2% plus bas.
Jusqu'à ce qu'il ne reste qu'une seule position, toutes les positions vendues seront reprises à -5%.
Quand toutes les lignes sont vendues, on recommence en traquant un nouveau plus haut sur l'indice pour acheter à -5%.
        """

quit()
