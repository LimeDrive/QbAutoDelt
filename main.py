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
logging.config.fileConfig('logging.conf')
logger_globale = logging.getLogger(__name__)
logger = logging.getLogger("qbAutoDelt")
listlog = logging.getLogger('torrentSelection')
init(autoreset=True)

# Connection a l'api de qBit, en cas d'echec retente 20 fois avec un delay de 340 seconds avant de down le script.


@retry(stop=stop_after_attempt(20), after=after_log(logger, logging.WARNING), wait=wait_fixed(340))
def qBit_Connection(logger, cfgGen):

    qbt = qbittorrentapi.Client(
        host=cfgGen["qBittorrent"]["host"], username=cfgGen["qBittorrent"]["user"], password=cfgGen["qBittorrent"]["password"], VERIFY_WEBUI_CERTIFICATE=False)
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


def disk_Usage_By_GiB():

    logger.debug(
        f"Control method : disk_Usage_By_GiB select, start calculation")
    limitDiskSpace = cfgGen["disk_Usage_By_GiB"]["val"]
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


def disk_Usage_By_Percent():

    logger.debug(
        "Control method : disk_Usage_By_Percent select... :: start calculation")
    statDisk = psutil.disk_usage(cfgGen["disk_Usage_By_Percent"]["path"])
    percentDisk = round(statDisk.percent, 1)
    percentMax = cfgGen["disk_Usage_By_Percent"]["max"]
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


def convert_To_List(string):
    if string:
        st_list = list(string.split(", "))
        return st_list

# Comapare les liste est retourne un boll True si present et False sinon


def list_Contains(List1, List2):
    if (List1 and List2):
        set1 = set(List1)
        set2 = set(List2)
        if set1.intersection(set2):
            return True
        else:
            return False

# Transforme un dico en Tuple et le trie en fonction de la valleur de sa clé


def for_Sorted_Dict(dict1):
    sortedDict = sorted(dict1.items(), key=lambda item: item[1], reverse=True)
    itemCount = 0
    for item in sortedDict:
        itemCount = itemCount + 1
        listlog.info(f"Torrent {str(itemCount)} :: {item} ")
    # backTodict = {k: v for k, v in sortedDict}

# Retourn True si un torrent a un tag ou des condition d'exclusion dans les paramettres


def exclud_Torrent(torrent):

    excludTags = cfgSel["Torrents_Tags"]["exclud"]
    excludCats = cfgSel["Torrents_Category"]["exclud"]
    excludTorrentStatesToExclud = cfgGen["Torrent_States"]["TorrentStatesToExclud"]
    excludSeederCountLimit = cfgSel["countSeeder"]
    minTime = cfgSel["min_SeedTime"] * 60 * 60
    minRatio = cfgSel["min_Ratio"]
    listlog.debug(f"Torrent : {torrent} ")
    if torrent.tags in excludTags:
        return True
    elif torrent.category in excludCats:
        return True
    elif torrent.state in excludTorrentStatesToExclud:
        return True
    elif torrent.num_complete < excludSeederCountLimit:
        return True
    elif torrent.ratio < minRatio:
        return True
    elif seed_Time_Torrent(torrent) < minTime:
        return True

# Retourn True si le torrent est Public, que le parméttre d'exclusion des Public et sur True,
# et que le torrent est en seed depuis plus de 30 min


def is_Public_Torrent(torrent):
    # trackerPublic = convert_To_List(torrent.tracker)
    # trackerCount = 1 if not trackerPublic else len(trackerPublic) For API 2.2
    trackerCount = count_Public_Tracker(torrent)
    publicInPriority = cfgSel["publicPriority"]
    minSeedTime = int(cfgGen["autoSupp"]["minSeedTime"]) * 60 * 60
    if publicInPriority:
        if not trackerCount == 1:
            if seed_Time_Torrent(torrent) > minSeedTime:
                return True

# Selection de la méthode pour reconaitre les torrent public en fonction de leur nombre de tracker,
# l'api du client est en version 2.2 utilise une conversion des tracker en liste pour les compter.


def count_Public_Tracker(torrent):
    if cfgGen["fix"]:
        trackerPublic = convert_To_List(torrent.tracker)
        trackerCount = 1 if not trackerPublic else len(trackerPublic)
    else:
        trackerCount = torrent.trackers_count
    return trackerCount

# Défini le temps de seed du torrent, si le Fix de l'api 2.2 est sur True, utilise le temps actif totale (moin precis car ne prend
# pas en compte les potentielle temps ou le tracker et offline, ni le temps de téléchargement pour les torrent qui down lentement
# donc impertaivement prévoir quelque heur de marge dans le réglage pour H&R)
# sinon prend le seedTime réel fourni par la nouvelle API


def seed_Time_Torrent(torrent):
    if cfgGen["fix"]:
        SeedTime = torrent.time_active
    else:
        SeedTime = torrent.seeding_time
    return SeedTime

# Détérmine si le torrent est a inclure ou a exclure en fonction des paramétre défini par l'utilisateur,
# et du Tag donné au torrent.


def torrent_To_Includ(torrent):
    """description

    Si torrent a exclur return False
    Si torrent a inclur return True
    """
    tagsPriority = cfgSel["Torrents_Tags"]["priority"]
    categoryPriority = cfgSel["Torrents_Category"]["priority"]
    excludTags = cfgSel["Torrents_Tags"]["exclud"]
    excludCats = cfgSel["Torrents_Category"]["exclud"]
    excludTorrentStatesToExclud = cfgGen["Torrent_States"]["TorrentStatesToExclud"]
    if list_Contains(convert_To_List(torrent.tags), tagsPriority):
        return True
    elif list_Contains(convert_To_List(torrent.category), categoryPriority):
        return True
    elif exclud_Torrent(torrent):
        if is_Public_Torrent(torrent):
            if list_Contains(convert_To_List(torrent.tags), excludTags):
                return False
            elif list_Contains(convert_To_List(torrent.category), excludCats):
                return False
            elif torrent.state in excludTorrentStatesToExclud:
                return False
            else:
                return True
        else:
            return False
    else:
        return True

# défini si il y a des torrent public ou a supp a chaque boucle.


def torrent_Check(torrentsInfo):
    
    minSeedTime = int(cfgGen["autoSupp"]["minSeedTime"]) * 60 * 60
    excludTorrentStatesToExclud = cfgGen["Torrent_States"]["TorrentStatesToExclud"]
    tagsPriority = cfgSel["Torrents_Tags"]["priority"]
    categoryPriority = cfgSel["Torrents_Category"]["priority"]
    excludTags = cfgSel["Torrents_Tags"]["exclud"]
    excludCats = cfgSel["Torrents_Category"]["exclud"]

    torrentData = dict()

    for torrent in torrentsInfo:
        if not torrent.state in excludTorrentStatesToExclud:
            if is_Public_Torrent(torrent):
                if cfgGen["autoSupp"]["public"]:
                    if not list_Contains(convert_To_List(torrent.tags), excludTags):
                        if not list_Contains(convert_To_List(torrent.category), excludCats):
                            torrentInfo = (torrent.name, torrent.size)
                            torrentData[torrent.hash] = torrentInfo
            elif list_Contains(convert_To_List(torrent.tags), tagsPriority):
                if cfgGen["autoSupp"]["priority"]:
                    if seed_Time_Torrent(torrent) > minSeedTime:
                        torrentInfo = (torrent.name, torrent.size)
                        torrentData[torrent.hash] = torrentInfo
            elif list_Contains(convert_To_List(torrent.category), categoryPriority):
                if cfgGen["autoSupp"]["priority"]:
                    if seed_Time_Torrent(torrent) > minSeedTime:
                        torrentInfo = (torrent.name, torrent.size)
                        torrentData[torrent.hash] = torrentInfo
    return torrentData

## Check si le tracker et dans la liste des traker préféré.


def tracker_Is_Prefer(torrent):
    
    trackerPrefer = cfgSel["preferTrackers"]
    torrentTraker = torrent.tracker    
    for i in trackerPrefer:
        if i in torrentTraker:
            return True

# Scrore les torrent qui passe tout les test d'inclusion, et retourn un dico avec le score trouvez,
# le noms, le hash et le poid des torrents.


def score_Torrent(torrentsInfo):
    
    minTime = cfgSel["min_SeedTime"] * 60 * 60
    tagsPriority = cfgSel["Torrents_Tags"]["priority"]
    categoryPriority = cfgSel["Torrents_Category"]["priority"]
    tagsPrefer = cfgSel["Torrents_Tags"]["prefer"]
    categoryPrefer = cfgSel["Torrents_Category"]["prefer"]
    settSeedScore = cfgSel['Scoring_Calculation']['seed_Time_Score']
    settRatioScore = cfgSel['Scoring_Calculation']['ratio_Score']
    settPopScore = cfgSel['Scoring_Calculation']['popularity_Score']

    torrentData = dict()

    for torrent in torrentsInfo:
        trackerCount = count_Public_Tracker(torrent)
        publicInPriority = is_Public_Torrent(torrent)
        torrentSelection = torrent_To_Includ(torrent)
        listlog.info(f"{torrent.name} :: to includ : {torrentSelection}")
        if torrentSelection:
            scoreSeed = round(seed_Time_Torrent(
                torrent) / 60 / 60 / 24 * 0.2, 2)
            scoreRatio = round(torrent.ratio, 2)
            scorePopularity = round(torrent.num_complete * 0.1)
            scoreIsPublic = 100000 if publicInPriority is True else 0
            scorePriority = 10000 if list_Contains(convert_To_List(torrent.tags), tagsPriority) is True else 10000 if list_Contains(
                convert_To_List(torrent.category), categoryPriority) is True else 0
            scorePrefer = 1000 if list_Contains(convert_To_List(torrent.tags), tagsPrefer) is True else 1000 if list_Contains(
                convert_To_List(torrent.category), categoryPrefer) is True else 0
            trackerIsPrefer = 1000 if tracker_Is_Prefer(torrent) is True else 0
            torrentInfo = (torrent.name, torrent.size, torrent.hash)
            torrentFinalScore = sum(
                (scoreSeed, scoreRatio, scorePriority, scorePrefer, trackerIsPrefer, scoreIsPublic, scorePopularity), 10)
            torrentData[torrentInfo] = torrentFinalScore
            listlog.debug(
                f"{torrent.hash} ::: Ratio: {str(torrent.ratio)}/={str(scoreRatio)}, SeedTime: {str(seed_Time_Torrent(torrent))}/={str(scoreSeed)}, Popularity: {str(scorePopularity)}, Prio: {str(scorePriority)}, Is Public: {str(scoreIsPublic)}, Prefer: {str(scorePrefer)}, TrackerIsPrefer: {str(trackerIsPrefer)} ")
            listlog.debug(
                f"{torrent.name} :: Final Score: {str(torrentFinalScore)}")
    # logger.debug(f"Data update, torrent scored :" + str(torrentData))
    return torrentData

# Suppression des torrent public et torrent tag ou cat Priority sans se souci de l'espace disque.


def supp_Torrent_Auto_Tagged(torrentCheck, torrentsInfo):

    time.sleep(3)
    safeMode = cfgGen["safe"]
    torrentData = torrentCheck
    
    for torrent in torrentData:
        torrentSelected = torrentData[torrent]
        sizeTorrent = int(torrentSelected[1])
        answer = safe_Mode(torrentSelected, sizeTorrent)
        if safeMode:
            if not answer:
                break
        qbt.torrents_delete(delete_files=True,
                            torrent_hashes=torrent)
        logger.info(
            f'{Fore.YELLOW}{Style.BRIGHT}Script delete: {Fore.WHITE}{torrentSelected[0]}, {Fore.RED}{humanize.naturalsize(sizeTorrent, binary=True)}{Fore.YELLOW} free up.{Style.RESET_ALL}')
        if useDiscord:
            discord.post(
                content=f'Torrent delete: {torrentSelected[0]}, {humanize.naturalsize(sizeTorrent, binary=True)} free up.', embeds=emb2, username="Qbittorrent")
        time.sleep(10)

# Mode de sécurité pour la suppréssion des torrents.


def safe_Mode(torrentSelected, sizeTorrent):
    if cfgGen["safe"]:
        named_tuple = time.localtime()  # get struct_time
        time_string = time.strftime(
            "%Y-%m-%d,%H:%M:%S", named_tuple)
        question = f'SAFE  ::  {time_string},000 - qbAutoDelt - {Fore.YELLOW}{Style.BRIGHT}Remove: {Fore.WHITE}{torrentSelected[0]}, {Fore.RED}{humanize.naturalsize(sizeTorrent, binary=True)}{Style.RESET_ALL}'
        answer = confirm_Input(question, default="no")
        if not answer:
            logger.debug(f'Value of user answer are : {answer}')
            logger.info(
                f"{Fore.RED}You don't approve my choise so... Scipt will Exit in 20 seconds{Style.RESET_ALL}")
            if useDiscord:
                discord.post(content=f"You don't approve my choise so... Scipt will Exit in 5 seconds",
                             embeds=emb2, username="Qbittorrent")
                time.sleep(5)
            return False
        else:
            return True

# Fonction de suppression qui supp j'usqu'a sa que l'espace disque soit revenu dans la limite fixé.


def supp_Disk_Usage(ctrlState, torrentsInfo):
    
    time.sleep(3)
    
    safeMode = cfgGen["safe"]
    dataScored = score_Torrent(torrentsInfo)
    for_Sorted_Dict(dataScored)
    totalRemove = 0
    
    # Deleting loop
    if dataScored:
        while totalRemove < ctrlState:
            torrentSelected = max(dataScored, key=dataScored.get)
            sizeTorrent = int(torrentSelected[1])
            answer = safe_Mode(torrentSelected, sizeTorrent)
            if safeMode:
                if not answer:
                    break
            qbt.torrents_delete(delete_files=True,
                                torrent_hashes=torrentSelected[2])
            logger.info(
                f'{Fore.YELLOW}{Style.BRIGHT}Script delete: {Fore.WHITE}{torrentSelected[0]}, {Fore.RED}{humanize.naturalsize(sizeTorrent, binary=True)}{Fore.YELLOW} free up.{Style.RESET_ALL}')
            if useDiscord:
                discord.post(
                    content=f'Torrent delete: {torrentSelected[0]}, {humanize.naturalsize(sizeTorrent, binary=True)} free up.', embeds=emb2, username="Qbittorrent")
            totalRemove = totalRemove + sizeTorrent
            logger.debug(
                f"Total space free in the loop: {humanize.naturalsize(totalRemove, binary=True)} sleep 10 second")
            del dataScored[torrentSelected]
            time.sleep(10)
    else:
        logger.info(
            f"{Fore.RED}Script has Nothing to delete following your parametere, will break the loop{Style.RESET_ALL}")


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


def confirm_Input(question, default="no"):

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

    # General Config:
    with open('config/GeneralSetting.yml', 'r') as ymlfile:
        cfgGen = yaml.load(ymlfile, Loader=yaml.FullLoader)

    useDiscord = cfgGen["discord"]["use"]
    discord = Discord(url=cfgGen["discord"]["webhook"])
    emb1 = [{"url": "https://github.com/LimeDrive/qb-auto-delt",
             "title": "Disk space Control"}]
    emb2 = [{"url": "https://github.com/LimeDrive/qb-auto-delt",
             "title": "Torrents Delete"}]

    # Main loop
    while True:
        
        # Torrent Selection Config :
        with open('config/TorrentsSelectionSetting.yml') as ymlfile:
            cfgSel = yaml.load(ymlfile, Loader=yaml.FullLoader)

        qbt = qBit_Connection(logger, cfgGen)
        torrentsInfo = qbt.torrents_info()
        torrentCheck = torrent_Check(torrentsInfo)
        ctrlState = disk_Usage_By_GiB(
        ) if cfgGen["ControlMethode"] is True else disk_Usage_By_Percent()
        interval = cfgGen['interval']
        # # For Test:
        # dataScored = score_Torrent(torrentsInfo)
        # for_Sorted_Dict(dataScored)
        if ctrlState:
            logger.debug(f"Control of ctrlState value : {ctrlState}")
            supp_Disk_Usage(ctrlState, torrentsInfo)
        elif torrentCheck:
            logger.debug(
                f"Control of torrent_Check value : {str(bool(torrentCheck))}")
            supp_Torrent_Auto_Tagged(torrentCheck, torrentsInfo)
        if cfgGen["countdown"]:
            logger.debug(
                f"{Fore.CYAN}Script will recheck your disk space in - {str(interval)} - minute{Style.RESET_ALL}")
            countdown(int(interval) * 60)
        else:
            logger.info(
                f"{Fore.CYAN}Script will recheck your disk space in - {str(interval)} - minute{Style.RESET_ALL}")
            time.sleep(int(interval) * 60)
