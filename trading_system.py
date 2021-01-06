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

    Ici nous avons le programme principal (__main__)
    """

# ------ importation des modules ------
from datetime import date
from classPosition import WebDriver, Position, get_datas, save_datas, get_higher, buy_limit, reformate_datetime

# ------ affectation de la valeur et de la date du premier point haut local ------
MY_LAST_HIGH = 5555.83
MY_LAST_DATE = "23/11/2020"
last_saved_date = "0"

# ------ déclaration des url des xpath des données à scraper ------
cac_url = 'https://www.boursorama.com/bourse/indices/cours/1rPCAC/'
cac_x_path = '//*[@id="main-content"]/div/section[1]/div[2]/article/div[1]/div[2]/div[1]/div[5]/' \
             'div[2]/div[1]/div/div/table/tbody/tr[{}]/td[{}]'

lvc_url = 'https://www.boursorama.com/bourse/trackers/cours/1rTLVC/'
lvc_x_path = '//*[@id="main-content"]/div/section[1]/div[2]/article/div[1]/div[1]/div[1]/div[6]/' \
             'div[2]/div[1]/div/div/table/tbody/tr[{}]/td[{}]'

loop_url = 'https://fr.investing.com/indices/france-40-historical-data'

loop_x_path = '//*[@id="curr_table"]/tbody/tr[{}]/td[{}]'


# ------ chargement du fichier des données historiques ------
PX_datas = []
PX_datas = get_datas("PX-datas", PX_datas)
try:
    if len(PX_datas) > 0:
        last_saved_date = PX_datas[0][0]
        print("Voici le fichier sauvegardé : " + str(PX_datas))
        print("La liste contient : " + str(len(PX_datas)) + " éléments.")
    else:
        print("Aucune donnée sauvegardée. Le fichier est vide.")
except TypeError:
    print("Exception levée. Le fichier est vide, aucune donnée sauvegardée.")

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

# ------ mise à jour des dernières données du cac disponibles sur Investing ------
print("\nChargement du webDriver pour récupérer les dernières données...")
investing = WebDriver(loop_url, loop_x_path, 1, 1, loop="loop", last_saved_date=last_saved_date)
investing_datas = investing.datas
print("Les données scrapées sur le site d'Investing : " + str(investing_datas))

# ------ on vérifie si un nouveau plus haut a été réalisé ------
post_web_higher = get_higher(investing_datas)
if isinstance(post_web_higher, str):    # si get_higher retourne une chaîne on l'écrit
    print(post_web_higher)
else:
    if post_web_higher > MY_LAST_HIGH:    # sinon c'est un float et on peut comparer les valeurs
        print("Un nouveau plus haut a été effectué depuis le dernier chargement : " + str(post_web_higher))
    else:
        print("Aucun nouveau plus haut depuis le dernier chargement.")

# ------ récupération de la dernière valeur disponible du cac et du lvc sur Boursorama ------
print("\nInstanciation de la classe WebDriver pour récupérer les données sur le site de Boursorama...")
cac_high = WebDriver(cac_url, cac_x_path, 4, 6)
high_cac = float(cac_high.datas.replace(" ", ""))
cac_low = WebDriver(cac_url, cac_x_path, 5, 6)
low_cac = float(cac_low.datas.replace(" ", ""))
lvc_high = WebDriver(lvc_url, lvc_x_path, 4, 6)
lvc_low = WebDriver(lvc_url, lvc_x_path, 5, 6)
high_lvc = float(lvc_high.datas)
low_lvc = float(lvc_low.datas)
print(f"Les dernières valeurs disponibles du cac : {high_cac} et du lvc : {high_lvc}")
print(f"Le plus bas du lvc ce même jour est à {low_lvc} et le plus bas du cac est {low_cac}")
lvc_datas = (high_lvc, low_lvc, high_cac, low_cac)
save_datas("lvc_datas", lvc_datas)

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
new_high_done = False
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
                    new_high_done = True
                else:
                    msg = "Pas de nouveau plus haut local effectué, MY_LAST_HIGH vaut toujours " + str(MY_LAST_HIGH)
            else:
                break
except TypeError:
    msg = "Le fichier est vide..."
finally:
    if new_high_done:
        msg = "MY_LAST_HIGH vaut maintenant : " + str(MY_LAST_HIGH) + " à la date du " + str(MY_LAST_DATE)
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

# ------ insertion des données du second module ------

# ------ récupération des instances enregistrées de la classe Position ------
positions = []
position_nb = 0
positions = get_datas("positions", positions)
try:
    if len(positions) > 0:
        position_nb = len(positions)
        print(f"\nVoici le nombre de positions : {position_nb}")
    else:
        print("\nPas de positions...")
except TypeError:
    print("\nException levée. Pas de fichier trouvé...")

# ------ récupération de la date du jour ------
date = date.today()
date = reformate_datetime(date)     # la fonction semble renvoyer un objet identique à l'entrée...
print(f"la date du jour est {date}")

# ------ calcul de la date de validité à 3 mois ------
expiration = reformate_datetime(date, 3)
print(f"La date d'expiration à trois mois nous donne {expiration}")

# ------ on recupère notre objet position, s'il n'existe pas on le crée ------
lvc_quantity = 500 / A1
if position_nb == 0:
    position_A1 = Position("A1", date, "+", lvc_quantity, "lvc", A1, PX_A1, expiration)
    positions.append(position_A1)
else:
    position_A1 = positions[0]

position_A1.date = reformate_datetime(position_A1.date)
print("\nLa position trouvée est la suivante :")
print(f"{position_A1.name} : le {position_A1.date} {position_A1.sign} {round(position_A1.quantity)} {position_A1.stock}"
      f"@{position_A1.price} (PX= {position_A1.px} validité jusqu'au {position_A1.deadline})")

# ------ on vérifie si la position a été exécutée ------
result = position_A1.check_position(PX_datas)
print(f"{result[0]} : le {result[1]} {result[2]} {round(result[3])} {result[4]}"
      f"@{result[5]} (PX= {result[6]} validité jusqu'au {result[7]})")

# ------ sauvegarde du fichier positions ------
save_datas("positions", positions)

"""    
    Revoir la fonction reformate_datetime() qui semble parfois travailler pour renvoyer un résultat identique à l'entrée
    
    Si last_low_lvc <= self.price, on considère que l'ordre est passé et on lance un ordre de vente cette fois.
    Autrement dit on crée une nouvelle instance de la classe Position avec les caractéristiques de la vente.
    Peut-être cette dernière instance gardera-t-elle le même nom de A1...

    Il faut remplacer la ligne A1 à l'achat par la ligne A1 à la vente.

    Il faut ajouter les plus bas du lvc et du px obtenus depuis boursorama afin que la classe puisse vérifier
    si les positions en attente à l'achat ont été exécutées. """
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
