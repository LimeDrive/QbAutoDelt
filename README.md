# Qb-auto-delt TESTING
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

Le script à pour l'instant vocation à tourner dans un environnement python dockerisé sur serveur, mais il est tout a fait possible de ne l'executé qu'une seul foi comme tout script python. 

The script is for the moment intended to run in a dockerized python environment.

---
# Instalation

- Créé un repertoire config/ et un répertoir log/ qui vont étre monté sur votre docker.

- Récupérer le fichier de config *qb-auto-delt.config.yml* a placé dans :`/config`

    `curl -LJO https://raw.githubusercontent.com/LimeDrive/qb-auto-delt/master/config/qb-auto-delt.config.yml`

- L'éditer pour l'adapté avec vos préférance

- Run votre docker avec compose en montant les volumes /log et /config

Exemple de docker compose :

```yaml
version: "3.9"
services:

    QbAutoDelt:
        container_name: qbautodelt
        image: limedrive/qbautodelt:latest
        environment:
            - PYTHON_QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE: True
        volumes:
            - 'path/to/config/:/qb-auto-delt/config'
            - 'path/to/log:/qb-auto-delt/log'
        restart: unless-stopped
```

## Configuration :

Pour configuré vos préférance édité le fichier : 

`config/qb-auto-delt.config.yml`

## Logging :

Le log qui rapport le processuce de séléction des torrent a supprimé se trouvent dans le fichier : 

`log/torrentSlection.log`

Le log de suivie générale sr trouvent dans le fichier : 

`log/qbAutoDelt.log`


- **INFO** console log exemple :

```log
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Conection with qBittorrent tested OK : v4.3.4.1
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Conection with qBt Web Api tested OK : 2.8.1
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Disk Space use at 33% - Your allow to fill up 47% before deleting Script start runing
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Script will recheck your disk space in - 600 - seconds
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Disk Space use at 84% -  Over -04%, deleting script start.
INFO  ::  2021-04-21 xx:xx:xx,xxx - __main__ - Script delete: covid19_vestiaires_v050520.pdf, 459.6 KiB free up.
```
