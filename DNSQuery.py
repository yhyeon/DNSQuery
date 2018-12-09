#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from struct import *
import dns.resolver
import csv
import pytz
from datetime import datetime, timedelta
import threading
import time
import os
import subprocess
from subprocess import check_output
import signal

pst = os.getcwd()+"/"+sys.argv[0] # get full path of the current file

proc = subprocess.Popen(['nohup', 'python3', pst], stdout = open('/dev/null', 'w'), stderr=open('logfile.log', 'a'), preexec_fn=os.setpgrp) # run another process to keep this tool running even after the current terminal session being terminated

class Ui_self(QWidget):
	global qip
	global ctime
	global rev
	global tz
	tz = pytz.timezone('Asia/Seoul') # set timezone

	def utc_kor(self, utc_dt):
		dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(tz) # get current time KST+09
		return tz.normalize(dt)

	def time(self, utc_dt):
		return self.utc_kor(utc_dt).strftime('%Y-%m-%d %H:%M:%S.%f %Z%z') # convert time format

	def submit_clicked(self):

		global qdns
		qdns = self.dnsinput.text() # get user input from self.dnsinput below
		if len(qdns) == 0: # if nothing specified for the DNS address to query,
			QMessageBox.about(self, "Notice", "Please specify the DNS name to query.") # a message box will be shown up
			return Ui_self() # return and no progress made

		global r_time_h
		global r_time_m
		global r_time_s
		r_time_h = self.lineEdit_2.text() # get user input from self.lineEdit_2 below
		r_time_m = self.lineEdit_4.text() # get user input from self.lineEdit_4 below
		r_time_s = self.lineEdit_6.text() # get user input from self.lineEdit_6 below
		if r_time_h=="" and r_time_m=="" and r_time_s=="": # if nothing specified for query schedule,
			QMessageBox.about(self, "Notice", "Query will be conducted every hour.") # a message box will be show up
			r_time_h = 1 # and the query will be conducted per hour
#		print(len(r_time_h),len(r_time_m),len(r_time_s))

		if not r_time_h == "": # if any user input exists for hour-based query,
			r_time_h = int(r_time_h) * 3600 # user input number * 3600
		else: # else,
			r_time_h = 0 # the value set to 0

		if not r_time_m == "": # if any user input exists for minute-based query,
			r_time_m = int(r_time_m) * 60 # user input number * 60
		else: # else,
			r_time_m = 0 # the variable set to 0

		if not r_time_s == "": # if any user input exists for second-based query,
			r_time_s = int(r_time_s) * 1 # the variable is equal to user input
		else: # else,
			r_time_s = 0 # the variable set to 0

		r_time = r_time_h + r_time_m + r_time_s
		#print(r_time)

		global csv_dir
		csv_dir = self.lineEdit_8.text() # get user input from self.lineEdit_8
		if len(csv_dir) == 0: # if nothing specified for csv dir,
			QMessageBox.about(self, "Notice", "A csv file 'dns_ip.csv' will be saved in the current directory") # a message box will be shown up
			csv_dir = os.getcwd() + "/dns_ip.csv" # and the csv file will be saved in the ./dns_ip.csv
		print(csv_dir)

		r = dns.resolver.Resolver()
		r.nameservers = ['8.8.8.8'] # set (primary) resolver
		r.timeout = 1 # set timeout
		r.lifetime = 1 # set lifetime
		dns.resolver.override_system_resolver(r) # ignore system resolver configuration
	

		try: 
			ip = r.query(qdns, 'a') # conduct query

			for i in ip:

				#print(self.time(datetime.utcnow()), qdns, i, r.nameservers[0])
				print(self.time(datetime.utcnow()))
				print(qdns)
				print(i)
				print(r.nameservers[0])


		except:
			r.nameservers = ['208.67.222.222'] # set (secondary) resolver
			dns.resolver.override_system_resolver(r) # ignore system resolver configuration
			ip = r.query(qdns, 'a') # conduct query
			for i in ip:

				print(self.time(datetime.utcnow()))
				print(qdns)
				print(i)
				print(r.nameservers[0])
		
#		csvfile = csv_dir+"/dns_ip2.csv"
#		csvfile = csv_dir

		while True:
			with open(csv_dir, "a", encoding='utf-8') as f_out: # open csv file as f_out in append mode
				with open(csv_dir, 'r', encoding='utf-8') as f_in: # open csv file as f_in in read mode
#					writer = csv.writer(f_out, delimiter = ",")
					numline = len(f_in.readlines()) # count line numbers
					print(numline)

					if numline == 0: # if there is no data in the file,
						fields = ('Num','DateTime','Domain','IP','Resolver') # set field names
						wr = csv.DictWriter(f_out, fieldnames=fields, lineterminator = '\n')
						wr.writeheader() # write fields in the header 
						wr.writerow({'Num':1, 'DateTime':self.time(datetime.utcnow()), 'Domain':qdns, 'IP':i, 'Resolver':r.nameservers[0]}) # write row with relevant data
						f_in.close() # close f_in
						f_out.close() # close f_out
						time.sleep(r_time) # sleep till next query schedule
					else: # else,
						wr = csv.writer(f_out)
						wr.writerow([(numline),self.time(datetime.utcnow()),qdns,i,r.nameservers[0]]) # write row with relevant data
						f_in.close() # close f_in
						f_out.close() # close f_out
						time.sleep(r_time) # sleep till next query schedule



	def __init__(self):
		super().__init__()

		self.setupUi()

	def setupUi(self):
		self.setObjectName("DNSQuery") # set its name
		self.resize(274, 150) # set its size
		self.gridLayout = QGridLayout(self)
		self.gridLayout.setObjectName("gridLayout")
		self.selfLayout_2 = QFormLayout()
		self.selfLayout_2.setObjectName("selfLayout_2")
		spacerItem = QSpacerItem(80, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
		self.selfLayout_2.setItem(0, QFormLayout.LabelRole, spacerItem)

		hidebtn = QPushButton('Hide', self)
		hidebtn.setToolTip('Hide the programme')
		hidebtn.clicked.connect(self.hide) # connect hide button to hide function
		self.selfLayout_2.setWidget(0, QFormLayout.FieldRole, hidebtn)
		self.selfLayout_2.setItem(0, QFormLayout.LabelRole, spacerItem)
		self.gridLayout.addLayout(self.selfLayout_2, 0, 0, 1, 3)

		clsbtn = QPushButton('Close', self)
		clsbtn.setToolTip('Close this programme')
		clsbtn.clicked.connect(self.close) # connect close button to close function
		self.gridLayout.addWidget(clsbtn, 0, 3, 1, 1)

		line_dns = QLineEdit('DNS', self)
		line_dns.setStyleSheet("background-color: gainsboro") # set background color
		line_dns.setAlignment(Qt.AlignCenter) # set text alignment
		line_dns.setMaximumSize(QSize(60, 16777215))
		line_dns.setReadOnly(True) # set read only
		line_dns.setObjectName("line_dns")
		self.gridLayout.addWidget(line_dns, 1, 0, 1, 1)

		self.dnsinput = QLineEdit(self)
		self.dnsinput.setToolTip('Please enter the DNS name to query.')
		self.dnsinput.setObjectName("dnsinput")
		self.gridLayout.addWidget(self.dnsinput, 1, 1, 1, 2)

		self.gridLayout_3 = QGridLayout()
		self.gridLayout_3.setObjectName("gridLayout_3")
		font = QFont()
		font.setPointSize(8) # set font size
		self.lineEdit_3 = QLineEdit('HH', self)
		self.lineEdit_3.setFont(font)
		self.lineEdit_3.setStyleSheet("background-color: gainsboro") # set background color
		self.lineEdit_3.setMaximumSize(QSize(25, 20))
		self.lineEdit_3.setAlignment(Qt.AlignCenter) # set text alignment
		self.lineEdit_3.setReadOnly(True)
		self.lineEdit_3.setObjectName("lineEdit_3")
		self.gridLayout_3.addWidget(self.lineEdit_3, 0, 1, 1, 1)
		self.lineEdit_2 = QLineEdit(self)
		self.lineEdit_2.setMaximumSize(QSize(25, 20))
		self.lineEdit_2.setObjectName("lineEdit_2")
		self.gridLayout_3.addWidget(self.lineEdit_2, 0, 0, 1, 1)
		self.lineEdit_6 = QLineEdit(self)
		self.lineEdit_6.setMaximumSize(QSize(25, 20))
		self.lineEdit_6.setObjectName("lineEdit_6")
		self.gridLayout_3.addWidget(self.lineEdit_6, 0, 4, 1, 1)
		self.lineEdit_4 = QLineEdit(self)
		self.lineEdit_4.setMaximumSize(QSize(25, 20))
		self.lineEdit_4.setObjectName("lineEdit_4")
		self.gridLayout_3.addWidget(self.lineEdit_4, 0, 2, 1, 1)
		self.lineEdit_5 = QLineEdit('mm', self)
		self.lineEdit_5.setStyleSheet("background-color: gainsboro") # set background color
		self.lineEdit_5.setMaximumSize(QSize(25, 20))
		self.lineEdit_5.setFont(font)
		self.lineEdit_5.setCursorPosition(0)
		self.lineEdit_5.setAlignment(Qt.AlignCenter) # set text alignment
		self.lineEdit_5.setReadOnly(True)
		self.lineEdit_5.setObjectName("lineEdit_5")
		self.gridLayout_3.addWidget(self.lineEdit_5, 0, 3, 1, 1)
		self.lineEdit_7 = QLineEdit('ss',self)
		self.lineEdit_7.setFont(font)
		self.lineEdit_7.setStyleSheet("background-color: gainsboro") # set background color
		self.lineEdit_7.setMaximumSize(QSize(25, 20))
		self.lineEdit_7.setAutoFillBackground(False)
		self.lineEdit_7.setAlignment(Qt.AlignCenter) # set text alignment
		self.lineEdit_7.setReadOnly(True)
		self.lineEdit_7.setObjectName("lineEdit_7")
		self.gridLayout_3.addWidget(self.lineEdit_7, 0, 5, 1, 1)
		self.gridLayout.addLayout(self.gridLayout_3, 2, 0, 1, 3)

		self.r_querybtn = QPushButton('R. Query',self)
		self.r_querybtn.setStyleSheet("background-color: steelblue") # set background color
		self.r_querybtn.clicked.connect(self.submit_clicked) # connect r_query button to submit.submit_clicked
		self.r_querybtn.setMinimumSize(QSize(75, 80))
		self.r_querybtn.setMaximumSize(QSize(75, 80))
		self.r_querybtn.setBaseSize(QSize(75, 80))
		self.r_querybtn.setObjectName("r_querybtn")
		self.gridLayout.addWidget(self.r_querybtn, 1, 3, 3, 1)
		self.lineEdit_10 = QLineEdit('CSV_Dir',self)
		self.lineEdit_10.setStyleSheet("background-color: gainsboro") # set background color
		self.lineEdit_10.setReadOnly(True) # set read only
		self.lineEdit_10.setMinimumSize(QSize(60, 0))
		self.lineEdit_10.setObjectName("lineEdit_10")
		self.gridLayout.addWidget(self.lineEdit_10, 3, 0, 1, 2)
		self.lineEdit_8 = QLineEdit(self)
		self.lineEdit_8.setObjectName("lineEdit_8")
		self.gridLayout.addWidget(self.lineEdit_8, 3, 2, 1, 1)


if __name__ == "__main__":

	app = QApplication(sys.argv)

	ui = Ui_self()
	ui.move(200, 100) # set its location
	ui.setWindowTitle('DNSQuery') # set its window title
	ui.show()
	sys.exit(app.exec_())

		

# timestamp reference: https://stackoverflow.com/questions/4563272/convert-a-python-utc-datetime-to-a-local-datetime-using-only-python-standard-lib

# subproc reference: https://stackoverflow.com/questions/6011235/run-a-program-from-python-and-have-it-continue-to-run-after-the-script-is-kille