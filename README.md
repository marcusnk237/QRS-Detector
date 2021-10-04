# QRS-Detector
QRS complex detector 
This graphical interface allows to determine the Q,R,S parameters of an ECG signal.
The button "Load ECG" allows to load our electrocardiogram.
The "Detection" button will first filter the signal using the Pan-Tompkins algorithm.

Once this is done, the Q, R, S points of the signal will be detected. From them, the program will calculate the average heartbeat per minute and make a diagnosis:
 - If the beat is higher than 100, it is a case of Tachycardia
 - If the beat is lower than 60, we are in front of a Bradycardia
 - Otherwise, the beat is normal.

The program is partially inspired by this one: https://ww2.mathworks.cn/matlabcentral/fileexchange/45840-complete-pan-tompkins-implementation-ecg-qrs-detector
