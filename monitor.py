import re
import time
import subprocess
import sys
import signal
from midi import midi

def signal_handler(signal, frame):
    print "caught signal"
    midi.close()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def tail_logs():
    # cmd = ['cf', 'logs', 'app-distribution-staging']
    cmd = ['cf', 'logs', 'allocations']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while(True):
        retcode = proc.poll()
        line = proc.stdout.readline()
        yield line
        if(retcode is not None):
            break

def extract_data(line):
    data = {}
    regex = r"[a-z0-9]+[[\-\.]{1}[a-z0-9]+]*\.[a-z]{2,6} - \[(.*)\] \"([A-Z]{3,4}) \/.* HTTP\/1\.1\" ([0-9]{3}) ([0-9]{1,10}) ([0-9]{1,10}) \".*\" \"(.*)\" .* x_forwarded_for:\"(.*)\""

    res = re.search(regex, line)
    if res:
        request_time = time.strptime(res.group(1), "%d/%m/%Y:%H:%M:%S +0000")
        data = {"time": request_time, "method": res.group(2), "status_code": int(res.group(3)), "content_length": int(res.group(5)), "user_agent": res.group(6), "x_forwarded_for": res.group(7) }

    return data

generator = tail_logs()
for line in generator:
    data = extract_data(line)
    if data:
        log = "Method: %s, Code: %s" % (data["method"], data["status_code"])
        print log
        try:
            midi.play_log(data["method"],data["content_length"],data["x_forwarded_for"],data["user_agent"],data["status_code"])
        except:
            print "error playing midi, continuing"
