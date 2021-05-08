import numpy as np
import pandas as pd
import scipy.signal as sig
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication,QMainWindow
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from gui import Ui_MainWindow


class ApplicationWindow(QMainWindow):

	def __init__(self, parent: QWidget = None):
		# uic boilerplate
		super(ApplicationWindow, self).__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

	 
		###################################### Connection aux Events ######################################
		self.ui.UpdatePlot.clicked.connect(self.graph_control_update_plot)
		self.ui.LoadData.clicked.connect(self.load_data_plot)

		self.ui.UpdatePlot.setEnabled(False)
		self.ui.LoadData.setEnabled(True)
		###################################################################################################


		################################### Paramètres de Visualisation  ###################################
		self.ui.ecg_before.setBackground(background="w")
		self.ui.ecg_before.setMenuEnabled(True)
		self.ui.ecg_before.setMouseEnabled(x=True, y=True)
		self.ui.ecg_before.showGrid(x=True, y=True)

		self.ui.ecg_after.setBackground(background="w")
		self.ui.ecg_after.addLegend(True)
		self.ui.ecg_after.setMenuEnabled(True)
		self.ui.ecg_after.setMouseEnabled(x=True, y=True)
		self.ui.ecg_after.showGrid(x=True, y=True)
		####################################################################################################

	###################################################################################################

	############### Mise à jour ###############
	def load_data(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Fichiers .csv (*.csv);;Python Files (*.py)", options=options)
		if fileName:
			return fileName
	

	@pyqtSlot(name="load_data_plot")
	def load_data_plot(self):
		
		#####┌ Récupération du chemin du fichier data #####
		file_Name = self.load_data()
		###################################################

		###### Lecture de la data #####
		res=pd.read_csv(file_Name)
		###############################
		
		############ Nombre d'échantillons ############
		global input_max
		################################################

		############ Conversion en matrice ############
		matrix = res.to_numpy()
		data = matrix[0:1500,1]
		###############################################
		global x #Signal d'entrée
		############ Conversion en Float ############
		x = data[:]
		x = x.astype("float")
		#############################################

		############ Normalisation des données ############
		x = (x - np.mean(x)) / np.std(x) 
		###################################################
		input_max=max(x)
		######################## Visualisation ########################
		if_pen = pg.mkPen(color='b', width=3)
		self.ui.ecg_before.clear()
		self.ui.ecg_after.clear()
		self.ui.ecg_before.plot(x[0:3000], pen=if_pen)
		self.ui.ecg_before.setLabel('bottom', "Temps(s)")
		self.ui.ecg_before.setLabel('left', "Amplitude (mV)")
		self.ui.ecg_before.setTitle("ECG Brutes") 
		self.ui.ecg_before.show()
		self.ui.UpdatePlot.setEnabled(True)
		################################################################



	@pyqtSlot(name="graph_control_update_plot")
	def graph_control_update_plot(self):

		self.ui.LoadData.setEnabled(False)
		self.ui.ecg_after.clear()
		self.ui.ecg_after.setLabel('bottom', "Temps(s)")
		self.ui.ecg_after.setLabel('left', "Amplitude (mV)")
		self.ui.ecg_after.setTitle("ECG Filtrés")
		if_pen = pg.mkPen(color='g', width=3)
		
		###################################### Paramètres ######################################

		global F # Fréquence d'échantillonnage
		global N # Largeur du QRS

		F= self.ui.F_ech.value() # Récupération de la Fréquence d'échantillonnage
		N= self.ui.qrs_width.value() # Récupération de Largeur du QRS

		##########################################################################################
		
		####################################################################################################################
		################################################ Filtre passe-bande ################################################
		####################################################################################################################
		
		################### Filtrage passe-bas ###################
		x1 = sig.lfilter([1,0,0,0,0,0,-2,0,0,0,0,0,1],[1,-2,1],x)
		##########################################################

		###################################### Filtrage passe-haut ######################################
		x2 = sig.lfilter([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,1],x1)
		#################################################################################################

		####################################################################################################################
		
		###################################### Filtrage dérivatif ######################################
		x3 = np.zeros(x.shape)
		for i in range(2,len(x2)-2):
			x3[i] = (-1*x2[i-2] -2*x2[i-1] + 2*x2[i+1] + x2[i+2])/(8*F)
		################################################################################################

		################### Signal carré ###################
		x4 = x3*x3
		#####################################################

		################### Signal final ###################
		y = np.zeros(x.shape)
		for i in range(N,len(x4)-N):
			for j in range(N):
				y[i]+= x4[i-j]
		y = y/N
		#####################################################

		######################## Calcul des pics R ########################
		r_peaks,_=sig.find_peaks(y,height=max(y)*0.70,distance=1)
		r_peaks_values=[y[i] for i in r_peaks]
		###################################################################
		
		######################### Calcul des points S ######################### 
		num_peak=r_peaks.shape[0]
		s_points=list()
		for index in range(num_peak):
			i=r_peaks[index]
			cnt=i
			if cnt+1>=y.shape[0]:
				break
			while y[cnt]>y[cnt+1]:
				cnt+=1
				if cnt>=y.shape[0]:
					break
			s_points.append(cnt)
		s_points_values=[y[i] for i in s_points]
		##########################################################################
		
		######################### Calcul des points Q ######################### 		
		q_points=list()
		for index in range(num_peak):
			i=r_peaks[index]
			cnt=i
			if cnt-1<0:
				break
			while y[cnt]>y[cnt-1]:
				cnt-=1
				if cnt<0:
					break
			q_points.append(cnt)
		q_points_values=[y[i] for i in q_points]	  
		##########################################################################

		############ Calcul du battement cardiaque moyen et classification ############ 
		diff=[]
		for j in range(len(r_peaks)-1):
			diff.append(r_peaks[j+1]-r_peaks[j])
		heartrate_avg=abs(np.mean(diff))

		bpm = (60000 / (2*heartrate_avg)) 
		self.ui.heartrate.setText(str(round(bpm)))
		if (bpm>100):
			self.ui.result.setText("Condition Cardiaque : Tachycardie")
		elif(bpm<60):
			self.ui.result.setText("Condition Cardiaque : Bradycardie")
		else:
			self.ui.result.setText ("Condition Cardiaque : Normale")    
		################################################################################
		 
		######################### Visualisation des résultats #########################
		self.ui.ecg_after.plot(y,pen=if_pen)
		self.ui.ecg_after.plot(r_peaks,r_peaks_values, pen=None,symbol='o',symbolBrush= pg.mkBrush(255,0,0),name='Q Peaks') 
		self.ui.ecg_after.plot(s_points,s_points_values,pen=None,symbol='o',symbolBrush= pg.mkBrush(0,0,255),name='S Points')
		self.ui.ecg_after.plot(q_points,q_points_values,pen=None,symbol='o',symbolBrush= pg.mkBrush(255,255,0),name='R Points')
		self.ui.ecg_after.show()
		################################################################################
		self.ui.LoadData.setEnabled(True)
	#############################################


def main():
	app = QApplication(sys.argv)
	application = ApplicationWindow()
	application.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	# Initialize application
	main()
