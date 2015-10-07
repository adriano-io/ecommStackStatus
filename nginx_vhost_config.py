#!/usr/bin/env python2

import re
import glob

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

conffile = "./amalg.conf"
stanza_count = 0
server_start = 0

def importfile(filename, keyword):

    files = glob.iglob(filename)
    combined = ""

    for onefile in files:
        #infile = open(filename, 'r')
        infile = open(onefile, 'r')

        for line in infile:
            #print "%s" % line.rstrip()
            #print "%s" % line.strip() # removes whitespace on left and right
            result = re.match('\s*%s\s+(\S+);' % keyword, line.strip() )
            #result = re.match('(include.*)', line.strip(), re.I | re.U )
            if result:
                combined += "#"+line+"\n"
                #print "#include %s " % result.group(1)
                combined += importfile(result.group(1),keyword)
            else:
                combined += line
                #print line.rstrip()
    return combined

#infile = open(onefile, 'r')

#wholeconfig = infile.readlines()
wholeconfig = importfile(conffile,"include")
#print wholeconfig

# list structure
# [ server stanza { line : { listen: [ ], server_name : [ ], root { location : path } } } ]

linenum = 0
nginx_stanzas = {} #AutoVivification()
for line in wholeconfig.splitlines():
    linenum += 1
    # this doesn't do well if you open and close a stanza on the same line
    if len(re.findall('{',line)) > 0 and len(re.findall('}',line)) > 0:
        print "This script does not consistently support opening { and closing } stanzas on the same line."
    stanza_count+=len(re.findall('{',line))
    stanza_count-=len(re.findall('}',line))
    result = re.match('^\s*server', line.strip() )
    if result:
        server_start = stanza_count
        server_line = str(linenum)
        if not server_line in nginx_stanzas:
            nginx_stanzas[server_line] = { }
    # are we in a server block, and not a child stanza of the server block? is so, look for keywords
    # this is so we don't print the root directive for location as an example. That might be useful, but isn't implemented at this time.
    if server_start == stanza_count:
        # we are in a server block
        #result = re.match('\s*(listen|server|root)', line.strip())
        result = re.match('\s*(listen|server_name|root)\s*(.*)', line.strip("\s\t;"))
        if result:
            #print line.strip()
            if result.group(1)=="listen":
                if not result.group(1) in nginx_stanzas[server_line]:
                    nginx_stanzas[server_line][result.group(1)] = []
                nginx_stanzas[server_line][result.group(1)] += [result.group(2)]
                #nginx_stanzas[server_line][result.group(1)].append(result.group(2)) # WORKS!
                #print result.group(2)
                print "listen %s" % result.group(2)
            if result.group(1)=="server_name":
                if not result.group(1) in nginx_stanzas[server_line]:
                    nginx_stanzas[server_line][result.group(1)] = []
                nginx_stanzas[server_line][result.group(1)] += result.group(2).split()
                #nginx_stanzas[server_line][result.group(1)].append(result.group(2)) # WORKS!
                # nothing here
                print "server_name %s" % result.group(2)
            if result.group(1)=="root":
                if not result.group(1) in nginx_stanzas[server_line]:
                    nginx_stanzas[server_line][result.group(1)] = []
                nginx_stanzas[server_line][result.group(1)] += result.group(2).split()
                #nginx_stanzas[server_line][result.group(1)].append(result.group(2)) # WORKS!
                # nothing here
                print "root %s" % result.group(2)
    # if the server block is bigger than the current stanza, we have left the server stanza we were in
    #if server_start > stanza_count and server_start > 0: # The lowest stanza_count goes is 0, so it is redundant
    if server_start > stanza_count:
        # we are no longer in the server { block
        server_start = 0
        print ""
print "%r" % nginx_stanzas