
#!/usr/bin/env python3

#
# Tourne en boucle toutes les 5 mins
#
# Supprime en priorité les torrent qui on un minimum de SEEDTIME (defini par l'user en heur)
# Passe devant ceux qui on le plus de ratio
# Chaque semaine de seed supplemantaire au SEEDTIME mini est scores comme 1 de ratio
# Les Tag PRIO sont peut import le ratio et le seedtime
# Les Tag PREFERT font monter les torrent en priorité, apré les PRIO
# peut import le ratio et le seed il ne respecte pas non plus le seedtime
#

import psutil
import time
import operator
import qbittorrentapi
import yaml


###############################
####    Variable Global   #####
###############################

## Import from Yaml config/qb-auto-delt.config.yml
with open('config/qb-auto-delt.config.yml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

qbt_host = cfg["qbt_log"]["qbt_host"]
qbt_user = cfg["qbt_log"]["qbt_user"]
qbt_pass = cfg["qbt_log"]["qbt_pass"]
disk_MAX = cfg["disk_MAX"]
min_SEEDTIME = cfg["t_statistique"]["min_SeedTime"]*60*60
min_ratio = cfg["t_statistique"]["min_Ratio"]
tags_PRIO = cfg["t_tags"]["priority"]
tags_PREF = cfg["t_tags"]["prefer"]
tags_EXCLUD = cfg["t_tags"]["exclud"]
time_interval = cfg["interval"]

###############################
####    Conection API     #####
###############################

qbt = qbittorrentapi.Client(host=qbt_host, username=qbt_user, password=qbt_pass)
try:
    qbt.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)
print(f'qBittorrent: {qbt.app.version}')
print(f'qBittorrent Web API: {qbt.app.web_api_version}')

###############################
####      Fonction        #####
###############################

# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, PATH a mettre dans une variable
def diskusagecontrol():
    stat = psutil.disk_usage('./')
    percent = round(stat.percent)
    return percent

# Vas récupéré les torrent, leur hash, leur donné un score. pour retouné un dico.
def scoretorrent():
    data = dict()
    for torrent in qbt.torrents_info():
        l_hash = torrent.hash
        l_seed = torrent.seeding_time
        if l_seed > min_SEEDTIME:
            s_seed = round(100 + (l_seed - min_SEEDTIME) / 6000, 2)
        else:
            s_seed = -10000
        t_ratio = torrent.ratio
        if t_ratio < min_ratio:
            s_ratio = -10000
        else:
            s_ratio = t_ratio * 100
        t_tag = torrent.tags
        if t_tag in tags_PRIO:
            s_tag = 9999999
        elif t_tag in tags_PREF:
            s_tag = 100000
        elif t_tag in tags_EXCLUD:
            s_tag = -10000
        else:
            s_tag = 0
        s_score = s_ratio + s_seed + s_tag
        data[l_hash] = s_score
    return data

###############################
####        Script        #####
###############################

while True:

    disk_REAL = diskusagecontrol()

    if disk_MAX >= disk_REAL:
        t = time.asctime()
        print("INFO " + t + " : Espace disque à " + str(disk_REAL) + "%")
    else:
        data = scoretorrent()
        i = diskusagecontrol()
        while i > disk_MAX:
            max_key = max(data, key = data.get)
            qbt.torrents_delete(delete_files=True, torrent_hashes=max_key)
            time.sleep(5)
            print("Good news Torrent supp log plus précis a faire")
            del data[max_key]
            i = diskusagecontrol()
            time.sleep(15)
        print("TO-DO")

    time.sleep(time_interval * 60)