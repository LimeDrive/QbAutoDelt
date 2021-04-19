
#!/usr/bin/env python3

# Tourne en boucle toutes les 5 mins
#

import psutil
import schedule
import time

###############################
####      Fonction        #####
###############################

# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, PATH a mettre dans une variable
def diskusagecontrol():
    stat = psutil.disk_usage('./')
    percent = round(stat.percent)
    return percent

###############################
####    Variable Global   #####
###############################

disk_MAX = 80

###############################
####        Script        #####
###############################

while True:

    disk_REAL = diskusagecontrol()

    if disk_MAX >= disk_REAL:
        t = time.asctime()
        print("INFO " + t + " : Espace disque à " + str(disk_REAL) + "%")
        time.sleep(5*60)
    else:
        print("TO-DO")
        time.sleep(5*60)
    