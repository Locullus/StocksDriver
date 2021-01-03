"""création d'une classe qui doit gérer les positions prises. Il s'agit de manipuler des objets conservés dans
    un fichier lu à chaque lancement. La classe vérifiera si les cours ont touchés une ou plusieurs positions
    et agira en conséquence.
    Un ordre est toujours en attente d'une exécution, soit parce qu'il attend que son objectif d'achat soit atteint
    pour être passé, soit qu'il attend d'être soldé quand son objectif est atteint. Pour les distinguer, on leur
    assigne donc un état, un signe + ( ordre d'achat en attente d'être exécuté) ou - (ordre de vente en attente
    d'être exécuté)."""

import pickle
from datetime import date


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


# ------ classe qui gère les positions ------
class Position:
    def __init__(self, name, my_date, sign, quantity, stock, price, px, deadline):
        self.name = name
        self.date = my_date
        self.sign = sign
        self.quantity = quantity
        self.stock = stock
        self.price = price
        self.px = px
        self.deadline = deadline

    def check_position(self):
        if self.sign == "+":
            print("Cette position n'a pas encore été ouverte, elle attend que les cours la touchent.")
        else:
            print("Cette position est ouverte et attend que les cours atteignent son objectif pour être soldée.")
        if self.px >= last_low_PX1:
            print("Le cours a été touché, la position est passée !")
            print("Il faut maintenant créer une nouvelle instance, de vente cette fois.")


# ------ récupération des instances enregistrées de la classe Position ------
positions = []
position_nb = 0
positions = get_datas("positions", positions)
try:
    if len(positions) > 0:
        print(("\nVoici le nombre de positions : " + str(len(positions))))
        position_nb = len(positions)
    else:
        print("\nPas de positions...")
except TypeError:
    print("\nException levée. Pas de fichier trouvé...")

# ------ récupération des valeurs scrapées du lvc via le fichier lvc_datas ------
lvc_garbage = ()    # ce tuple vide est créé pour éviter d'écraser lvc_datas à la récupèration de ses données
lcv_high, lvc_low, cac_high, cac_low = get_datas("lvc_datas", lvc_garbage)
print(f"Les données récupérées dans le fichier lvc_datas sont : lvc_high {lcv_high}, low_lvc {lvc_low}, cac_high "
      f"{cac_high} et cac_low {cac_low}")

# ------ récupération des données scrapées du lvc via le fichier buy_limit ------
A1, PX_A1, last_low_PX1 = get_datas("buy_limit", lvc_garbage)
print(f"Les données du fichier buy_limit sont pour A1 {A1}, pour PX_A1 {PX_A1} et pour last_low_PX1 {last_low_PX1}")

# ------ récupération de la date du jour ------
date = date.today()
print("la date du jour est " + str(date))
print(f"Au format local cela donne {date.day}/{date.month}/{date.year}")

# ------ calcul de la date de validité à 3 mois ------
expiration = f"{date.day}/{date.month + 3}/{date.year}"
print(f"La date d'expiration à trois mois nous donne {expiration}")

# ------ on reconstruit notre objet position ------
lvc_quantity = 500/A1
if position_nb == 0:
    position_A1 = Position("A1", date, "+", lvc_quantity, "lvc", A1, PX_A1, expiration)
    positions.append(position_A1)
else:
    position_A1 = positions[0]

print(f"{position_A1.name} : le {position_A1.date} {position_A1.sign} {round(position_A1.quantity)} {position_A1.stock}"
      f"@{position_A1.price} (PX= {position_A1.px} validité jusqu'au {position_A1.deadline})")
position_A1.check_position()

# ------ sauvegarde du fichier positions ------
save_datas("positions", positions)

"""Il faut importer les données du module trading_system.py et changer les variables arbitrairement affectées.

    Il faut changer la variable last_low_PX1 pour une valeur qui capte le plus bas du jour sur le lvc.
    Il faut récupérer le dernier plus bas relatif réalisé depuis le passage de l'ordre et non le dernier bas en date.
    Si last_low_lvc <= self.price, on considère que l'ordre est passé et on lance un ordre de vente cette fois.
    Autrement dit on crée une nouvelle instance de la classe Position avec les caractéristiques de la vente.
    Peut-être cette dernière instance gardera-t-elle le même nom de A1...
    
    Il faut remplacer la ligne A1 à l'achat par la ligne A1 à la vente.
    
    Il faut ajouter les plus bas du lvc et du px obtenus depuis boursorama afin que la classe puisse vérifier
    si les positions en attente à l'achat ont été exécutées. """
