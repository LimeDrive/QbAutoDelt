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
        host=cfg["qbt_log"]["qbt_host"], username=cfg["qbt_log"]["qbt_user"], password=cfg["qbt_log"]["qbt_pass"])
    try:
        qbt.auth_log_in()
        logger.info(
            f'{Fore.GREEN}Conection with qBittorrent tested OK : {qbt.app.version}{Style.RESET_ALL}')
        logger.info(
            f'{Fore.GREEN}Conection with qBt Web Api tested OK : {qbt.app.web_api_version}{Style.RESET_ALL}')
    except:
        logger.warning(
            f'{Fore.RED}{Style.BRIGHT}Conection with qBittorrent and Web Api Logging failed{Style.RESET_ALL}')
        raise
    return qbt

# Disk space controle, return bol follows parameter


def diskUsageControl():
    if cfg["ControlMethode"]:
        time.sleep(60)
        logger.debug(f"{Fore.CYAN}Control method : diskUsageByGiB select{Style.RESET_ALL}")
        limit = cfg["diskUsageByGiB"]["val"]
        i = qbt.sync.maindata.delta()
        free = round(i.server_state.free_space_on_disk / 2 ** 30)
        ctrlDisk = True if limit > free else False
        if ctrlDisk is True:
            logger.info(
                f"{Fore.RED}Disk Space at {humanize.naturalsize(i.server_state.free_space_on_disk, binary=True)} -  Over than {str(limit - free)} GiB, deleting script start{Style.RESET_ALL}")
            if useDiscord:
                discord.post(
                    content=f"Disk Space at {humanize.naturalsize(i.server_state.free_space_on_disk, binary=True)} -  Over than {str(limit - free)} GiB, deleting script start", embeds=emb1, username="Qbittorrent")
        else:
            logger.info(
                f"{Fore.GREEN}Disk Space at {humanize.naturalsize(i.server_state.free_space_on_disk, binary=True)} - Your allow to fill up {str(free - limit)} GiB before deleting script process{Style.RESET_ALL}")
    else:
        logger.debug("Control method : diskUsageByPercent select")
        stat = psutil.disk_usage(cfg["diskUsageByPercent"]["path"])
        percent = round(stat.percent)
        limit = cfg["diskUsageByPercent"]["max"]
        ctrlDisk = True if percent > limit else False
        if ctrlDisk is True:
            logger.info(
                f"{Fore.RED}Disk Space use at {str(percent)}% -  Over than {str(percent - limit)} %, deleting script start{Style.RESET_ALL}")
            if useDiscord:
                discord.post(
                    content=f"Disk Space use at {str(percent)}% -  Over than {str(percent - limit)} %, deleting script start", embeds=emb1, username="Qbittorrent")
        else:
            logger.info(
                f"{Fore.GREEN}Disk Space use at {str(percent)}% - Your allow to fill up {str(limit - percent)} % before deleting script process{Style.RESET_ALL}")
    return ctrlDisk

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
            print(f"{Fore.RED}{Style.BRIGHT}Please respond with 'yes' or 'no' (or 'y' or 'n').\n{Style.RESET_ALL}")

# Remove Torrents


def removeSelectTorrent(aprouve, t, qbt):
    if aprouve is True:
        qbt.torrents_delete(delete_files=True, torrent_hashes=t[1])
        time.sleep(5)
        logger.info(f'{Fore.YELLOW}{Style.BRIGHT}Script delete: {Fore.RED}{t[0]}, {Fore.CYAN}{str(size)}{Fore.YELLOW} free up.{Style.RESET_ALL}')
        if useDiscord:
            discord.post(
                content=f'Torrent delete: {t[0]}, {str(size)} free up.', embeds=emb2, username="Qbittorrent")
    else:
        logger.debug(f'Value of isTrue are : {aprouve}')
        logger.info(
            f"{Fore.RED}You don't approve my choise so... Scipt will Exit in 20 seconds{Style.RESET_ALL}")
        if useDiscord:
            discord.post(content=f"You don't approve my choise so... Scipt will Exit in 5 seconds",
                         embeds=emb2, username="Qbittorrent")
        time.sleep(5)
        sys.exit(f'{Fore.RED}INFO.....exit by user choise. CyU :({Style.RESET_ALL}')


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
    qbt = qBitConnection(logger, cfg)

    # Main loop
    while True:
        # if control disk retourn out limit fixed
        if diskUsageControl():
            i = diskUsageControl()
            data = scoreTorrent(cfg, qbt)
            # If safe mode or not
            while i is True:
                t = max(data, key=data.get)
                size = humanize.naturalsize(t[2], binary=True)
                security = cfg["safe"]
                if security is True:
                    question = f'{Fore.YELLOW}{Style.BRIGHT}Remove: {Fore.RED}{t[0]}, {Fore.CYAN}{str(size)}{Style.RESET_ALL}'
                    answer = confirmInput(question, default="no")
                    removeSelectTorrent(answer, t, qbt)
                    del data[t]
                else:
                    removeSelectTorrent(True, t, qbt)
                    del data[t]
                i = diskUsageControl()
            looger.info(
                f'{Fore.CYAN}Good enough for today ! Stop Dll, otherwise im gona delete everyting...{Style.RESET_ALL}')
            looger.info(f'{Style.BRIGHT}{Back.RED}{Fore.CYAN}rm -rf / ? ready... ?{Style.RESET_ALL}')
        inter = cfg["interval"] * 60
        logger.info(
            f"{Fore.CYAN}Script will recheck your disk space in - {str(inter)} - seconds{Style.RESET_ALL}")
        time.sleep(inter)
