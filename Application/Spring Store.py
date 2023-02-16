import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
import welcom_page
import login
import creatAccount
import mainpage
import viewhistory
import rating
import MainCode

app = QApplication(sys.argv)

welcom_page = QDialog()
welcom_page.loadUi("welcom_page.py", welcom_page)

login = QDialog()
login.loadUi("login.py", login)

creatacc = QDialog()
creatacc.loadUi("creatAccount.py", creatAccount)

mainpage = QDialog()
mainpage.loadUi("mainpage.py", mainpage)

viewhistory = QDialog()
viewhistory.loadUi("viewhistory.py", viewhistory)

rating = QDialog()
rating.loadUi("rating.py", rating)

ecommerce.show()
sys.exit(app.exec_())