# Qb-auto-delt **WIP**
***Test only with safe env.
Can delete some torrent(s) from your seedbox definitly.
You're now warned.***

**Script/dockerapp** 

Permet de supprimer automatiquement des torrents de qBittorrent, en fonction d'un score prenant en compte divers paramètres.
Il contrôle l'espace disque de la seedbox a interval régulier, pour le maintenir à un % défini ou laisser un espace libre défini par l'utilisateur.
Le choix des torrents à supprimer en priorité est fait en fonction de leur temps de seed, de leur ratio d'upload et de leurs étiquettes.
Cela respecte donc les H&R des tracker priver.
Des exceptions sont possibles grâce a l'ajout manuel d'étiquettes sur les torrent concerné dans qBittorrent.

 
Allows you to automatically remove torrents from qBittorrent, based on a score that takes into account various parameters.
It controls the disk space of the seedbox at regular intervals, to maintain it at a defined % or leave a free space defined by the user.
The choice of torrents to delete in priority is made according to their seed time, their upload ratio and their tags.
This respects the H&R of private trackers.
Exceptions are possible thanks to the manual addition of tags on the concerned torrents in qBittorrent.

Le script à pour l'instant vocation à tourner dans un environnement python dockerisé.

The script is for the moment intended to run in a dockerized python environment.

## TO DO

- Rédiger un WIKI d'installation et d'utilisation propre. 
- **DOCKERISATION**

Pas de liaisons avec une messagerie instantanée ou un service mail pour le moment, Cela pouvant déjà être géré par qBittorrent.

- Write a WIKI for clean installation and use. 
- **DOCKERIZATION**

## Logging :
Logging info show in console
File log name `qb-auto-delt.log` are also created from scratch at start of the app in `./log` directory.
By default, logging lvl are up to `INFO` for the console and up to `DEBUG` in the log file.


- **INFO** console log exemple :

```log
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Conection with qBittorrent tested OK : v4.3.4.1
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Conection with qBt Web Api tested OK : 2.8.1
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Disk Space use at 33% - Your allow to fill up 47% before deleting Script start runing
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Script will recheck your disk space in - 600 - seconds
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Disk Space use at 84% -  Over -04%, deleting script start.
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Script delete: covid19_vestiaires_v050520.pdf, 459.6 KiB free up.
```

- **DEBUG** logs in `qb-auto-delt.log` exemple :

```log
INFO  ::  2021-04-21 12:31:37,321 - __main__ - Conection with qBittorrent tested OK : v4.3.4.1
INFO  ::  2021-04-21 12:31:37,326 - __main__ - Conection with qBt Web Api tested OK : 2.8.1
DEBUG  ::  2021-04-21 12:31:37,326 - __main__ - Disque usage calculation OK
INFO  ::  2021-04-21 12:31:37,326 - __main__ - Disk Space use at 33% - Your allow to fill up 47% before deleting Script start runing
DEBUG  ::  2021-04-21 12:31:37,333 - __main__ - 
             covid19_vestiaires_v050520.pdf :
             Ratio: 0/=0   SeedTime: 2730/=-10000   Tag: PUBLIC/=9999999   State: stalledUP/=0
             Final Score: 9989999
DEBUG  ::  2021-04-21 12:31:37,333 - __main__ - Dico data update, torrent scored : 
{'1b00dcebb138fe69230aad0c3c3d34c4964d1d80': 9989999}
INFO  ::  2021-04-21 12:31:37,333 - __main__ - Script will recheck your disk space in - 600 - seconds
```
