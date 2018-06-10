#!/usr/bin/env python
from .cyverse-irods/CyRODS import CyVerseiRODS

from datetime import datetime
from os import path

ap = argparse.ArgumentParser(description="CyVerse/iRODS interaction")
ap.add_argument("--upload", action='store_true')
ap.add_argument("--localsource")
ap.add_argument("--remotedestination")
ap.add_argument("--user")
ap.add_argument("--password")
ap.add_argument("--timestamp", action="store_true")

anon_prefix = "https://de.cyverse.org/anon-files/"



args = ap.parse_args()

kwargs = {}
if args.user and args.password:
    kwargs["user"] = args.user
    kwargs["password"] = args.password

# initialize connection
conn = CyVerseiRODS(**kwargs)

default_perm = {
  "type" : "write",
  "name" : "anonymous",
  "zone" : CyRODS.KWARGS["zone"]
}


# generate timestamp, if relevant
if args.timestamp or not args.remotedestination:
    timestamp = datetime.utcnow().strftime("_%y%m%dT%H%M%S")
    if not args.remotedestination:
        args.remotedestination = args.user + timestamp
    else:
        args.remotedestination = args.remotedestination + timestamp



# upload
if args.upload:
    if args.localsource is None:
        parser.error("--upload requires --localsource, --remotedestination is optional")
    else:
        args.remotedestination = conn.user_dir if not args.remotedestination else args.remotedestination
        conn.recursive_upload(args.localsource, args.remotedestination, default_perm)

# this is the location of the file to write the url to
if args.output:
    html_content = gen_html()
    with open(args.output, "w") as file:
        file.write(html_content)

dataset_dir = args.remotedestination.split(',')[0] + "_files/"
# UCSC has a "hub.txt"
# JBrowse has a "json/trackList.json"
ucsc_specific = dataset_dir + "hub.txt"
jbrowse_specific = dataset_dir + "json"
local = ""
url = ""
hubtype=None
if path.isfile(ucsc_specific):
    local = ucsc_specific
    hubtype="UCSC"
    url="http://genome.ucsc.edu/cgi-bin/hgHubConnect?hgHub_do_redirect=on&hgHubConnect.remakeTrackHub=on&hgHub_do_firstDb=1&hubClear={}"
elif path.isfile(jbrowse_specific):
    local = jbrowse_specific
    url="https://de.cyverse.org/anon-files/iplant/home/shared/G-OnRamp_hubs/JBrowse-1.12.3/index.html?data={}"
    hubtype = "JBROWSE"
else:
    raise OSError("Neither '{}' nor '{}' found.".format(ucsc_specific, jbrowse_specific))

url.format(data_url)

# generate link
html = '''
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>{}</title>
  </head>
  <body>
    <h1>{}</h1>
    <a href="{}">Generated Hub</a>
  </body>
</html>
'''.format(title, header, url)




# generate HTML file
