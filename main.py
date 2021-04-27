#!/usr/bin/env python3
# By LimeCat

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
logger_globale = logging.getLogger(__name__)
logger = logging.getLogger("qbAutoDelt")
listlog = logging.getLogger('torrentSelection')
init(autoreset=True)

# Connection a l'api de qBit, en cas d'echec retente 20 fois avec un delay de 20 seconds avant de down le script.


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

# Func. de control disque par GiB, retourn la quantité d'espace en KiB au dessus de la
# limit defini par l'user si elle est dépassé - ou False si elle ne l'est pas.


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

# Func. de control disque par %, retourn la quantité d'espace en KiB au dessus de la limit
# defini par l'user si elle est dépassé - ou False si elle ne l'est pas


def diskUsageByPercent():

    logger.debug(
        "Control method : diskUsageByPercent select... :: start calculation")
    statDisk = psutil.disk_usage(cfg["diskUsageByPercent"]["path"])
    percentDisk = round(statDisk.percent, 1)
    percentMax = cfg["diskUsageByPercent"]["max"]
    ctrlDisk = True if percentDisk > percentMax else False

    if ctrlDisk:
        logger.info(
            f"{Fore.RED}Disk Space use at {str(percentDisk)}% -  Over than {str(round(percentDisk - percentMax, 2))} %, deleting script start{Style.RESET_ALL}")
        if useDiscord:
            discord.post(
                content=f"Disk Space use at {str(percentDisk)}% -  Over than {str(round(percentDisk - percentMax, 2))} %, deleting script start", embeds=emb1, username="Qbittorrent")
        ctrlDiskOver = (statDisk.total / 100) * \
            round((percentDisk - percentMax) * 2 ** 30)
        return ctrlDiskOver
    else:
        logger.info(
            f"{Fore.GREEN}Disk Space use at {str(percentDisk)}% - Your allow to fill up {str(round(percentMax - percentDisk,2))} % before deleting script process{Style.RESET_ALL}")

# Manage the multipl tags or cat retourn by api


def convertTolist(string):
    if string:
        st_list = list(string.split(", "))
        return st_list

# Comapare les liste est retourne un boll True si present et False sinon


def listContains(List1, List2):
    if (List1 and List2):
        set1 = set(List1)
        set2 = set(List2)
        if set1.intersection(set2):
            return True
        else:
            return False

# Transforme un dico en Tuple et le trie en fonction de la valleur de sa clé


def forLoggSortedDict(dict1):
    sortedDict = sorted(dict1.items(), key=lambda item: item[1], reverse=True)
    itemCount = 0
    for item in sortedDict:
        itemCount = itemCount + 1
        listlog.info(f"Torrent {str(itemCount)} :: {item} ")
    # backTodict = {k: v for k, v in sortedDict}

# Retourn True si un torrent a un tag ou des condition d'exclusion dans les paramettres


def excludTorrent(torrent):

    excludTags = cfg["t_tags"]["exclud"]
    excludCats = cfg["t_cats"]["exclud"]
    excludStates = cfg["t_states"]["states"]
    excludSeederCountLimit = cfg["countSeeder"]
    minTime = cfg["min_SeedTime"] * 60 * 60
    minRatio = cfg["min_Ratio"]
    listlog.debug(f"Torrent : {torrent} ")
    if torrent.tags in excludTags:
        return True
    elif torrent.category in excludCats:
        return True
    elif torrent.state in excludStates:
        return True
    elif torrent.num_complete < excludSeederCountLimit:
        return True
    elif torrent.ratio < minRatio:
        return True
    elif torrent.time_active < minTime:
        return True

# Retourn True si le torrent est Public, que le parméttre d'exclusion des Public et sur True,
# et que le torrent est en seed depuis plus de 30 min


def includPublicTorrent(torrent):
    # trackerPublic = convertTolist(torrent.tracker)
    # trackerCount = 1 if not trackerPublic else len(trackerPublic) For API 2.2
    trackerCount = fixFoxDispAPI(torrent)
    publicInPriority = cfg["publicPriority"]
    if publicInPriority:
        if not trackerCount == 1:
            if torrent.time_active > 18:
                return True

# Selection de la méthode pour reconaitre les torrent public en fonction de leur nombre de tracker,
# l'api du client est en version 2.2 utilise une conversion des tracker en liste pour les compter.


def fixFoxDispAPI(torrent):
    if not cfg["fix"]:
        trackerPublic = convertTolist(torrent.tracker)
        trackerCount = 1 if not trackerPublic else len(trackerPublic)
    else:
        trackerCount = torrent.trackers_count
    return trackerCount

# Détérmine si le torrent est a inclure ou a exclure en fonction des paramétre défini par l'utilisateur,
# et du Tag donné au torrent.


def torrentToInclud(torrent):
    """description

    Si torrent a exclur return False
    Si torrent a inclur return True
    """
    tagsPriority = cfg["t_tags"]["priority"]
    categoryPriority = cfg["t_cats"]["priority"]
    excludTags = cfg["t_tags"]["exclud"]
    excludCats = cfg["t_cats"]["exclud"]
    excludStates = cfg["t_states"]["states"]
    if listContains(convertTolist(torrent.tags), tagsPriority):
        return True
    elif listContains(convertTolist(torrent.category), categoryPriority):
        return True
    elif excludTorrent(torrent):
        if includPublicTorrent(torrent):
                if torrent.tags in excludTags:
                    return False
                elif torrent.category in excludCats:
                    return False
                elif torrent.state in excludStates:
                    return False
                else:
                    return True
        else:
            return False
    else:
        return True

# Scrore les torrent qui passe tout les test d'inclusion, et retourn un dico avec le score trouvez,
# le noms, le hash et le poid des torrents.


def scoreTorrent():

    minTime = cfg["min_SeedTime"] * 60 * 60
    tagsPriority = cfg["t_tags"]["priority"]
    categoryPriority = cfg["t_cats"]["priority"]
    tagsPrefer = cfg["t_tags"]["prefer"]
    categoryPrefer = cfg["t_cats"]["prefer"]
    torrentData = dict()

    for torrent in qbt.torrents_info():
        trackerCount = fixFoxDispAPI(torrent)
        publicInPriority = includPublicTorrent(torrent)
        torrentSelection = torrentToInclud(torrent)
        listlog.info(f"{torrent.name} :: to exclud : {torrentSelection}")
        if torrentSelection:
            scoreSeed = round(torrent.time_active / 60 / 60 / 24 * 0.2, 2)
            scoreRatio = round(torrent.ratio, 2)
            scorePopularity = round(torrent.num_complete * 0.1)
            scoreIsPublic = 10000 if publicInPriority is True else 0
            scorePriority = 1000 if listContains(convertTolist(torrent.tags), tagsPriority) is True else 1000 if listContains(
                convertTolist(torrent.category), categoryPriority) is True else 0
            scorePrefer = 200 if listContains(convertTolist(torrent.tags), tagsPrefer) is True else 200 if listContains(
                convertTolist(torrent.category), categoryPrefer) is True else 0
            torrentInfo = (torrent.name, torrent.hash, torrent.size)
            torrentFinalScore = sum(
                (scoreSeed, scoreRatio, scorePriority, scorePrefer, scoreIsPublic, scorePopularity), 10)
            torrentData[torrentInfo] = torrentFinalScore
            listlog.debug(
                f"{torrent.hash} ::: Ratio: {str(torrent.ratio)}/={str(scoreRatio)}, SeedTime: {str(torrent.time_active)}/={str(scoreSeed)}, Popularity: {str(scorePopularity)}, Prio: {str(scorePriority)}, Is Public: {str(scoreIsPublic)}, Prefer: {str(scorePrefer)}")
            listlog.debug(
                f"{torrent.name} :: Final Score: {str(torrentFinalScore)}")
    # logger.debug(f"Data update, torrent scored :" + str(torrentData))
    return torrentData

# define the countdown func. Petit goody qui a l'aire de foutre plus le bordel
# qu'autre chose sur docker ^^ mais sa sa clac en console


def countdown(t):

    while t:
        mins, secs = divmod(t, 60)
        named_tuple = time.localtime()  # get struct_time
        time_string = time.strftime("%Y-%m-%d,%H:%M:%S", named_tuple)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(f"INFO  ::  {time_string},000 - qbAutoDelt - {Fore.CYAN}Script will recheck your disk space in - {timer} - minute{Style.RESET_ALL}", end="\r")
        time.sleep(1)
        t -= 1

# Prompt confirmation [y/n]


def confirmInput(question, default="no"):

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = f"{Fore.RED}{Style.BRIGHT} [y/n] {Style.RESET_ALL}:: "
    elif default == "yes":
        prompt = f"{Fore.RED}{Style.BRIGHT} [Y/n] {Style.RESET_ALL}:: "
    elif default == "no":
        prompt = f"{Fore.RED}{Style.BRIGHT} [y/N] {Style.RESET_ALL}:: "
    else:
        raise ValueError("Invalid default answer: '{}}'".format(default))
    while True:
        # print(question + prompt)
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print(
                f"{Fore.RED}{Style.BRIGHT}:.    Please respond with 'yes' or 'no' (or 'y' or 'n').{Style.RESET_ALL}")

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

    # Main loop
    while True:
        qbt = qBitConnection(logger, cfg)
        ctrlState = diskUsageByGiB(
        ) if cfg["ControlMethode"] is True else diskUsageByPercent()
        if ctrlState:
            logger.debug(f"Control of ctrlState value : {ctrlState}")
            time.sleep(3)
            dataScored = scoreTorrent()
            forLoggSortedDict(dataScored)
            totalRemove = 0
            # Deleting loop
            while totalRemove < ctrlState:
                torrentWithHighScore = max(dataScored, key=dataScored.get)
                sizeTorrent = int(torrentWithHighScore[2])
                if cfg["safe"]:
                    named_tuple = time.localtime()  # get struct_time
                    time_string = time.strftime(
                        "%Y-%m-%d,%H:%M:%S", named_tuple)
                    question = f'SAFE  ::  {time_string},000 - qbAutoDelt - {Fore.YELLOW}{Style.BRIGHT}Remove: {Fore.WHITE}{torrentWithHighScore[0]}, {Fore.RED}{humanize.naturalsize(sizeTorrent, binary=True)}{Style.RESET_ALL}'
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
                    f'{Fore.YELLOW}{Style.BRIGHT}Script delete: {Fore.WHITE}{torrentWithHighScore[0]}, {Fore.RED}{humanize.naturalsize(sizeTorrent, binary=True)}{Fore.YELLOW} free up.{Style.RESET_ALL}')
                if useDiscord:
                    discord.post(
                        content=f'Torrent delete: {torrentWithHighScore[0]}, {humanize.naturalsize(sizeTorrent, binary=True)} free up.', embeds=emb2, username="Qbittorrent")
                totalRemove = totalRemove + sizeTorrent
                logger.debug(
                    f"Total space free in the loop: {humanize.naturalsize(totalRemove, binary=True)} sleep 10 second")
                del dataScored[torrentWithHighScore]
                time.sleep(10)
        else:
            logger.debug(f"Control of ctrlState value : {bool(ctrlState)}")
        interval = cfg['interval']
        logger.debug(
            f"{Fore.CYAN}Script will recheck your disk space in - {str(interval)} - minute{Style.RESET_ALL}")
        countdown(int(interval) * 60)
