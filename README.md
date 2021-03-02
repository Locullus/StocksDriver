# StocksDriver
utilisation d'un webdriver pour calculer des prises de positions sur un tracker d'indice.

Une fois le fichier Trading_system.py lancé, le programme va dans un premier temps mettre à jour son fichier de données historiques puis gérer les différentes positions.
En fonction des niveaux atteints, les positions seront soit soldées, soit ouvertes, soit ajustées à la hausse ou à la baisse.
Pour l'instant ce programme n'en est qu'à la reconnaissance des niveaux d'interventions, pas encore à la prise de positions autonome - ce qui sera le but final.
L'objectif intermédiaire est de développer un système d'alerte par courrier électronique qui précisera les niveaux d'interventions.
