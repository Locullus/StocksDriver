# StocksDriver
utilisation d'un webdriver pour calculer des prises de positions sur un tracker d'indice.

Ce programme utilisant le navigateur Chrome de Google en mode automatique, il nécessite au préalable l'installation du ChromeDriver de Selenium sur votre système. Veuillez à télécharger la version correspondant à votre navigateur et à le garder à jour régulièrement.
Si les versions viennent à différer - ce qui arrive lorsqu'une mise à jour est nécessaire - téléchargez simplement celle qui se rapporte à votre navigateur Chrome.

Vous la trouverez à cette adresse :
  https://chromedriver.chromium.org/downloads
  
Pour remplacer une version par une autre, décompressez votre fichier directement dans le répertoire d'origine du téléchargement précédent. Le nouveau fichier remplacera automatiquement l'ancien devenu inutile.

Vous pouvez également visiter celle-ci :
  http://chromedriver.storage.googleapis.com/index.html
  
  
Une fois le WebDriver installé, ajoutez son chemin d'accès au PATH de vos variables d'environnement. Ceci permettra à ChromeDriver de fonctionner en mode automatisé.
Ne reste plus qu'à installer le package Selenium. Cela peut-être fait très simplement en tapant dans console :

  pip install selenium

Pour de plus amples informations sur le fonctionnement de Selenium, vous pouvez vous reportez à la documentation en ligne :

  https://selenium-python.readthedocs.io/
  
