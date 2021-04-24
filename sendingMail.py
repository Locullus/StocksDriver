""" Programme d'envoi d'email automatique.
    Les identifiants personnels sont stockées puis récupérées dans les variables d'environnement avec dotenv
    """

import os
import smtplib
import ssl
from dotenv import load_dotenv

load_dotenv()


def sending_mail(position):
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
    message = f"""Subject: Email from StocksDriver\n\n    

    Verifier vos positions. La derniere position en date est la suivante : 
    {position.name} : le {position.date} {position.sign} {position.quantity} {position.stock} {position.price} \
    (PX= {position.px}) [validite jusqu'au {position.deadline}]

    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


"""
La prochaine fonctionnalité consistera à gérer une liste d'objets en argument plutôt qu'un unique objet.
Ceci permettra de recevoir plusieurs positions, ce qui à terme est l'objectif.
Il suffira pour cela de créer une boucle.
"""