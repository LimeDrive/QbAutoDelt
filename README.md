# qb-auto-delt

## init repo

### TO DO
- proper readme
- def quelle torrent sont pertinant a supp ?
- Fichier de conf yaml pour l'user

## idés de base :
Script/app permetant de supprimé automatiquement des torrent de qBittorrent, en fonction de leur pertiance.
***
    DiskSpace = # Valeur Espace disk en %
    
    DiskTaget = Valeur ( defini dans un json de reglage )
    
    PrefertLBL = "" # Label qui seront preferet pour supp ( defini dans un json de reglage )
    PrioLabel = "" # Label qui on une haute priorité pour supp ( defini dans un json de reglage )
    EcludLabel = "" # Label a exclure de la supp ( defini dans un json de reglage )
    
        if DiskSpace >= DiskTaget then
            print log
            END Script...
    
        else
    
            SortTorrent() # Trie and Score les Torrents actif
    
                Boucle While, DiskSpace >= DiskTaget
                    SuppHighScoredTorrent()
                    delay 30 second
                    dSpace();
    
    
            Print log
            END Script
    
    
    fonction(dSpace);
        # redéfini la valeur de DiskSpace
    
    
    fonction(SortTorrent);		
        # Boucle for sur l'api qui liste les torrent par leur hash	
        # Classement des Torrents dans un dico avec des Score : Pour chaque hash
        # Connection RPC
    
        SortedTorrent = {}
    
        For hash in Api.List.Torrent.Hash: 
    
            SeedTime = Api.Torrent.seedTime(hash)
            Label = Api.Torrent.Label(hash)
            Ratio = Api.Torrent.Ratio(hash)
            Score = 0
    
            Score = Score + Ratio
    
            if SeedTime > 288000: # 80 Heure
                Score = Score + 100
    
            if Label == PrefertLBL:
                Score = Score + 100
            elif Label == PrioLBL:
                Score = Score + 1000
            elif Label == EcludLabel:
                Score = 0
    
            SortedTorrent[hash] = Score
    
    fonction(SuppHighScoredTorrent);
        # Connection RPC
        # Suppression du hash associer a la +haute Valeur de Score dans le dico
        # Notification

## Exemple de retour api :

    >>> print(torrent)

    [AttrDict({'added_on': 1618863901, 'amount_left': 0, 'auto_tmm': False, 'availability': -1, 'category': '', 'completed': 19763, 'completion_on': 1618863902, 'content_path': "/Users/***/Documents/12-31 Jour de l'An.docx", 'dl_limit': -1, 'dlspeed': 0, 'downloaded': 0, 'downloaded_session': 0, 'eta': 8640000, 'f_l_piece_prio': False, 'force_start': False, 'hash': '41426e6274d721a55886a65155caa01eeb02002d', 'last_activity': 1618864314, 'magnet_uri': 'magnet:?xt=urn:btih:41426e6274d721a55886a65155caa01eeb02002d&dn=12-31%20Jour%20de%20l%27An.docx', 'max_ratio': -1, 'max_seeding_time': -1, 'name': "12-31 Jour de l'An.docx", 'num_complete': 0, 'num_incomplete': 1, 'num_leechs': 0, 'num_seeds': 0, 'priority': 0, 'progress': 1, 'ratio': 0, 'ratio_limit': -2, 'save_path': '/Users/$$$$$$$$/Documents/', 'seeding_time': 407, 'seeding_time_limit': -2, 'seen_complete': -3600, 'seq_dl': False, 'size': 19763, 'state': 'stalledUP', 'super_seeding': False, 'tags': '', 'time_active': 407, 'total_size': 19763, 'tracker': '', 'trackers_count': 0, 'up_limit': -1, 'uploaded': 0, 'uploaded_session': 0, 'upspeed': 0})]