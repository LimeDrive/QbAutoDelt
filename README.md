# Qb-auto-delt   ---   ***alpha phase***   ---
***Test only with safe env.***

Can delete some torrent(s) from your seedbox definitly.
You're now warned.

---

**Script/dockerapp** 
---
Permet de supprimer automatiquement des torrents de qBittorrent, en fonction d'un score prenant en compte divers paramètres.
Il contrôle l'espace disque de la seedbox a interval régulier, pour le maintenir à un % défini ou laisser un espace libre défini par l'utilisateur.
Le choix des torrents à supprimer en priorité est fait en fonction de leur temps de seed, de leur ratio d'upload et de leurs étiquettes.
Cela respecte donc les H&R des tracker priver.
Des exceptions sont possibles grâce a l'ajout manuel d'étiquettes sur les torrent concerné dans qBittorrent.

___
 
Allows you to automatically remove torrents from qBittorrent, based on a score that takes into account various parameters.
It controls the disk space of the seedbox at regular intervals, to maintain it at a defined % or leave a free space defined by the user.
The choice of torrents to delete in priority is made according to their seed time, their upload ratio and their tags.
This respects the H&R of private trackers.
Exceptions are possible thanks to the manual addition of tags on the concerned torrents in qBittorrent.

___

>Le script à pour l'instant vocation à tourner dans un environnement python dockerisé sur serveur, mais il est tout a fait possible de ne l'executé qu'une seul foi comme tout script python. 

>The script is for the moment intended to run in a dockerized python environment.

---
# Installation

## Docker et docker-compose (recomandé)

### Création des fichier des répertoires partagé et montage des volumes:

* Créé un repertoire **_config/_** et un répertoir **_log/_** qui vont étre monté sur votre docker.

* Récupérer le fichier yml *qb-auto-delt.config.yml* a placé dans :`/config`

  >  `curl -LJO https://raw.githubusercontent.com/LimeDrive/qb-auto-delt/master/config/qb-auto-delt.config.yml`

* L'éditer pour l'adapté avec vos préférance

* Run votre docker en montant les volumes ainsi dans la commande:
    * `-v /PATH/TO/LOCAL/log:/qb-auto-delt/log`
    * `-v /PATH/TO/LOCAL/config:/qb-auto-delt/config:ro`

### Exemple de ***docker-compose*** : _(recomandé)_

```yml
---
version: "3.9"
services:
  QbAutoDelt:
      container_name: qbautodelt
      image: limedrive/qbautodelt:latest
      environment:
        - PYTHON_QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE=true
      volumes:
        - 'path/to/config/:/qb-auto-delt/config:ro'
        - 'path/to/log:/qb-auto-delt/log'
      restart: unless-stopped
```
### Exemple ***docker run*** :

```docker
docker run -d \
    --name=qbautodelt
    -e PYTHON_QBITTORRENTAPI_DO_NOT_VERIFY_WEBUI_CERTIFICATE=true \
    -v path/to/config/:/qb-auto-delt/config:ro \
    -v path/to/log:/qb-auto-delt/log \
    --restart unless-stopped \
    limedrive/qbautodelt:latest
```

---

# Configuration du script:

Pour configuré vos préférance édité le fichier : 

**`config/qb-auto-delt.config.yml`**

___

## Identifiant pour la webUI de qBittorrent :
- Mettre vos identifant d'acses a la webUI de qbitorrent ici:
```yml
qBittorrent:
  host: "127.0.0.1:8080"
  user: "admin"
  password: "adminadmin"
```
| Options | Exemples | Description |
|:------|:------|--------:|
| **host:** | "127.0.0.1:8080" | \<hostIP>:\<port> |
| **user:** | "admin" | \<WebUI User Name> |
| **pass:** | "adminamin" | \<WebUI Password> |
> Avec votre instalation docker il est possible et conseillé de mettre **qBittorrent** et **Qbautodelt** sur le meme network docker (bridge): Dans se cas renseigner dans le host simplement l'adresse local de votre docker et le port exemple : ***"qbittorrent:8080"***

___

## Configuration de la méthode de controle de l'espace disque et déclanchement de la suppréssion:
- Le script propose deux méthode de controle de l'espace diques restant qui déclanche sa suppression, le contol par % ne dépend pas de l'api de qbittorrent.
> Seul True n'est disponible si vous utilisé ce script pour une instance distante (ex: Seedbox)
> il est conseillé d'utilisé True en docker également, sans quoi vous aurai besoin de monter en volume, votre dossier de téléchargement afin que le script puisse calculé a l'espace disque

```yml
ControlMethode: True
```
| Options | Description |
|:------|--------:|
| **True** | Déclanchement de la suppréssion quand il ne reste que xx GiB d'espace libre sur votre disque |
| **False** | Déclanchement de la suppréssion quand vous dépassé XX % d'espace disque |

### **Réglages des option inérante a la méthode de contrôle :**
> Si **ControlMethode: False**
- Pourcentage d'espace disque qui déclenche la suppression des torrents et path du disque a surveillé.
```yml
disk_Usage_By_Percent:
  max: 80
  path: "./"
```
| Options | Exemples | Description |
|:------|:------|--------:|
| **max:** | 80 | limite en % d'espace disque avant le déclanchement du script de supréssion |
| **path:** | "./" | Path a surveillé, peut etre la racine de votre partition, ou le path de votre montage du dossier de téléchargement si vous utilisé docker. |

### **Qantité d'espace disque restante exprimé en GiB qui déclenche la suppression des torrents.**
> Si **ControlMethode: True**
- Paramétrage de la limite de quantité d'espace disque restant qui déclenche la suppression des torrents:
```yml
disk_Usage_By_GiB:
  val: 35
```
| Options | Exemples | Description |
|:------|:------|--------:|
| **val:** | 35 | limite en GiB d'espace disque restant avant le déclanchement du script de supréssion |

---
# Logging :

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
