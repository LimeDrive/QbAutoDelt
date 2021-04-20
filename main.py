
#!/usr/bin/env python3

import psutil
import time
import operator
import qbittorrentapi
import yaml
import logging
import logging.config

###############################
####        Logging       #####
###############################

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

###############################
####    Variable Global   #####
###############################

## Import from Yaml config/qb-auto-delt.config.yml
with open('config/qb-auto-delt.config.yml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


###############################
####    Conection API     #####
###############################

qbt = qbittorrentapi.Client(host=cfg["qbt_log"]["qbt_host"], username=cfg["qbt_log"]["qbt_user"], password=cfg["qbt_log"]["qbt_pass"])
try:
    qbt.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    logger.warning('Conection with qBittorrent and Web Api failed')
logger.info(f'Conection with qBittorrent tested OK : version:  {qbt.app.version}')
logger.info(f'Conection with qBt Web Api tested OK : version:  {qbt.app.web_api_version}')

###############################
####      Fonction        #####
###############################

# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, PATH a mettre dans une variable
def diskusagecontrol():
    stat = psutil.disk_usage(cfg["disk"]["PATH"])
    percent = round(stat.percent)
    logger.debug('Disque usage calculation done.')
    return percent

# Vas récupéré les torrent, leur hash, leur donné un score. pour retouné un dico.
def scoretorrent():
    min_SEEDTIME = cfg["t_statistique"]["min_SeedTime"]*60*60
    min_ratio = cfg["t_statistique"]["min_Ratio"]
    tags_PRIO = cfg["t_tags"]["priority"]
    tags_PREF = cfg["t_tags"]["prefer"]
    tags_EXCLUD = cfg["t_tags"]["exclud"]
    tags_STATE = cfg["t_tags"]["states"]
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
        t_state = torrent.state
        if t_state in tags_STATE:
            s_state = -99999999999
        else:
            s_state = 0
        s_score = s_ratio + s_seed + s_tag + s_state
        data[l_hash] = s_score
        #tname = torrent.name
        #logger.debug(f"{tname} :\nRatio: {str(t_ratio)}/={str(s_ratio)}   SeedTime: {str(t_seed)}/={str(s_seed)} \
        #      Tag: {t_tag}/={str(s_tag)}   State: {t_state}/={str(s_state)}\nFinale Scored: {str(s_score)}")
    logger.info('Torrents fully scored...')
    return data

###############################
####        Script        #####
###############################

while True:

    disk_P = cfg["disk"]["MAX"]
    disk_REAL = diskusagecontrol()

    if disk_P >= disk_REAL:
        logger.info("...........Disk use at :  " + str(disk_REAL) + "% ..keep going.")
    else:
        data = scoretorrent()
        i = diskusagecontrol()
        while i > disk_P:
            max_key = max(data, key = data.get)
            qbt.torrents_delete(delete_files=True, torrent_hashes=max_key)
            logger.info('Torrent delted')
            time.sleep(3)
            del data[max_key]
            i = diskusagecontrol()
            logger.info('Sleep for 15 seconds')
            time.sleep(15)
        looger.info('Good enough for today ! Stop Dll, otherwise im gone delet everyting...')
        time.sleep(5)
        looger.info('rm -rf / ? ready... ?')

    inter = cfg["interval"] * 60
    logger.info(f"Start interval of - {str(inter)} - seconds")
    time.sleep(inter)
    logger.debug('Script restart')