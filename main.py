
#!/usr/bin/env python3

# Tourne en boucle toutes les 5 mins
#

import psutil
import schedule
import time
import qbittorrentapi


###############################
####    Variable Global   #####
###############################

qbt = qbittorrentapi.Client(host='localhost:8080', username='admin', password='adminadmin')
disk_MAX = 32

###############################
####      Fonction        #####
###############################

# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, PATH a mettre dans une variable
def diskusagecontrol():
    stat = psutil.disk_usage('./')
    percent = round(stat.percent)
    return percent

def apitest():
    try:
        qbt.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
    print(f'qBittorrent: {qbt.app.version}')
    print(f'qBittorrent Web API: {qbt.app.web_api_version}')

###############################
####        Script        #####
###############################

while True:

    disk_REAL = diskusagecontrol()

    if disk_MAX >= disk_REAL:
        t = time.asctime()
        print("INFO " + t + " : Espace disque à " + str(disk_REAL) + "%")
    else:
        apitest()
        i = diskusagecontrol()
        while i > disk_MAX:
            i = diskusagecontrol()
            time.sleep(20)
        print("TO-DO must be done lool")

    time.sleep(5*60)
    