"""
fichier de test qui vérifie certaines conditions dans le répertoire courant
"""

import unittest
import os


class TestChromedriver(unittest.TestCase):

    def test_isfile(self):
        self.assertTrue(os.path.isfile('chromedriver.exe'))     # true
        self.assertFalse(os.path.isfile('chromedriver.zip'))     # false


if __name__ == '__main__':
    unittest.main()
