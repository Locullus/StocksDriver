""" Programme d'envoi d'email automatique.
    Les identifiants personnels sont stockées puis récupérées dans les variables d'environnement avec dotenv
    """

import os
import smtplib
import ssl
from dotenv import load_dotenv

load_dotenv()


def sending_mail(list_position):
    """Fonction qui envoie un mail d'alerte automatique

        Args :
        elle prend en argument un objet qui est la position à actualiser

        Return :
        ne retourne rien, se contente d'expédier le mail en appelant les différents attribut de l'objet
    """

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("PASSWORD")

    # on crée une boucle pour récupérer toutes les positions existantes et on en fait le rendu dans une variable render
    # on ajoute également un peu de logique conditionnelle pour personnaliser l'affichage.
    # Comme il n'est pas possible d'injecter de la logique dans le rendu triple quotes ("""), j'opte pour render()
    # que j'utilise comme un rendu commun de template (React-like)
    render = []
    for position in list_position:
        if position.sign == "+":
            direction = "achat"
        else:
            direction = "vente"

        render.append(f"{position.name} : le {position.date} dans le sens {direction} {position.quantity} \
{position.stock} {position.price} (PX= {position.px}) [validite jusqu'au {position.deadline}]")
    render = "\n".join(render)

    message = f"""Subject: Email from StocksDriver\n\n    

    Verifiez vos positions.\n
    Voici le contenu du fichier 'positions' : \n
    
    {render}

    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

# TODO : vérifier l'affichage des positions multiples lorsqu'elles auront été envoyées au fichier positions
