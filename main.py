
#!/usr/bin/env python3

import psutil


# % disque usage ./ comme path sur mac a l'air ok, a voir sur linux, et a mettre dans une variable
def diskusagecontrol():
    stat = psutil.disk_usage('./')
    percent = round(stat.percent)
    return percent

# Variable Global
DiskUsage = diskusagecontrol()

print(DiskUsage)
