
#!/usr/bin/env python3

import psutil


# % disque usage
def diskusagecontrol():
    stat = psutil.disk_usage('./')
    percent = round(stat.percent)
    return percent

# Variable Global
DiskUsage = diskusagecontrol()

print(DiskUsage)
