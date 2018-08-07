#!/usr/bin/env python
from cyverse_irods.CyRODS import CyVerseiRODS

from datetime import datetime
from os import path, walk
import argparse

ap = argparse.ArgumentParser(description="CyVerse/iRODS interaction")
ap.add_argument("--upload", action='store_true')
ap.add_argument("--localsource")
ap.add_argument("--remotedestination")
ap.add_argument("--user")
ap.add_argument("--password")
ap.add_argument("--timestamp", action="store_true")
ap.add_argument("--output")

anon_prefix = "https://de.cyverse.org/anon-files/iplant/home/"

args = ap.parse_args()

kwargs = {}
if args.user and args.password:
    kwargs["user"] = args.user
    kwargs["password"] = args.password

# initialize connection
conn = CyVerseiRODS(**kwargs)

default_perm = {
  "type" : "read",
  "name" : "anonymous",
  "zone" : conn.KWARGS["zone"]
}

# generate timestamp, if relevant
if args.timestamp or not args.remotedestination:
    timestamp = datetime.utcnow().strftime("_%y%m%dT%H%M%S")
    if not args.remotedestination:
        args.remotedestination = args.user + "_hub" + timestamp
    else:
        args.remotedestination = args.remotedestination + timestamp

remote_subdir = args.remotedestination

args.remotedestination = conn.user_dir + "/" + args.remotedestination

# UCSC has a "hub.txt"
# JBrowse has a "myHub/trackList.json"
ucsc_specific = remote_subdir + "/hub.txt"
jbrowse_specific = remote_subdir
data_url = anon_prefix + kwargs["user"] + "/"
hubtype=""
title=""
header="Link to generated {} hub:"

filesize = 0

# find where the files REALLY live
args.localsource = ".".join(args.localsource.split('.')[:-1]) + "_files/"

# ensure we have a valid archive
if path.isfile(args.localsource + "myHub/hub.txt"):
    data_url = data_url + ucsc_specific
    args.localsource = args.localsource + "myHub/"
    hubtype="UCSC"
    url="http://genome.ucsc.edu/cgi-bin/hgHubConnect?hgHub_do_redirect=on&hgHubConnect.remakeTrackHub=on&hgHub_do_firstDb=1&hubClear={}"
elif path.isfile(args.localsource + "myHub/trackList.json"):
    args.localsource = args.localsource + "myHub/"
    data_url = data_url + jbrowse_specific
    url="https://de.cyverse.org/anon-files/iplant/home/shared/G-OnRamp_hubs/JBrowse-1.12.3/index.html?data={}"
    hubtype = "JBrowse"
elif path.isfile(args.localsource + "myHub"):
    raise OSError("ERROR: myHub is a file, suggesting that this is an imported history, which does not work with G-OnRamp archive creators")
else:
    raise OSError("Neither '{}' nor '{}' found.".format(args.localsource + "myHub/hub.txt", args.localsource + "myHub/trackList.json"))

# get filesize
for dirpath, dirnames, filenames in walk(args.localsource):
    for f in filenames:
        fpath = path.join(dirpath, f)
        filesize += path.getsize(fpath)

print("bytes: {}".format(filesize))

sizestring = "<b>{}</b> {}"
# gigs
magnitude = 0.0
unit = ""
if int(filesize / 1000000000):
    magnitude = filesize/1000000000
    unit = "GB"
elif int(filesize / 1000000):
    magnitude = filesize/1000000
    unit = "MB"
elif int(filesize / 1000):
    magnitude = filesize/1000
    unit = "kB"
else:
    magnitude = filesize
    unit = "B"

sizestring = sizestring.format(magnitude, unit)

# upload
if args.upload:
    if args.localsource is None:
        parser.error("--upload requires --localsource, --remotedestination is optional")
    else:
        print("conn.recursive_upload(args.localsource, args.remotedestination, default_perm)\n{}\n{}\n{}\n\n".format(args.localsource, args.remotedestination, default_perm))
        conn.recursive_upload(args.localsource, args.remotedestination, default_perm)

header = header.format(hubtype)
url = url.format(data_url)

# generate link
html_content = str('''
<!DOCTYPE html>\
<html lang="en">\
  <head>\
    <title>{}</title>\
  </head>\
  <body>\
    <h1>{}</h1>\
    <a href="{}">Generated Hub at {}</a>\
    <h3>Hub size:</h3> <span style="color:blue">{}</span>\
  </body>\
</html>''')

# generate HTML file
if args.output:
    with open(args.output, "w") as file:
        file.write(html_content.format(title, header, url, kwargs["user"] + "/" + remote_subdir, sizestring))
