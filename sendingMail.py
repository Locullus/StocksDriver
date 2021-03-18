""" Programme d'envoi d'email automatique.
    Les identifiants personnels sont stockées puis récupérées dans les variables d'environnement avec dotenv
    """

import os
import smtplib
import ssl
from dotenv import load_dotenv

load_dotenv()


def sending_mail(name, date, sign, quantity, stock, price, px, deadline):
    """Fonction qui envoie un mail d'alerte automatique

        Args :
        elle prend en argument la position à actualiser

        Return :
        ne retourne rien, se contente d'expédier le mail
    """

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("PASSWORD")
    message = f"""Subject: Email from StocksDriver\n\n    

    Verifier vos positions. La derniere position en date est la suivante : 
    {name} : le {date} {sign} {quantity} {stock} {price} (PX= {px}) [validite jusqu'au {deadline}]

    This message is sent from Python."""

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
