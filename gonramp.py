#!/usr/bin/env python
from CyRODS import CyVerseiRODS
from os import path

ap = argparse.ArgumentParser(description="CyVerse/iRODS interaction")
ap.add_argument("--upload", action='store_true')
ap.add_argument("--localsource")
ap.add_argument("--remotedestination")
ap.add_argument("--user")
ap.add_argument("--password")

args = ap.parse_args()

kwargs = {}
if args.user and args.password:
    kwargs["user"] = args.user
    kwargs["password"] = args.password

# initialize connection
conn = CyVerseiRODS(**kwargs)

# upload
if args.upload:
    if args.localsource is None:
        parser.error("--upload requires --localsource, --remotedestination is optional")
    else:
        args.remotedestination = conn.user_dir if not args.remotedestination else args.remotedestination
        conn.recursive_upload(args.localsource, args.remotedestination)

dataset_dir = args.remotedestination.split(',')[0] + "_files/"
# UCSC has a "hub.txt"
# JBrowse has a "json/trackList.json"
ucsc_specific = dataset_dir + "hub.txt"
jbrowse_specific = dataset_dir + "json/trackList.json"
local = ""
if path.isfile(ucsc_specific):
    local = ucsc_specific
    
elif path.isfile(jbrowse_specific):
    local = jbrowse_specific
else:
    raise OSError("Neither '{}' nor '{}' found.".format(ucsc_specific, jbrowse_specific))

# generate link
# generate HTML file
