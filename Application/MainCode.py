#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import pyodbc
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


# In[2]:


class welcomescreen(QDialog):
    def __init__(self):
        super(welcomescreen,self).__init__()
        loadUi("welcome_page.ui",self)
        self.signin.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)
    def gotologin(self):
        login = loginscreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotocreate(self):
        create = createAccscreen()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex()+1)
       

class loginscreen(QDialog):
    customer_id = None
    def __init__(self):
        super(loginscreen, self).__init__()
        loadUi("login.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
      # establish a connection to the database
        self.conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                                   "SERVER=.;"
                                   "DATABASE=E-Commerce;"
                                   "Trusted_Connection=yes;")
    
    def loginfunction(self):
        useremail = self.emailfield.text()
        userpassword = self.passwordfield.text()
        if len(useremail) == 0 or len(userpassword)==0:
            self.error.setText('Please, Fill all fields')
        else:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM customers WHERE email='{useremail}' AND password='{userpassword}'")
            result = cursor.fetchone()[0]
            cursor.close()

            if result == 1:
                #print("Login Successful")
                self.gotomainpage()
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT customer_id FROM customers WHERE email='{useremail}' AND password='{userpassword}'")
                customer_id = cursor.fetchone()[0]
                cursor.close()
                loginscreen.customer_id = customer_id

            else:
                self.error.setText('Invalid Username or Password')
              
    def gotomainpage(self):
        mainpage = mainpagescreen()
        widget.addWidget(mainpage)
        widget.setCurrentIndex(widget.currentIndex()+1)

class createAccscreen(QDialog):
    def __init__(self):
        super(createAccscreen,self).__init__()
        loadUi('createAccount.ui', self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.registerbutt.clicked.connect(self.signup)
        self.gotologpage.setEnabled(False)
        self.gotologpage.clicked.connect(self.continuetologin)
        self.conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                                   "SERVER=.;"
                                   "DATABASE=E-Commerce;"
                                   "Trusted_Connection=yes;")
    
    def continuetologin(self):
        self.close()
        self.login = loginscreen()
        self.login.show()
    def signup(self):
        email = self.emailfield.text()
        password = self.passwordfield.text()
        fname = self.fname.text()
        lname = self.lname.text()
        city = self.city.text()
        phone = self.mobile.text()
        gender = self.gender.text()
        age = self.age.text()
        country = self.country.text()
        zip = self.zip.text()

        if len(email) == 0 or len(password) == 0 or len(fname) == 0 or len(lname) == 0 or len(city) == 0 or len(gender) == 0 or len(phone) == 0 or len(age) == 0 or len(zip) == 0 or len(country) == 0:
            self.error.setText('Please, Fill all fields')
        else:
            cursor = self.conn.cursor()
            cursor.execute(f"customer_register'{fname}','{lname}','{gender}','{zip}','{age}','{country}','{city}','{password}','{email}','{phone}'")
            self.conn.commit()
            cursor.close()
            self.done.setText('Registeration Done. Lets continue!!')
            self.gotologpage.setEnabled(True)

class mainpagescreen(QDialog):
    def __init__(self):
        super(mainpagescreen,self).__init__()
        loadUi('mainpage.ui', self) 
        self.tableWidget.setColumnWidth(0,100)
        self.tableWidget.setColumnWidth(1,200)
        self.tableWidget.setColumnWidth(2,200)
        self.tableWidget.setColumnWidth(3,200)
        self.tableWidget.setColumnWidth(4,200)

        self.searchbutt.clicked.connect(self.product_search)
        self.history.clicked.connect(self.gotohistory)
        self.makeorder.clicked.connect(self.finishorder)
        self.submitrate.clicked.connect(self.ratefunction)

        self.cart = []
        self.cart_id = 0
        self.tableWidget.cellClicked.connect(self.add_to_cart)
        self.conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                                   "SERVER=.;"
                                   "DATABASE=E-Commerce;"
                                   "Trusted_Connection=yes;")
    def gotohistory(self):
        history = historyscreen()
        widget.addWidget(history)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def product_search(self):
            keyword = self.search.text()
            row = 0
            cursor = self.conn.cursor()
            if len(keyword) == 0:
                cursor.execute(" view_all_products")
            else:
                cursor.execute(f"search_by_product '{keyword}'")
            rows = cursor.fetchall()
            self.tableWidget.setRowCount(len(rows))
            for row_index in  rows:

                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row_index[0])))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(row_index[1]))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(row_index[2])))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(row_index[3]))
                self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(row_index[4]))
                row = row + 1
               
            cursor.close()
    def add_to_cart(self, row, column):
        product_id = self.tableWidget.item(row, 0).text()
        product_name = self.tableWidget.item(row, 1).text()
        customer_id = loginscreen.customer_id

        # Check if the product is already in the cart
        product_exists = False
        for i in range(self.cart_table.rowCount()):
            if self.cart_table.item(i, 1).text() == product_name:
                product_exists = True
                current_quantity = int(self.cart_table.item(i, 2).text())
                new_quantity = current_quantity + 1
                self.cart_table.setItem(i, 2, QTableWidgetItem(str(new_quantity)))

                cursor = self.conn.cursor()
                cursor.execute(f"change_quantity_of_certain_product '{customer_id}','{product_id}','{new_quantity}'")
                self.conn.commit()
                cursor.close()
                break

        if not product_exists:
            self.cart_id += 1
            self.cart_table.insertRow(self.cart_table.rowCount())
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 0, QTableWidgetItem(str(self.cart_id)))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 1, QTableWidgetItem(str(product_name)))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 2, QTableWidgetItem(str(1)))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 3, QTableWidgetItem(str(customer_id)))
            cursor = self.conn.cursor()
            cursor.execute(f"AddToCart '{product_id}', '{customer_id}', 1")
            self.conn.commit()
            cursor.close()
  ############# making order from cart #########################################
    def finishorder(self):
        customer_id = loginscreen.customer_id
        city = self.city.currentText()
        payment = self.payment.currentText()
        cursor = self.conn.cursor()
        cursor.execute(f"MakeOrder '{customer_id}','{payment}','{city}'")
        self.conn.commit()
        cursor.close()
        cursor = self.conn.cursor()
        cursor.execute(f"select sub_total from orders where customer_id ='{customer_id}' and order_id = (select max(order_id) from orders where customer_id = '{customer_id}')")
        subtotal = str(cursor.fetchone()[0])
        cursor.execute(f"select total_tax from orders where customer_id ='{customer_id}' and order_id = (select max(order_id) from orders where customer_id = '{customer_id}')")
        tax = str(cursor.fetchone()[0])
        cursor.execute(f"select total_freight from orders where customer_id ='{customer_id}' and order_id = (select max(order_id) from orders where customer_id = '{customer_id}')")
        freight = str(cursor.fetchone()[0])
        cursor.execute(f"select total_due from orders where customer_id ='{customer_id}' and order_id = (select max(order_id) from orders where customer_id = '{customer_id}')")
        total_due = str(cursor.fetchone()[0])
        cursor.close()
        text1 = self.subtotal.toPlainText()
        self.subtotal.setText(self.subtotal.toPlainText()+'  '+subtotal)
        self.tax.setText(self.tax.toPlainText()+'  '+tax)
        self.freight.setText(self.freight.toPlainText()+'  '+freight)
        self.totalamount.setText(self.totalamount.toPlainText()+'  '+total_due)
        self.feedback.setText('Succefull Order. Alwayes At Your Service')
        ############# Rating ################
    def ratefunction(self):
        delivery = self.delivery.currentText()
        service = self.service.currentText()
        quality= self.quality.currentText()
        overall = self.overall.currentText()
        loyality = self.loyality.currentText()
        customer_id = loginscreen.customer_id

        cursor = self.conn.cursor()
        cursor.execute(f"rating_survey '{customer_id}','{overall}','{delivery}','{service}','{loyality}','{quality}'")
        self.conn.commit()
        cursor.close()


            
class historyscreen(QDialog):
    def __init__(self):
        super(historyscreen,self).__init__()
        loadUi('viewhistory.ui', self) 
        customer_id =  loginscreen.customer_id
        self.backfromhistory.clicked.connect(self.gotomainpage)
        self.conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};"
                                   "SERVER=.;"
                                   "DATABASE=E-Commerce;"
                                   "Trusted_Connection=yes;")
        cursor = self.conn.cursor()                           
        cursor.execute(f"order_history '{customer_id}'")
        rows = cursor.fetchall()
        self.tableWidget.setRowCount(len(rows))
        row = 0
        for row_index in  rows:

                self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row_index[0])))
                self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(row_index[1])))
                self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(str(row_index[2])))
                self.tableWidget.setItem(row, 3, QtWidgets.QTableWidgetItem(str(row_index[3])))
                self.tableWidget.setItem(row, 4, QtWidgets.QTableWidgetItem(str(row_index[4])))
                self.tableWidget.setItem(row, 5, QtWidgets.QTableWidgetItem(row_index[5]))
                self.tableWidget.setItem(row, 6, QtWidgets.QTableWidgetItem(row_index[6]))
                self.tableWidget.setItem(row, 7, QtWidgets.QTableWidgetItem(row_index[7]))
                self.tableWidget.setItem(row, 8, QtWidgets.QTableWidgetItem(str(row_index[8])))
                self.tableWidget.setItem(row, 9, QtWidgets.QTableWidgetItem(str(row_index[9])))
                
                row = row + 1
    QtCore.pyqtSlot()
    def gotomainpage(self):
        self.close()
        self.mainpage = mainpagescreen()
        self.mainpage.show()

        
##main
app = QApplication(sys.argv)
welcome = welcomescreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print('exiting')


# In[2]:



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cart = []
        self.cart_id = 0

        # UI setup code here

        self.product_table.cellClicked.connect(self.add_to_cart)
       
    def add_to_cart(self, row, column):
        product_id = self.product_table.item(row, 0).text()
        product_name = self.product_table.item(row, 1).text()

        # Check if the product is already in the cart
        product_exists = False
        for i in range(self.cart_table.rowCount()):
            if self.cart_table.item(i, 1).text() == product_name:
                product_exists = True
                current_quantity = int(self.cart_table.item(i, 2).text())
                self.cart_table.setItem(i, 2, QTableWidgetItem(str(current_quantity + 1)))
                break

        if not product_exists:
            self.cart_id += 1
            self.cart_table.insertRow(self.cart_table.rowCount())
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 0, QTableWidgetItem(str(self.cart_id)))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 1, QTableWidgetItem(product_name))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 2, QTableWidgetItem(str(1)))
            self.cart_table.setItem(self.cart_table.rowCount() - 1, 3, QTableWidgetItem(str(customer_id)))

