
# make the code as Python 3 compatible as possible
from __future__ import print_function, division, absolute_import

import os

top_html = """
<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title> blog | nworbmot:tombrown</title>
<link rel="stylesheet" type="text/css" href="../theme-260104.css" />
</head>
<body>
<div id="outer_box">
<div id="header">

<ul id="submenu">
<li><a href="../index.html">home</a></li>
<li><a href="../publications.html">publications</a></li>
<li><a href="../talks.html">talks</a></li>
<li><a href="../code.html">code</a></li>
<li><a href="../teaching.html">teaching</a></li>
<li><a href="../physics/index.html">other</a></li>
<li><a href="index.html">blog</a></li>
</ul>




</div>

<div id="main">
"""

bottom_html ="""
<p>Copyright Tom Brown, Licensed under <a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC BY 4.0</a></p>
</div>
</body>
</html>
"""

def process_org(file_name):

    print(file_name)

    command = "emacs {} --batch -f org-html-export-to-html --kill".format(file_name)

    os.system(command)

    file_name = file_name[:-4] + ".html"

    f = open(file_name,"r")
    html = f.read()

    f.close()

    print("Examining {}".format(file_name))

    if "outer_box" in html:
        print("File is already processed, skipping")
        return

    start_string = '<div id="content" class="content">'

    if start_string not in html:
        print("Start string not found, skipping")
        return


    end_string = '<div id="postamble" class="status">'
    if end_string not in html:
        print("End string not found, skipping")
        return

    new = html[html.find(start_string)+len(start_string):html.find(end_string)]

    new = top_html + new + bottom_html

    f = open(file_name,"w")

    f.write(new)

    f.close()

for file_name in os.listdir("."):
    if file_name == "blog.org":
        continue
    elif file_name[-4:] == ".org":
        html_name = file_name[:-3] + "html"
        if os.path.isfile(html_name) and os.path.getmtime(html_name) > os.path.getmtime(file_name):
            print(f"{file_name} was already processed, skipping")
        else:
            print(f"processing {file_name}")
            process_org(file_name)
