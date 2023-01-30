#Otevřít nedávné (JSON)
import json
from operator import le
from re import X

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QLineEdit, QFileDialog, QMessageBox, QFontDialog, \
    QColorDialog, QShortcut, QAction, QLabel
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtGui import QKeySequence, QIntValidator
import os
import paramiko
import subprocess


class Instructions_UI(QMainWindow): # Okno s návodem
    def __init__(self):
        super(Instructions_UI, self).__init__()
        uic.loadUi("instructions.ui", self)
        #Titulek okna
        self.setWindowTitle("Návod")  
        self.show()

class About_UI(QMainWindow): # Okno s informaceni o programu
    def __init__(self):
        super(About_UI, self).__init__()
        uic.loadUi("about.ui", self)
        #Titulek okna
        self.setWindowTitle("O programu")  
        self.show()


class Main_UI(QMainWindow): # Hlavní okno
    def __init__(self):
        super(Main_UI, self).__init__()
        uic.loadUi("main.ui", self)
 
        #Titulek okna
        self.setWindowTitle("Vzdálený přístup")  
        #Funkce po stisknutí tlačítka
        self.action_instructions.triggered.connect(self.instructions)
        self.action_about.triggered.connect(self.about)

        self.pushButton_set_pins.clicked.connect(self.change_pins)
        self.pushButton_set.clicked.connect(self.set_output)

        # Stavová informace ve statusbaru
        self.status_info = QLabel()
        self.status_info.setText(f'Připojeno k {username}@{host}')
        self.statusbar.addPermanentWidget(self.status_info)
        self.pushButton_set.setEnabled(False)

        # Vytvoření seznamu pro vstupní piny
        self.pin_inputs = [
            self.lineEdit_pin_A,
            self.lineEdit_pin_B,
            self.lineEdit_pin_C
        ]
        # Seznam dat vstupních pinů
        self.pins = []

        # Povolení jen čísel jak výstupní piny
        self.onlyInt = QIntValidator(0,27)
        for i in self.pin_inputs:
            i.setValidator(self.onlyInt)

        # Vytvoření seznamu grafického výstupu
        self.output_labels = [
            self.label_1,
            self.label_2,
            self.label_3
        ]
        

        self.show()


    def instructions(self):
        self.instructions_window = Instructions_UI()

    def about(self):
        self.about_window = About_UI()

    def change_pins(self): # Nastavení výstupních pinů
        self.pins = [] # Vyčištění seznamu dat pinů
        self.error = False # Chyba v pinech
        for i in range(len(self.pin_inputs)):
            text = self.pin_inputs[i].text() # Číslo ze vstupu
            if text: # Není-li text ""
                text = int(text) # Převod na celé číslo
                if text > 27 or text in self.pins: # Pinů je jen 27 a jeden nemůže být použit vícekrát
                    self.pin_inputs[i].setStyleSheet("background-color: red;") # Pole s chybou budou označena červeně
                    self.error = True
                else:
                    self.pin_inputs[i].setStyleSheet("background-color: lightgreen;") # Pole bez chyby budou označeny zeleně
                self.pins.append(text) # Přidání hodnoty do seznamu
            else:
                self.pin_inputs[i].setStyleSheet("background-color: red;")
                self.error = True
        
        # Nevyskytuje-li se chyba, tlačítko "Nastavit piny" může být povoleno
        if not self.error:
            self.pushButton_set.setEnabled(True)
        else:
            self.pushButton_set.setEnabled(False)

    def set_output(self): # Nastavení výstupu
        global window
        output = self.spinBox_value.value()

        output = self.binar(output)
        args = f'{self.pins[0]} {self.pins[1]} {self.pins[2]} '
        
        for i in range(len(output)):
            args += str(output[i]) + " "
            if output[i]:
                self.output_labels[i].setStyleSheet("background-color: lightgreen;") # Logická 1
            else:
                self.output_labels[i].setStyleSheet("background-color: red;") # Logická 0
        
        command = f'python3 set_output.py {args[:-1]}'
        
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            if stdout.channel.recv_exit_status() != 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Chyba")
                msg.setInformativeText("Nespecifikovaná chyba")
                msg.setText(str(stderr))
                msg.exec_()
            
            
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Chyba")
            msg.setInformativeText("Možná už nejste připojeni")
            msg.setText("Zkontrolujte připojení")       
            msg.exec_()
            
            self.close()
            del self
            window = Login_UI() # Otevření přihlašovacího okna
            

    def binar(self, number):
        x = list(format(number, "#05b")[2:])
        for i in range(len(x)):
            x[i] = int(x[i])
        return x

class Login_UI(QMainWindow): # Přihlašovací dialog
    def __init__(self):
        super(Login_UI, self).__init__()
        uic.loadUi("login.ui", self)
 
        #Titulek okna
        self.setWindowTitle("Přihlášení")  
        #Funkce po stisknutí tlačítka
        self.login_pushButton.clicked.connect(self.login)

        #Klávesová zkratka pro Enter
        self.shortcut_login = QShortcut(QKeySequence('Return'), self)
        self.shortcut_login.activated.connect(self.login)

        self.show()


    def login(self): # Přihlášení, připojení k RPI
        global port, host, username, password, ssh, window
        port = 22
        host = self.lineEdit_host.text()
        username = self.lineEdit_user.text()
        password = self.lineEdit_password.text()

        #print(host, username, password, port)
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, port, username, password)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Chyba")
            msg.setInformativeText("Spojení nemohlo být navázáno")
            msg.setText("Zkontrolujte vyplněná data")       
            msg.setDetailedText("IP adresa, jméno uživatele, nebo heslo jsou chybné.")
            msg.exec_()
            return
            
        stdin, stdout, stderr = ssh.exec_command("ls")
        if not 'set_output.py\n' in stdout.readlines():
            ftp_client=ssh.open_sftp()
            ftp_client.put('set_output.py',f'/home/{username}/set_output.py')
            ftp_client.close()
        self.close() # Zavření okna
        del self
        window = Main_UI() # Otevření hlavního okna


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Login_UI() # Spuštění přihlašovacího okna
    app.exec_()