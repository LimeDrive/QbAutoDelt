# qb-auto-delt /!  WORK IN PROGRESS 
Test only with safe env.
Could delete torrent from your seedbox definitly.
You've been warned :/

**Script/dockerapp** permetant de supp automatiquement des torrents de qBittorrent, en fonction de leur pertiance.
Il control l'espace disque de la seedbox a interval réguliere, pour le maintenire à un % défini.
Le choix des torrents a supp en priorité et fait en fonction de leur temps de seed et leur ratio.
Cela respecte donc les H&R des tracker priver.
Des exéption son possible grace a l'ajout manuel d'étiquette sur les torrent concerné dans qBt.

Le script à pour l'instant vocation a tounez dans un environement python en docker.

## TO DO

- proper README.md, install and use instruction. 
- **DOCKERISE** Next ;/

NO instant msg plan for the moment,... could be send by torrent client already, and usless with this app due the logs.

### Improve logs : done. 
- consol log lvl Info
- log file lvl DEBUG, exemple : 

```
INFO  ::  2021-04-20 15:04:21,904 - __main__ - Conection with qBittorrent tested OK : version:  v4.3.4.1
INFO  ::  2021-04-20 15:04:21,909 - __main__ - Conection with qBt Web Api tested OK : version:  2.8.1
DEBUG  ::  2021-04-20 15:04:21,909 - __main__ - Disque usage calculation done.
INFO  ::  2021-04-20 15:04:21,909 - __main__ - ...........Disk use at :  32% ..keep going.
INFO  ::  2021-04-20 15:04:21,909 - __main__ - Start interval of - 600 - seconds
```
### Note : Exemple de retour api :

```DEBUG  ::  2021-04-21 10:29:16,830 - __main__ - torrent api: AttrDict({'added_on': 1618992220, 'amount_left': 0, 'auto_tmm': False, 'availability': -1, 'category': '', 'completed': 470667, 'completion_on': 1618992220, 'content_path': '/Users/user/Documents/covid19/covid19_vestiaires_v050520.pdf', 'dl_limit': -1, 'dlspeed': 0, 'downloaded': 0, 'downloaded_session': 0, 'eta': 8640000, 'f_l_piece_prio': False, 'force_start': True, 'hash': '1b00dcebb138fe69230aad0c3c3d34c4964d1d80', 'last_activity': 1618993757, 'magnet_uri': 'magnet:?xt=urn:btih:1b00dcebb138fe69230aad0c3c3d34c4964d1d80&dn=covid19_vestiaires_v050520.pdf', 'max_ratio': -1, 'max_seeding_time': -1, 'name': 'covid19_vestiaires_v050520.pdf', 'num_complete': 0, 'num_incomplete': 0, 'num_leechs': 0, 'num_seeds': 0, 'priority': 0, 'progress': 1, 'ratio': 0, 'ratio_limit': -2, 'save_path': '/Users/user/Documents/covid19/', 'seeding_time': 1254, 'seeding_time_limit': -2, 'seen_complete': -3600, 'seq_dl': False, 'size': 470667, 'state': 'forcedUP', 'super_seeding': False, 'tags': '', 'time_active': 1254, 'total_size': 470667, 'tracker': '', 'trackers_count': 0, 'up_limit': -1, 'uploaded': 0, 'uploaded_session': 0, 'upspeed': 0}) ```

- le `seeding_time': 1254` n'a pas l'aire supper, sa ne se mets pas a jour certaine foi sur les test, et sa vient de qBittorrent
Voir a utilisé `completion_on': 1618992220` et fair une fonction de calcul.
A voir avec des tests...