
#!/usr/bin/env python3

#
#
#
#

import psutil

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
disk_REAL = diskusagecontrol()
disk_MAX = 80

###############################
####        Script        #####
###############################
if disk_MAX >= disk_REAL:
    print("INFO : Espace disque à " + str(disk_REAL) + "%")
else:
    print("inferieur")