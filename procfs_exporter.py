#!/usr/bin/env python3

import json
import os
import datetime
import time
import multiprocessing

day = datetime.datetime.today().today().strftime("%Y-%m-%d")
log_path = "/var/log"
file_name = day + "-awesome-monitoring.log"
unix_time = time.time_ns()

metrics = []

def proc_stat():
    jiffy = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    num_cpu = multiprocessing.cpu_count()

    stat_fd = open('/proc/stat')
    for stat in stat_fd.readlines():
        if stat.startswith("cpu "):
            iowait = float(stat.split(' ')[6])
    stat_fd.close()

    time.sleep(1)

    stat_fd = open('/proc/stat')
    for stat in stat_fd.readlines():
        if stat.startswith("cpu "):
            iowait_n = float(stat.split(' ')[6])
    stat_fd.close()
    iowait_s = round(((iowait_n - iowait) * 100 / jiffy) / num_cpu, 2)
    return iowait_s

def write_json(metrics_dict):
    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    if not os.path.exists(log_path + "/" + file_name):
        open(log_path + "/" + file_name, 'w').close()

    if os.path.isfile(log_path + "/" + file_name):
        with open(log_path + "/" + file_name, "a") as f:
            f.write(json.dumps(metrics_dict) + '\n')

def load_average():
    with open("/proc/loadavg") as file:
        load_average = file.read().split(' ')[0]
        return float(load_average)

def mem_info():
    with open("/proc/meminfo") as file:
        for mem in file.readlines():
            if mem.startswith("MemAvailable:"):
                mem_available = int(mem.split(':')[1].lstrip().split(' ')[0])
            elif mem.startswith("SwapFree:"):
                swap_free = int(mem.split(':')[1].lstrip().split(' ')[0])
            elif mem.startswith("Active:"):
                mem_active = int(mem.split(':')[1].lstrip().split(' ')[0])
        return [mem_available, swap_free, mem_active]

load_average = load_average()
iowait = proc_stat()
mem_available = mem_info()[0]
swap_free = mem_info()[1]
mem_active = mem_info()[2]

metrics_dict = {"timestamp": unix_time, "load average": load_average, "iowait": iowait, "mem_available": mem_available,
                "swap_free": swap_free, "mem_active": mem_active}

write_json(metrics_dict)

