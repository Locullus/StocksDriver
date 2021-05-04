#!/usr/bin/env python3

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
from classPosition import WebDriver, Position, get_datas, save_datas,\
    get_higher, buy_limit, reformate_datetime, set_delta
from sendingMail import sending_mail

# ------ affectation de la valeur et de la date du premier point haut local ------
MY_LAST_HIGH = 5555.83
MY_LAST_DATE = "23/11/2020"
last_saved_date = "0"
new_higher = False

# ===============================================================================================
# une alternative pour scraper les cours du lvc via le site d'Euronext :
#
# le lvc : https://live.euronext.com/en/product/etfs/fr0010592014-xpar/lyxor-etf-lev-cac/lvc
#
# idem pour le CAC : https://live.euronext.com/en/product/indices/FR0003500008-XPAR
#
# ===============================================================================================

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
        print("Le fichier de sauvegarde contient : " + str(len(PX_datas)) + " éléments.")
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
try:
    investing_datas = investing.datas
except AttributeError:
    print("Aucune données disponibles. Le problème pourrait venir du site lui-même ou de l'horaire...")
    investing_datas = None
print("Les données scrapées sur le site d'Investing : " + str(investing_datas))

# ------ on vérifie si un nouveau plus haut a été réalisé ------
post_web_higher = get_higher(investing_datas)
if isinstance(post_web_higher, str):  # si get_higher retourne une chaîne on l'écrit
    print(post_web_higher)
else:
    if post_web_higher > MY_LAST_HIGH:  # sinon c'est un float et on peut comparer les valeurs
        new_higher = True
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
print(f"Les dernières valeurs disponibles du cac : plus haut {high_cac}, plus bas {low_lvc} ; "
      f"pour le  lvc : plus haut {high_lvc}, plus bas {low_cac}.")
lvc_datas = (high_lvc, low_lvc, high_cac, low_cac)
save_datas("lvc_datas", lvc_datas)

# ------ fusion et sauvegarde de la liste historique (PX_datas) actualisée et de la liste scrapée (new_datas) ------
index = 0
for each_element in investing_datas:
    PX_datas.insert(index, each_element)
    index += 1
save_datas("PX-datas", PX_datas)
print("\nFusion des listes réalisées : la sauvegarde a été actualisée. "
      "La liste contient désormais " + str(len(PX_datas)) + " éléments.")
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

# ------ prise en compte du leverage x2 : fonction qui calcule le delta ------
lvc = set_delta(high_cac, MY_LAST_HIGH, high_lvc)

# ------ détermination du premier niveau d'achat arrondi sur le LVC, avec objectif +5% et levier x2 ------
PX_A1 = buy_limit(MY_LAST_HIGH, 5, 1)
A1 = buy_limit(lvc, 5, 2)
print("\nLe premier niveau d'achat se situe à " + str(PX_A1) + " points, ce qui équivaut à " + str(A1) + " sur le lvc.")

# ------ insertion des données du second module ------

# ------ récupération des instances enregistrées de la classe Position ------
positions = []
position_length = 0
positions = get_datas("positions", positions)
try:
    if len(positions) > 0:
        position_length = len(positions)
        print(f"\nVoici le nombre de positions : {position_length}")
    else:
        position_length = 0
        print("\nPas de positions...")
except TypeError:
    print("\nException levée. Pas de fichier trouvé...")

# ------ récupération de la date du jour ------
today = date.today()
string_date = reformate_datetime(today)  # la fonction semble renvoyer un objet identique à l'entrée...
print(f"la date du jour est {string_date}")

# ------ calcul de la date de validité à 3 mois ------
expiration = reformate_datetime(today, 90)
print(f"La date d'expiration à 90 jours nous donne le {expiration}")

# ------ on recupère notre objet position, s'il n'existe pas on le crée ------
# TODO : ZeroDivisionError: float division by zero => ATTENTION : près de l'heure d'ouverture LVC = 0
# TODO : on peut gérer cette erreur avec un message demandant d'attendre l'ouverture du marché pour lancer l'appli
lvc_quantity = round(750 / A1)
if position_length == 0:
    position_A1 = Position("A1", string_date, "+", lvc_quantity, "lvc", A1, PX_A1, expiration)
    positions.append(position_A1)
else:
    position_A1 = positions[0]

print("\nLa position existante est la suivante :")
print(f"{position_A1.name} : le {position_A1.date} {position_A1.sign} {position_A1.quantity} {position_A1.stock}"
      f"@{position_A1.price} (PX= {position_A1.px}) [validité jusqu'au {position_A1.deadline}]")

# ------ on vérifie si la position a été exécutée ------
print("\nOn vérifie si la position a été touchée")
result = []

# ============ ATTENTION CECI NE VAUT QUE POUR UNE LISTE 'POSITIONS' AVEC UN UNIQUE ELEMENT =============

for position in positions:
    result = position.check_position(PX_datas)
    print(f"Voici le contenu du fichier positions : {result}")

    # ------ on vérifie si la position existante est toujours relative au dernier plus haut ------
    if position.sign == "+" and new_higher:
        print("L'ordre d'achat non exécuté va être actualisé pour refléter le nouveau plus haut atteint.")

        # TODO : il faudrait créer un objet 'Position' avec tous les attributs plutôt que les envoyer un à un
        ma_position_test = {
            "name": "A1",
            "date": string_date,
            "sign": "+",
            "quantity": lvc_quantity,
            "stock": "lvc",
            "price": A1,
            "px": PX_A1,
            "deadline": expiration
        }
        # TODO: ensuite passer ce dictionnaire ou cet objet en paramètre puis faire self.name = args.name par exemple
        position_A1 = Position("A1", string_date, "+", lvc_quantity, "lvc", A1, PX_A1, expiration)
        print(f"La nouvelle position en attente à l'achat est la suivante : "
              f"{position_A1.name} : le {position_A1.date} {position_A1.sign} {position_A1.quantity} "
              f"{position_A1.stock} {position_A1.price} (PX= {position_A1.px}) [validité jusqu'au "
              f"{position_A1.deadline}]")

        # ------ on met à jour l'UNIQUE ELEMENT de la liste 'positions' ------
        positions[0] = position_A1

        # ------ on envoie un mail automatique afin d'avertir de l'évolution de la position ------
        sending_mail(positions)
        print("Vérifiez votre boîte mail...")

# ============ ATTENTION CECI NE VAUT QUE POUR UNE LISTE 'POSITIONS' AVEC UN UNIQUE ELEMENT =============

    # ------ sauvegarde du fichier positions ------
print("Le fichier 'positions' a été sauvegardé.")
save_datas("positions", positions)

quit()

"""    
    =====================================================================================
    Il faut calculer les positions depuis un nouveau plus haut pour trois lignes (A1, A2, A3)
    Il faut aussi calculer l'objectif de revente à PX+5% pour chaque ligne passée
    =====================================================================================
    
    =====================================================================================
    Le programme nécessitant un web Driver à jour pour fonctionner, il faut implémenter une
    gestion de l'exception levée lorsqu'une mise à jour est requise et la télecharger automatiquement
    =====================================================================================
    
    =====================================================================================
    Développement de l'application avec une interface utilisateur avec Flask dans un premier temps.
    Transformation du fichier de sauvegarde en système de base de données et ajout de fichiers html.    
    Une fois en ligne, l'appli devra se connecter au marché après la fermeture de celui-ci pour
    récupérer les dernières données qu'elle conservera dans une base de données.
    Elle opérera alors un contrôle des positions et les ajustera en fonction des données recueillies.
    Un mail sera envoyé quotidiennement pour avertir des changements ou non dans les positions.
    A terme, elle se connectera au broker pour passer les ordres nécessaires automatiquement.
    =====================================================================================
    
    =====================================================================================
    en début de script ajouter ceci (shabang) pour qu'il soit reconnu comme tel par le serveur :
    #!/usr/bin/env python3 => cette commande pour Unix recherche l'éxecutable Python à l'aide de la commande env
    
    en fin de script ajouter ceci :
    if __name__ == "__main__":
        main()
    =====================================================================================
    On pourra ajouter un Cron depuis le serveur pour planifier une exécution automatique quotidienne.
    Cf https://faq.o2switch.fr/hebergement-mutualise/tutoriels-cpanel/taches-cron
        
    ================================== ALGORITHME =======================================
L'idée est de traquer l'indice de référence pour se placer à l'achat dès qu'il perd 5%.
L'objectif de revente est à +5%.
Quand une ligne est prise, les ordres suivants se situent 2% plus bas.
Jusqu'à ce qu'il ne reste qu'une seule position, toutes les positions vendues seront reprises à -5%.
Quand toutes les lignes sont vendues, on recommence en traquant un nouveau plus haut sur l'indice pour acheter à -5%.
        
L'algorithme est le suivant :

A L'ACHAT :
1-  IF POSITIONS = 0:
        +A1 à LAST_HIGH-5%
        +A2 à A1-2%
        +A3 à A2-2%
2-   IF POSITIONS == 0 AND NEW_HIGH:
        ANNULATION A1 A2 A3
        +A1 à NEW_HIGH-5%
        +A2 à A1-2%
        +A3 à A2-2%
3-  IF POSITION > 0:
        FOR POSITION IN POSITIONS:
        ON RECUPERERE LES POSITIONS DANS LE FICHIER
        ON VERIFIE SI LE NIVEAU D'ACHAT EST TOUCHE
A LA VENTE :
4-   DES QUE LE COURS EST TOUCHE:
    IF POSITIONS == 0:
        RETOUR à 1
    IF POSITIONS > 0:
        REPRISE DE LA POSITION SUR NIVEAU ACHAT PRECEDENT
        RETOUR A 3
        """
