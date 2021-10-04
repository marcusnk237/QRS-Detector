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

	 
		###################################### Connection to the  Events ##################################
		self.ui.UpdatePlot.clicked.connect(self.graph_control_update_plot)
		self.ui.LoadData.clicked.connect(self.load_data_plot)

		self.ui.UpdatePlot.setEnabled(False)
		self.ui.LoadData.setEnabled(True)
		###################################################################################################


		################################### Display paramters ###################################
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
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "",".csv (*.csv);;Python Files (*.py)", options=options)
		if fileName:
			return fileName
	

	@pyqtSlot(name="load_data_plot")
	def load_data_plot(self):
		
		################# Get data path #################
		file_Name = self.load_data()
		#################################################

		########### Read data ##########
		res=pd.read_csv(file_Name)
		################################
		
		############ Samples numbers ############
		global input_max
		################################################

		############ Convert into a matrix ############
		matrix = res.to_numpy()
		data = matrix[0:1500,1]
		###############################################
		global x # Input signal
		############ Convert into a float ###########
		x = data[:]
		x = x.astype("float")
		#############################################

		############ Data normalization ############
		x = (x - np.mean(x)) / np.std(x) 
		###################################################
		input_max=max(x)
		######################## Visualization ########################
		if_pen = pg.mkPen(color='b', width=3)
		self.ui.ecg_before.clear()
		self.ui.ecg_after.clear()
		self.ui.ecg_before.plot(x[0:3000], pen=if_pen)
		self.ui.ecg_before.setLabel('bottom', "Time(s)")
		self.ui.ecg_before.setLabel('left', "Amplitude (mV)")
		self.ui.ecg_before.setTitle("ECG raw data ") 
		self.ui.ecg_before.show()
		self.ui.UpdatePlot.setEnabled(True)
		################################################################



	@pyqtSlot(name="graph_control_update_plot")
	def graph_control_update_plot(self):

		self.ui.LoadData.setEnabled(False)
		self.ui.ecg_after.clear()
		self.ui.ecg_after.setLabel('bottom', "Time (s)")
		self.ui.ecg_after.setLabel('left', "Amplitude (mV)")
		self.ui.ecg_after.setTitle("Filtered ECG")
		if_pen = pg.mkPen(color='g', width=3)
		
		###################################### Parameters ######################################

		global F # Sampling Frequency
		global N # QRS Width

		F= self.ui.F_ech.value() # Get sampling fresuency value
		N= self.ui.qrs_width.value() # Get QRS width

		##########################################################################################
		
		####################################################################################################################
		################################################ Bandpass filter ###################################################
		####################################################################################################################
		
		################### Low-pass filter #####################
		x1 = sig.lfilter([1,0,0,0,0,0,-2,0,0,0,0,0,1],[1,-2,1],x)
		##########################################################

		###################################### Highpass filter ##########################################
		x2 = sig.lfilter([1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,1],x1)
		#################################################################################################

		####################################################################################################################
		
		###################################### Derivative filter ######################################
		x3 = np.zeros(x.shape)
		for i in range(2,len(x2)-2):
			x3[i] = (-1*x2[i-2] -2*x2[i-1] + 2*x2[i+1] + x2[i+2])/(8*F)
		################################################################################################

		################### Square signal ###################
		x4 = x3*x3
		#####################################################

		################### Final signal ###################
		y = np.zeros(x.shape)
		for i in range(N,len(x4)-N):
			for j in range(N):
				y[i]+= x4[i-j]
		y = y/N
		#####################################################

		######################## R points computation ########################
		r_peaks,_=sig.find_peaks(y,height=max(y)*0.70,distance=1)
		r_peaks_values=[y[i] for i in r_peaks]
		###################################################################
		
		######################### S points computation ######################### 
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
		
		######################### Q points computation ######################### 		
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

		############ Average heart rate and classification ############ 
		diff=[]
		for j in range(len(r_peaks)-1):
			diff.append(r_peaks[j+1]-r_peaks[j])
		heartrate_avg=abs(np.mean(diff))

		bpm = (60000 / (2*heartrate_avg)) 
		self.ui.heartrate.setText(str(round(bpm)))
		if (bpm>100):
			self.ui.result.setText("Heart condition : Tachycardy")
		elif(bpm<60):
			self.ui.result.setText("Heart condition : Bradycardy")
		else:
			self.ui.result.setText ("Heart condition : Normal")    
		################################################################################
		 
		################################################## Display results ##################################################
		self.ui.ecg_after.plot(y,pen=if_pen)
		self.ui.ecg_after.plot(r_peaks,r_peaks_values, pen=None,symbol='o',symbolBrush= pg.mkBrush(255,0,0),name='Q Peaks') 
		self.ui.ecg_after.plot(s_points,s_points_values,pen=None,symbol='o',symbolBrush= pg.mkBrush(0,0,255),name='S Points')
		self.ui.ecg_after.plot(q_points,q_points_values,pen=None,symbol='o',symbolBrush= pg.mkBrush(255,255,0),name='R Points')
		self.ui.ecg_after.show()
		#######################################################################################################################
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
