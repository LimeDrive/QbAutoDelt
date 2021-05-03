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

>Le script à pour l'instant vocation à tourner dans un environnement python dockerisé sur serveur, mais il est tout a fait possible de ne l'executer qu'une seule fois comme tout script python. 

>The script is for the moment intended to run in a dockerized python environment. But he can ben launched in a one shot side.

---
# Installation


- Assurez vous d'avoir Python 3
- Clonez le repos git
- Editez vos préférences et paramétrez votre configuration dans qb-auto-delt.config.yml
- Ouvrez une console dans le dossier cloné précédemment.
- Installez les dépandance et lancez le script via les 2 commandes ci-dessous :
```zsh
pip3 install -r requirements.txt
python3 main.py
```


## Docker et docker-compose (recommandé)

### Création des fichier des répertoires partagés et montage des volumes:

* Créez un repertoire **_config/_** et un répertoire **_log/_** qui vont être montés dans votre docker.

* Récupérez les fichiers yml *qb-auto-delt.config.yml* et placez le dans le dossier :`/config`

 `curl -LJO https://raw.githubusercontent.com/LimeDrive/qb-auto-delt/master/config/GeneralSetting.yml `
 `curl -LJO https://raw.githubusercontent.com/LimeDrive/qb-auto-delt/master/config/TorrentsSelectionSetting.yml `


* Editez les pour les adapter à votre configuration. Voir détaile plus bas. 

* Lancez le containeur docker en montant les volumes comme dans l'exemple donné ci-dessous :
    * `-v /PATH/TO/LOCAL/log:/qb-auto-delt/log`
    * `-v /PATH/TO/LOCAL/config:/qb-auto-delt/config:ro`

### Exemple avec ***docker-compose*** : _(recommandé)_

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
### Exemple avec ***docker run*** :

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

Pour configurer vos préférences, éditez les fichiers : 

**`config/GeneralSetting.yml`** et **`config/TorrentsSelectionSetting.yml`**

> Pour tout changements dans `GeneralSetting.yml` il vous faudra relancé le script / docker.

> Les changement dans `TorrentsSelectionSetting.yml`sont prit en compte imédiatement.

___

## **Identifiants pour la webUI de qBittorrent : `GeneralSetting.yml`**
- Mettez vos identifants d'accès a la webUI de qbitorrent :
```yml
qBittorrent:
  host: "127.0.0.1:8080"
  user: "admin"
  password: "adminadmin"
```
| Options | Exemples | Description |
|:------|:------|--------|
| **host:** | "127.0.0.1:8080" | \<hostIP>:\<port> |
| **user:** | "admin" | \<WebUI User Name> |
| **pass:** | "adminamin" | \<WebUI Password> |
> Avec votre installation docker, il est possible et conseillé de mettre les containeurs **qBittorrent** et **Qbautodelt** sur le même network docker (bridge): Pour faire cela, renseignez dans le host l'adresse locale de votre docker et le port de la manière suivante : ***"qbittorrent:8080"***

___

## **Configuration de la méthode de contrôle de l'espace disque et déclanchement de la suppression: `GeneralSetting.yml`**
- Le script propose deux méthode de contrôle de l'espace dique restant qui déclenche la/les suppression(s), le contrôle par pourcentage ne dépend pas de l'api de qbittorrent.
> Seul True est disponible si vous utilisez ce script pour une instance distante (ex: Seedbox)
> il est conseillé d'utiliser True en docker également, sans quoi vous aurez besoin de monter en volume, votre dossier de téléchargement afin que le script puisse calculer  l'espace disque restant

```yml
ControlMethode: True
```
| Options | Methode | Description |
|:------|------|--------|
| **True** | GiB |Déclenchement de la suppression quand il ne reste plus que xx GiB d'espace libre sur votre disque |
| **False** | % |Déclenchement de la suppression quand vous dépassez un certain taux d'occupation de l'espace disque disponible (%) |

### **Réglages des options inérantes a la méthode de contrôle :**
> Si **ControlMethode: False**
- Pourcentage d'espace disque qui déclenche la suppression des torrents et path du disque a surveiller.
```yml
disk_Usage_By_Percent:
  max: 80
  path: "./"
```
| Options | Exemples | Description |
|:------|------|--------|
| **max:** | 80 | Limite en % d'espace disque avant le déclenchement du script de supression |
| **path:** | "./" | Path a surveiller, ce peut être la racine de votre partition, ou le path de votre montage du dossier de téléchargement si vous utilisez docker. |

### **Qantité d'espace disque restante exprimée en GiB qui déclenche la suppression des torrents.**
> Si **ControlMethode: True**
- Paramétrage de la valeur minimale d'espace disque restant qui déclenche la suppression des torrents:
```yml
disk_Usage_By_GiB:
  val: 35
```
| Options | Exemples | Description |
|:------|------|--------|
| **val:** | 35 | limite en GiB d'espace disque restant avant le déclenchement du script de suppression |

## **Mode Sécurisé : `GeneralSetting.yml` (utile pour tester vos réglages)**
- Mode de sécurité, il demande à l'utilisateur une confirmation pour la suppression du(des) torrent(s).
> Utilisable uniquement si vous lancé le script sans docker. Permet de tester en toute sécurité la sélection résultant de vos réglages, et le compotement du module de suppression.

> Utilisateur docker. Bien verifier que l'option soit désactivée (False): Autrement le programme plante ^^
```yml
safe: False
```
| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Demande à l'utilisateur une confimation en console |
| **False** | Désactivé | Ne demande pas de confirmation, et supprime si tous les paramètres sont réunis |

## **Intervalle entre les exécutions du programme: `GeneralSetting.yml`**
- Réglage de l'intervalle d'exécution du programme.
```yml
interval: 15
```
| Options | Exemples | Description |
|:------|------|--------|
| **interval:** | 15 | Le script va se ré-exécuter automatiquement toutes les 15 minutes |

## **Fixe For qBitorrent-NoX Api: `GeneralSetting.yml`**
- Si vous utilisez une version de qbittorrent-nox en pkg, elle n'a pas été mise a jour depuis plus d'un an... Je vous conseille d'en changer en utilisant le système docker. Toutefois, si vous voulez restez dessus, activez cette option a des fins de compatibilité avec les anciennes versions de l'API.
> Sachez que la reconaissance des torrents publics sera moins précise, tout comme le temps de seed réel ( donc prévoir de la marge pour les H&R )...
```yml
fix: False
```
| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Fix de compatibilité activé |
| **False** | Désactivé | \<default> |

## **Compte a rebours - Goody pour les utilisateurs HORS DOCKER: `GeneralSetting.yml`**
- En console vous aurez un compte a rebours entre chaque exécution du script dans le logging info
> A désactiver pour docker. Dans l'absolu, ce n'est pas gênant, mais les service comme portainer qui envoient des logs en temps réel n'apprécient pas vraiment.
```yml
countdown: False
```
| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Pour les utilisateurs sur console |
| **False** | Désactivé | \<default> |

## **Suppression automatique des torrents publics et/ou de certains Tags: `GeneralSetting.yml`\<BETA>**
- Supprime automatiquement les torrents publics ou/et qui ont des tags ou catégories Prioritaire de votre seedbox après un certain temps de seed. Cette option bypass le contrôle d'espace disque, donc que vous ayez de la place ou non, les torrents concernés seront supprimés si ils réunissent les conditions.
> L'option Public est destiné a ceux qui ont un service de syncronisation (rclone ou rsync) en place qui aura aux préalable fait une copy de vos fichier sur cloud ou sur un espace de stockage automatiquement.

> Pour la suppression par tags ou catégorie veillez a sauvegarder vos fichiers avant de tagger le torrent manuellement.

```yml
autoSupp:
  public: False
  priority: True
  minSeedTime: 2
```
- `public:`

| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Va automatiquement supprimer les torrent publics |
| **False** | Désactivé | \<default> |
- `priority:`

| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Va automatiquement supprimer les torrents qui ont un tag ou une catégorie prioritaire |
| **False** | Désactivé | \<default> |
- `minSeedTime: 2`

| Options | Exemples | Description |
|:------|------|--------|
| **minSeedTime:** | 2 | Temps de seed en heure minimum du torrent avant de prendre en compte l'auto-supression |

## **Notification Discord: `GeneralSetting.yml`**
- Paramétrage des notifications sur discord
> Utilise un Webhook pour envoyer les notifications émanant du serveur vers un salon textuel.
```yml
discord:
  use: False # True = Oui/Yes, False = Non/No
  webhook: "https://discord.com/api/webhooks/8345$$$$$$$$92500/Hq0K$$$$$$$$$$$$$$$2-5"
```
### Activation:
| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Envoie les notifications |
| **False** | Désactivé | \<default> |
### Webhook
| Options | Exemples | Description |
|:------|------|--------|
| **webhook:** | `"url"` | Lien du Webhook. Se référer a google pour savoir comment l'obtenir :) |

## **Paramètres pour le tri et la sélection des torrents à supprimer en priorité : `TorrentsSelectionSetting.yml`**
- Ensemble de paramètres qui influent sur la sélection des torrents à supprimer lorsque critère défini plus haut est atteint (% ou Gb).

```yml
min_SeedTime: 80
publicPriority: False
countSeeder: 30
min_Ratio: 0
```
### Temps de Seed Minimum:
| Options | Exemples | Description |
|:------|------|--------|
| **min_SeedTime:** | 80 | Temps de seed minimum en heure du torrent avant de le prendre en compte |
### publicPriority:
| Options | States | Description |
|:------|------|--------|
| **True** | Activé | Fait passer en priorité les torrents publics, peut importe s'ils matchent avec les autres paramètres définis |
| **False** | Désactivé | \<default> |
### Nombre Minimum de seeder:
| Options | Exemples | Description |
|:------|------|--------|
| **countSeeder:** | 30 | Nombre minimum de seeders restant sur le torrent avant de le prendre en compte pour la suppression |
### Ratio Minimum:
| Options | Exemples | Description |
|:------|------|--------|
| **min_Ratio:** | 0 | Ratio minimum sur le torrent avant de le prendre en compte pour la suppression |

## **Définition des Tags et étiquettes (Labels) : `TorrentsSelectionSetting.yml`**
Les **étiquettes** aka **Tags** doivent être définies manuellement. Elle sont sensibles à la casse (minuscules/majuscules) donc `"MonTags"` est différent de `"montags"`. Et doivent être encadrés de `" "`
```yml
Torrents_Tags:
  priority:
    - "PUBLIC"
    - "TODELETE"
  prefer:
    - "PRIO"
    - "TOBAD"
  exclud:
    - "DONOT"
    - "PERSO"

Torrents_Category:
  priority:
    - "Remux"
    - "Trash"
  prefer:
    - "radarr"
    - "tv-sonarr"
  exclud:
    - "KeepFolder"
    - "Perso"
```

| Options | Def. |
|:------|------|
| **Torrents_Tags:** | Pour définir les Tag |
| **Torrents_Category:** | Pour définir les Catégories |

- Le script distingue 3 types de tags et/ou catégories:
    - **Prioritaire:** Haute priorité sur la sélection = `priority:`
    > Est utilisée notament par le processus de suppression automatique.
    - **Préferé:** Fait passer les torrents en haut de la liste dans le processus de sélection, mais après les prioritaires = `prefer:`
    > N'est pas pris en compte dans la suppression automatique.
    - **Exclusion:** Ne prend pas du tout en compte le torrent. = `exclud:`
    > Surplombe tout, que le torrent soit public ou non et que la suppression automatique soit activée ou non, le torrent ne sera PAS sélectionné ni supprimé par le script


## **Définition du calcule de score : ## `TorrentsSelectionSetting.yml`**
- Ensemble de paramètres qui influent sur la sélection des torrents à supprimer lorsque critère défini plus haut est atteint (% ou Gb). Le script utilise un systeme a points, la base et de 10, le temps de seed, le ratio et la popularité du torrent augmente cette base. Les torrents supprimé en premier sont ceux avec le plus de point.
```yml
Scoring_Caculation:
  seed_Time_Score: 0.5
  ratio_Score: 2
  popularity_Score: 0.1
```
### Point rapporté par le Temps de Seed:
| Options | Exemples | Description |
|:------|------|--------|
| **seed_Time_Score:** | 0.5 | Multiplicateur du temps de seed, *1 jour de seed et score 0,5 point*  |
### Point rapporté par la Valeur du Ratio:
| Options | Exemples | Description |
|:------|------|--------|
| **ratio_Score:** | 2 | Multiplicateur du ratio, *2 de ratio est score 4 point*  |
### Point rapporté par la Popularité du torrent:
| Options | Exemples | Description |
|:------|------|--------|
| **popularity_Score:** | 0.1 | Multiplicateur sur le nombre de seeder actif sur le Torrent, *50 seeder actif et score 5 point*  |
```yml
  # Exemples to use this setting Base are always = 10
  ## Torrent with ratio 3 seeding since 7 days and with 100 active seeder
  ### 10 + (7 x 0,5) + ( 3 x 2 ) + ( 100 x 0.1 ) = 29,5
  ## Torrent with ratio 3 on seeding since 20 days and with 50 active seeder
  ### 10 + (20 x 0,5) + ( 3 x 2 ) + ( 50 x 0.1 ) = 31 ### SeedTime Wine
  ## Torrent with ratio 6 on seeding since 7 days and with 100 active seeder
  ### 10 + (7 x 0,5) + ( 6 x 2 ) + ( 100 x 0.1 ) = 35,5 ### ratio Wine
  ## Torrent with ratio 3 on seeding since 7 days and with 400 active seeder
  ### 10 + (7 x 0,5) + ( 1 x 2 ) + ( 400 x 0.1 ) = 55,5 ### Active Seeder Wine

```
---
# Logging :

Le log qui enregistre le processus de sélection des torrents à supprimer se trouve dans le fichier : 

`log/torrentSlection.log`

Le log de suivi général se trouve dans le fichier : 

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
