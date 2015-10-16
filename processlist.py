#!/usr/bin/env python2

import re
import os

def processlist(var_filter=""):
    """
    var_filter = "text to search with"
    using this as the filter will find an executable by name whether it was call by absolute path or bare
    "^(\S*/bash|bash)"
    """
    processlist = {}
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    
    for pid in pids:
        try:
            pscmd = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read().replace("\000"," ").rstrip()
        except IOError: # proc has already terminated
            continue
        if pscmd:
            if var_filter:
                ps_filter = re.search(var_filter,pscmd)
                if ps_filter:
                    processlist[pid] = pscmd
            else:
                processlist[pid] = pscmd
    return(processlist)

# works
#pslist = processlist("^(\S*/bash|bash)")
#for key in pslist.keys():
#    print "%6d %s" % (int(key),pslist[key])

# also works
#for key, value in processlist("^(\S*/bash|bash)").iteritems():
#    print "%6d %s" % (int(key),value)
    
# works, no filter
#for key, value in processlist().iteritems():
#    print "%6d %s" % (int(key),value)

import psutil
import os
var_filter = "http"

def daemon_exe(match_exe):
    daemons = {}
    
    pidlist = psutil.get_pid_list()
    for pid in pidlist:
        p = psutil.Process(pid)
        try:
            if p.exe:
                #match_exe = ["httpd", "apache2", "nginx", "bash"]
                for daemon_name in match_exe:
                    if os.path.basename(p.exe) == daemon_name:
                        if not "daemon_name" in daemons:
                            daemons[daemon_name] = { "exe" : [] }
                        daemons[daemon_name]["exe"] += [p.exe]
                        #print p.exe
        except:
            #print "You should run this as root"
            pass
    return daemons

daemons = daemon_exe(["httpd", "apache2", "nginx", "bash"])
#for key,value in daemons.iteritems():
#    print "%s %r" % (key,value)
if "apache2" in daemons:
    print "apache2 on Debian/Ubuntu %s" % daemons["apache2"]["exe"][0]
if "httpd" in daemons:
    print "httpd on Red Hat/CentOS %s" % daemons["httpd"]["exe"][0]