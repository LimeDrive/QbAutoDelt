# qb-auto-delt

**Script/dockerapp** permetant de supp automatiquement des torrents de qBittorrent, en fonction de leur pertiance.
Il control l'espace disque de la seedbox a interval réguliere, pour le maintenire à un % défini.
Le choix des torrents a supp en priorité et fait en fonction de leur temps de seed et leur ratio.
Cela respecte donc les H&R des tracker priver.
Des exéption son possible grace a l'ajout manuel d'étiquette sur les torrent concerné dans qBt.

Le script à pour l'instant vocation a tounez dans un environement python en docker.

## TO DO

- proper readme
- add condition with lower scord to : state = downloding torrents to advoid PRIO tag to be supp to early.
- notification discod and/or télégramme
- requirement.txt for python
- docker file


### Note : Exemple de retour api :

    >>> print(torrent)

    [AttrDict({'added_on': 1618863901, 'amount_left': 0, 'auto_tmm': False, 'availability': -1, 'category': '', 'completed': 19763, 'completion_on': 1618863902, 'content_path': "/Users/***/Documents/12-31 Jour de l'An.docx", 'dl_limit': -1, 'dlspeed': 0, 'downloaded': 0, 'downloaded_session': 0, 'eta': 8640000, 'f_l_piece_prio': False, 'force_start': False, 'hash': '41426e6274d721a55886a65155caa01eeb02002d', 'last_activity': 1618864314, 'magnet_uri': 'magnet:?xt=urn:btih:41426e6274d721a55886a65155caa01eeb02002d&dn=12-31%20Jour%20de%20l%27An.docx', 'max_ratio': -1, 'max_seeding_time': -1, 'name': "12-31 Jour de l'An.docx", 'num_complete': 0, 'num_incomplete': 1, 'num_leechs': 0, 'num_seeds': 0, 'priority': 0, 'progress': 1, 'ratio': 0, 'ratio_limit': -2, 'save_path': '/Users/$$$$$$$$/Documents/', 'seeding_time': 407, 'seeding_time_limit': -2, 'seen_complete': -3600, 'seq_dl': False, 'size': 19763, 'state': 'stalledUP', 'super_seeding': False, 'tags': '', 'time_active': 407, 'total_size': 19763, 'tracker': '', 'trackers_count': 0, 'up_limit': -1, 'uploaded': 0, 'uploaded_session': 0, 'upspeed': 0})]