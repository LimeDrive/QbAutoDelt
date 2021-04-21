#!/usr/bin/env python3

import psutil
import time
import operator
import qbittorrentapi
import yaml
import logging
import logging.config
import humanize
import os

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

def diskUsageControl(logger, cfg):
    mtd = cfg["ControlMethode"]
    if mtd:
        logger.debug("Control method : diskUsageByGiB select")
        limit = cfg["diskUsageByGiB"]["val"]
        i = qbt.sync.maindata.delta()
        free = round(i.server_state.free_space_on_disk / 2 ** 30)
        ctrlDisk = True if limit > free else False
        if ctrlDisk is True:
            logger.info(f"Disk Space at {humanize.naturalsize(i.server_state.free_space_on_disk, binary=True)} -  Over than {str(limit - free)} GiB, deleting script start")
        else:
            logger.info(f"Disk Space at {humanize.naturalsize(i.server_state.free_space_on_disk, binary=True)} - Your allow to fill up {str(free - limit)} GiB before deleting script process")
    else:
        logger.debug("Control method : diskUsageByPercent select")
        stat = psutil.disk_usage(cfg["diskUsageByPercent"]["path"])
        percent = round(stat.percent)
        limit = cfg["diskUsageByPercent"]["max"]
        ctrlDisk = True if percent > limit else False
        if ctrlDisk is True:
            logger.info(f"Disk Space use at {str(percent)}% -  Over than {str(percent - limit)} %, deleting script start")
        else:
            logger.info(f"Disk Space use at {str(percent)}% - Your allow to fill up {str(limit - percent)} % before deleting script process")
    return ctrlDisk
    

def scoreTorrent(cfg, qbt):
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

    # Logging
    logdir = 'log'
    if not os.path.exists(logdir):
        os.mkdir(logdir)
        print("Directory " , logdir ,  " Created ")
    else:    
        print("Directory " , logdir ,  " already exists")

    logging.config.fileConfig('config/logging.conf')
    logger = logging.getLogger(__name__)

    # Import from Yaml config/qb-auto-delt.config.yml
    with open('config/qb-auto-delt.config.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Try to establish Qbittorrent connection
    qbt = qBitConnection(logger, cfg)


    while True:

        # ctrl = diskUsageControl(logger, cfg)
        scoreTorrent(cfg, qbt) # for test
        if diskUsageControl(logger, cfg):
            data = scoreTorrent(cfg, qbt)
            i = diskUsageControl(logger, cfg)
            while i is True:
                t = max(data, key = data.get)
                qbt.torrents_delete(delete_files=True, torrent_hashes=t[1])
                time.sleep(3)
                size = humanize.naturalsize(t[2], binary=True)
                logger.info(f'Script delete: {t[0]}, {str(size)} free up.')
                del data[max_key]
                logger.info('Script will sleep 45 seconds...CY-L ;)')
                time.sleep(45)
                i = diskUsageControl(logger, cfg)
            looger.info('Good enough for today ! Stop Dll, otherwise im gona delete everyting...')
            time.sleep(5)
            looger.info('rm -rf / ? ready... ?')
        inter = cfg["interval"] * 60
        logger.info(f"Script will recheck your disk space in - {str(inter)} - seconds")
        time.sleep(inter)
        logger.debug('Script restart')
