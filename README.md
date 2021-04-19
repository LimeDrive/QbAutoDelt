# qb-auto-delt

## init repo

### TO DO
- proper readme
- def quelle torrent sont pertiant a supp ?

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