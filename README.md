# QRS-Detector
Détection de QRS Complex

Cette interface graphique permet de déterminer les paramètres Q,R,S d'un ECG.
Le bouton "Charger L'ECG" permet de charger notre électrocardiogramme.
Le bouton "Détection" va tout d'abord filtrer le signal grâce à l'algorithme de Pan-Tompkins.

Une fois cela fois, les points Q, R,S du signal seront détectés. A partir d'eux, le programme va calcul le battement cardiaque moyen par minute et effectuer un diagnostique :
 - Si le battement est supérieur à 100, on est en face d'un cas de Tachycardie
 - Si le battement est inférieur à 60, on est en face d'une Bradycardie
 - Dans le cas contraire, le battement est normal.

Le programme est partiellement inspiré de celui-ci: https://ww2.mathworks.cn/matlabcentral/fileexchange/45840-complete-pan-tompkins-implementation-ecg-qrs-detector
