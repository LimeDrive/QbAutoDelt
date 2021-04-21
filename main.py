#!/usr/bin/env python3

import psutil
import time
import operator
import qbittorrentapi
import yaml
import logging
import logging.config
import humanize

###############################
####    Conection API     #####
###############################

def qBitConnection(logger, cfg):
    qbt = qbittorrentapi.Client(host=cfg["qbt_log"]["qbt_host"], username=cfg["qbt_log"]["qbt_user"], password=cfg["qbt_log"]["qbt_pass"])
    try:
        qbt.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        logger.warning(f'Conection with qBittorrent and Web Api failed: \n{e}')
    logger.info(f'Conection with qBittorrent tested OK : {qbt.app.version}')
    logger.info(f'Conection with qBt Web Api tested OK : {qbt.app.web_api_version}')
    return qbt

###############################
####      Fonction        #####
###############################

# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, PATH a mettre dans une variable
def diskUsageControl():
    stat = psutil.disk_usage(cfg["disk"]["PATH"])
    percent = round(stat.percent)
    logger.debug(f'Disque usage calculation OK result : {str(percent)}')
    return percent

# Va récupérer les torrents, leur hash, leur donne un score, puis retourne le tout sous forme de dictionnaire
def scoreTorrent():
    min_time = cfg["t_statistique"]["min_SeedTime"] * 60 * 60
    min_ratio = cfg["t_statistique"]["min_Ratio"]
    tgprio = cfg["t_tags"]["priority"]
    tgpref = cfg["t_tags"]["prefer"]
    tgex = cfg["t_tags"]["exclud"]
    tgstate = cfg["t_tags"]["states"]
    data = dict()
    for t in qbt.torrents_info():
        s_seed = round(100 + (t.seeding_time - min_time) / 6000, 2) if t.seeding_time > min_time else -10000
        s_ratio = -10000 if t.ratio < min_ratio else t.ratio * 100
        s_tag = 9999999 if t.tags in tgprio else 100000 if t.tags in tgpref else -99999999999 if t.tags in tgex else 0
        s_state = -99999999999 if t.state in tgstate else 0
        t_score = s_ratio + s_seed + s_tag + s_state
        t_info = (t.name, t.hash, t.size)
        data[t_info] = t_score
        logger.debug( f"\n \
            {t.name} :\n \
            Ratio: {str(t.ratio)}/={str(s_ratio)}   SeedTime: {str(t.seeding_time)}/={str(s_seed)}   Tag: {t.tags}/={str(s_tag)}   State: {t.state}/={str(s_state)}\n \
            Final Score: {str(t_score)}" )
    logger.debug( "Data update, torrent scored : \n" + str(data) )
    return data

###############################
####        Script        #####
###############################

if __name__ == '__main__':

    logging.config.fileConfig('config/logging.conf')
    logger = logging.getLogger(__name__)

    ## Import from Yaml config/qb-auto-delt.config.yml
    with open('config/qb-auto-delt.config.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Qbit connection
    qbt = qBitConnection(logger, cfg)

    while True:

        disk_P = cfg["disk"]["MAX"]
        disk_REAL = diskUsageControl()

        if disk_P >= disk_REAL:
            logger.info(f"Disk Space use at {str(disk_REAL)}% - Your allow to fill up {str(disk_P - disk_REAL)}% before deleting script process")
            # scoreTorrent() # for testing
        else:
            data = scoreTorrent()
            i = diskUsageControl()
            logger.info(f"Disk Space use at {str(disk_REAL)}% -  Over than {str(disk_REAL - disk_P)}%, deleting script start")
            while i > disk_P:
                t = max(data, key = data.get)
                qbt.torrents_delete(delete_files=True, torrent_hashes=t[1])
                time.sleep(3)
                size = humanize.naturalsize(t[2], binary=True)
                logger.info(f'Script delete: {t[0]}, {str(size)} free up.')
                del data[max_key]
                logger.debug('Sleep for 15 seconds')
                time.sleep(15)
                i = diskUsageControl()
            looger.info('Good enough for today ! Stop Dll, otherwise im gona delete everyting...')
            time.sleep(5)
            looger.info('rm -rf / ? ready... ?')

        inter = cfg["interval"] * 60
        logger.info(f"Script will recheck your disk space in - {str(inter)} - seconds")
        time.sleep(inter)
        logger.debug('Script restart')