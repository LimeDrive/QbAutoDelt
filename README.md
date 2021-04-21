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

- Améliorer les logs lors de la suppression de torrents
- Rédiger un WIKI d'installation et d'utilisation propre. 
- **DOCKERISATION**

Pas de liaisons avec une messagerie instantanée ou un service mail pour le moment, Cela pouvant déjà être géré par qBittorrent.

- Improve logs when deleting torrents
- Write a WIKI for clean installation and use. 
- DOCKERIZATION**

No link with an instant messenger or a mail service for the moment, this can already be managed by qBittorrent.

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


### Note : Exemple de retour api :

```DEBUG  ::  2021-04-21 10:29:16,830 - __main__ - torrent api: AttrDict({'added_on': 1618992220, 'amount_left': 0, 'auto_tmm': False, 'availability': -1, 'category': '', 'completed': 470667, 'completion_on': 1618992220, 'content_path': '/Users/user/Documents/covid19/covid19_vestiaires_v050520.pdf', 'dl_limit': -1, 'dlspeed': 0, 'downloaded': 0, 'downloaded_session': 0, 'eta': 8640000, 'f_l_piece_prio': False, 'force_start': True, 'hash': '1b00dcebb138fe69230aad0c3c3d34c4964d1d80', 'last_activity': 1618993757, 'magnet_uri': 'magnet:?xt=urn:btih:1b00dcebb138fe69230aad0c3c3d34c4964d1d80&dn=covid19_vestiaires_v050520.pdf', 'max_ratio': -1, 'max_seeding_time': -1, 'name': 'covid19_vestiaires_v050520.pdf', 'num_complete': 0, 'num_incomplete': 0, 'num_leechs': 0, 'num_seeds': 0, 'priority': 0, 'progress': 1, 'ratio': 0, 'ratio_limit': -2, 'save_path': '/Users/user/Documents/covid19/', 'seeding_time': 1254, 'seeding_time_limit': -2, 'seen_complete': -3600, 'seq_dl': False, 'size': 470667, 'state': 'forcedUP', 'super_seeding': False, 'tags': '', 'time_active': 1254, 'total_size': 470667, 'tracker': '', 'trackers_count': 0, 'up_limit': -1, 'uploaded': 0, 'uploaded_session': 0, 'upspeed': 0}) ```




Le `seeding_time': 1254` n'a pas l'air au point, ça ne se met pas a jour certaines fois sur les tests, et ça vient de qBittorrent
Peut être utiliser `completion_on': 1618992220` et faire une fonction de calcul.
A voir lors des tests...


The `seeding_time': 1254` doesn't look right, it doesn't update sometimes on tests, and it's from qBittorrent
Maybe use `completion_on': 1618992220` and make a calculation function.
To be seen on tests...
