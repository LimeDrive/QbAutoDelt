#!/usr/bin/env python3

import psutil
import time
import operator
import yaml
import os
import sys
import humanize
import qbittorrentapi
import logging
import logging.config
from colorama import Fore, Style, init
from discordwebhook import Discord
from tenacity import retry, stop_after_attempt, after_log, wait_fixed

# Logging Consol + File
os.makedirs("log", exist_ok=True)
logging.config.fileConfig('config/logging.conf')
logger = logging.getLogger(__name__)
init(autoreset=True)

# Qbittorrent API conection.


@retry(stop=stop_after_attempt(20), after=after_log(logger, logging.WARNING), wait=wait_fixed(20))
def qBitConnection(logger, cfg):
    qbt = qbittorrentapi.Client(
        host=cfg["qbt_log"]["qbt_host"], username=cfg["qbt_log"]["qbt_user"], password=cfg["qbt_log"]["qbt_pass"], VERIFY_WEBUI_CERTIFICATE=False)
    try:
        qbt.auth_log_in()
        logger.info(
            f'{Fore.CYAN}Conection with qBittorrent tested OK : Qbittorrent {qbt.app.version}, API {qbt.app.web_api_version}{Style.RESET_ALL}')
    except:
        logger.warning(
            f'{Fore.RED}{Style.BRIGHT}Conection with qBittorrent and Web Api Logging failed{Style.RESET_ALL}')
        raise
    return qbt

# Fonction de control disque par GiB, retourn la quantité d'espace en KiB au dessus de la limit defini par l'user si elle est dépassé - ou False si elle ne l'est pas.


def diskUsageByGiB():
    logger.debug(f"Control method : diskUsageByGiB select, start calculation")
    limitDiskSpace = cfg["diskUsageByGiB"]["val"]
    infoDisk = qbt.sync.maindata.delta()
    freeDiskSpace = round(
        infoDisk.server_state.free_space_on_disk / 2 ** 30, 2)
    ctrlDisk = True if (freeDiskSpace - limitDiskSpace) < 0 else False
    if ctrlDisk:
        logger.info(
            f"{Fore.RED}Disk Space at {humanize.naturalsize(infoDisk.server_state.free_space_on_disk, binary=True)} -  Over than {round( limitDiskSpace - freeDiskSpace, 2 )} GiB, deleting script start{Style.RESET_ALL}")
        if useDiscord:
            discord.post(
                content=f"Disk Space at {humanize.naturalsize(infoDisk.server_state.free_space_on_disk, binary=True)} -  Over than {round( limitDiskSpace - freeDiskSpace, 2 )} GiB, deleting script start", embeds=emb1, username="Qbittorrent")
        return round(limitDiskSpace - freeDiskSpace) * 2 ** 30
    else:
        logger.info(
    f"{Fore.GREEN}Disk Space at {humanize.naturalsize(infoDisk.server_state.free_space_on_disk, binary=True)} - Your allow to fill up {round( freeDiskSpace - limitDiskSpace, 2 )} GiB before deleting script process{Style.RESET_ALL}")

# Fonction de control disque par %, retourn la quantité d'espace en KiB au dessus de la limit defini par l'user si elle est dépassé - ou False si elle ne l'est pas

def diskUsageByPercent():
    logger.debug(
        "Control method : diskUsageByPercent select... :: start calculation")
    statDisk = psutil.disk_usage(cfg["diskUsageByPercent"]["path"])
    percentDisk = round(statDisk.percent, 1)
    percentMax = cfg["diskUsageByPercent"]["max"]
    ctrlDisk = True if percentDisk > percentMax else False
    if ctrlDisk:
        logger.info(
            f"{Fore.RED}Disk Space use at {str(percentDisk)}% -  Over than {str( percentDisk - percentMax )} %, deleting script start{Style.RESET_ALL}")
        if useDiscord:
            discord.post(
                content=f"Disk Space use at {str(percentDisk)}% -  Over than {str( percentDisk - percentMax )} %, deleting script start", embeds=emb1, username="Qbittorrent")
        ctrllDiskOver = (statDisk.total / 100) * round((percentDisk - percentMax) * 2 ** 30)
        return ctrlDiskOver
    else:
        logger.info(
            f"{Fore.GREEN}Disk Space use at {str(percentDisk)}% - Your allow to fill up {str( percentMax - percentDisk )} % before deleting script process{Style.RESET_ALL}")

# Torrents scroring


def scoreTorrent(cfg, qbt):
    min_time = cfg["t_statistique"]["min_SeedTime"] * 60 * 60
    min_ratio = cfg["t_statistique"]["min_Ratio"]
    tgprio = cfg["t_tags"]["priority"]
    tgpref = cfg["t_tags"]["prefer"]
    tgex = cfg["t_tags"]["exclud"]
    tgstate = cfg["t_tags"]["states"]
    data = dict()
    for t in qbt.torrents_info():
        s_seed = round(100 + (t.seeding_time - min_time) / 6000,
                       2) if t.seeding_time > min_time else -10000
        s_ratio = -10000 if t.ratio < min_ratio else t.ratio * 100
        s_tag = 9999999 if t.tags in tgprio else 100000 if t.tags in tgpref else - \
            99999999999 if t.tags in tgex else 0
        s_state = -99999999999 if t.state in tgstate else 0
        t_score = s_ratio + s_seed + s_tag + s_state
        t_info = (t.name, t.hash, t.size)
        data[t_info] = t_score
        logger.debug(f"\n \
            {t.name} :\n \
            Ratio: {str(t.ratio)}/={str(s_ratio)}   SeedTime: {str(t.seeding_time)}/={str(s_seed)}   Tag: {t.tags}/={str(s_tag)}   State: {t.state}/={str(s_state)}\n \
            Final Score: {str(t_score)}")
    logger.debug(f"Data update, torrent scored : \n" + str(data))
    return data

# Prompt confirmation [y/n]


def confirmInput(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("Invalid default answer: '{}}'".format(default))
    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}Please respond with 'yes' or 'no' (or 'y' or 'n').\n{Style.RESET_ALL}")

###############################
####        Script        #####
###############################


if __name__ == '__main__':

    # Import from Yaml config/qb-auto-delt.config.yml
    with open('config/qb-auto-delt.config.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # Discord notify
    useDiscord = cfg["discord"]["use"]
    discord = Discord(url=cfg["discord"]["webhook"])
    emb1 = [{"url": "https://github.com/LimeDrive/qb-auto-delt",
             "title": "Disk space Control"}]
    emb2 = [{"url": "https://github.com/LimeDrive/qb-auto-delt",
             "title": "Torrents Delete"}]

    # Try to establish Qbittorrent connection
    # qbt = qBitConnection(logger, cfg)

    # Main loop
    while True:
        qbt = qBitConnection(logger, cfg)
        ctrlState = diskUsageByGiB() if cfg["ControlMethode"] is True else diskUsageByPercent()
        if ctrlState:
            logger.debug(f"Control of ctrlState value : {ctrlState}")
            dataScored = scoreTorrent(cfg, qbt)
            totalRemove = 0
            # Deleting loop
            while totalRemove < ctrlState:
                torrentWithHighScore = max(dataScored, key=dataScored.get)
                sizeTorrent = int(torrentWithHighScore[2])
                if cfg["safe"]:
                    question = f'{Fore.YELLOW}{Style.BRIGHT}Remove: {Fore.RED}{torrentWithHighScore[0]}, {Fore.CYAN}{humanize.naturalsize(sizeTorrent, binary=True)}{Style.RESET_ALL}'
                    answer = confirmInput(question, default="no")
                    if not answer:
                        logger.debug(f'Value of user answer are : {answer}')
                        logger.info(
                            f"{Fore.RED}You don't approve my choise so... Scipt will Exit in 20 seconds{Style.RESET_ALL}")
                        if useDiscord:
                            discord.post(content=f"You don't approve my choise so... Scipt will Exit in 5 seconds",
                                        embeds=emb2, username="Qbittorrent")
                            time.sleep(5)
                        break
                qbt.torrents_delete(delete_files=True,
                                    torrent_hashes=torrentWithHighScore[1])
                logger.info(
                    f'{Fore.YELLOW}{Style.BRIGHT}Script delete: {Fore.RED}{torrentWithHighScore[0]}, {Fore.CYAN}{humanize.naturalsize(sizeTorrent, binary=True)}{Fore.YELLOW} free up.')
                if useDiscord:
                    discord.post(
                    content=f'Torrent delete: {torrentWithHighScore[0]}, {humanize.naturalsize(sizeTorrent, binary=True)} free up.', embeds=emb2, username="Qbittorrent")
                totalRemove = totalRemove + sizeTorrent
                logger.debug(
                    f"Total remove space free in the loop : {humanize.naturalsize(totalRemove, binary=True)}")
                del dataScored[torrentWithHighScore]
                time.sleep(20)
        else:
            logger.debug(f"Control of ctrlState value : {bool(ctrlState)}")
        interval = cfg['interval']
        logger.info(
        f"{Fore.CYAN}Script will recheck your disk space in - {str(interval)} - minute{Style.RESET_ALL}")
        time.sleep(int(interval) * 60)
