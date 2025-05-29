
# make the code as Python 3 compatible as possible
from __future__ import print_function, division, absolute_import

import os

top_html = """
<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"https://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title> blog | nworbmot:tombrown</title>
<link rel="stylesheet" type="text/css" href="../theme.css" />
<script type="text/javascript" src="https://orgmode.org/mathjax/MathJax.js"></script>
<script type="text/javascript">
<!--/*--><![CDATA[/*><!--*/
    MathJax.Hub.Config({
        // Only one of the two following lines, depending on user settings
        // First allows browser-native MathML display, second forces HTML/CSS
        //  config: ["MMLorHTML.js"], jax: ["input/TeX"],
            jax: ["input/TeX", "output/HTML-CSS"],
        extensions: ["tex2jax.js","TeX/AMSmath.js","TeX/AMSsymbols.js",
                     "TeX/noUndefined.js"],
        tex2jax: {
            inlineMath: [ ["\\(","\\)"] ],
            displayMath: [ ['$$','$$'], ["\\[","\\]"], ["\\begin{displaymath}","\\end{displaymath}"] ],
            skipTags: ["script","noscript","style","textarea","pre","code"],
            ignoreClass: "tex2jax_ignore",
            processEscapes: false,
            processEnvironments: true,
            preview: "TeX"
        },
        showProcessingMessages: true,
        displayAlign: "center",
        displayIndent: "2em",

        "HTML-CSS": {
             scale: 100,
             availableFonts: ["STIX","TeX"],
             preferredFont: "TeX",
             webFont: "TeX",
             imageFont: "TeX",
             showMathMenu: true,
        },
        MMLorHTML: {
             prefer: {
                 MSIE:    "MML",
                 Firefox: "MML",
                 Opera:   "HTML",
                 other:   "HTML"
             }
        }
    });
/*]]>*///-->
</script>
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

    start_string = '<div id="content">'

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
    if file_name[-4:] == ".org":
        html_name = file_name[:-3] + "html"
        if os.path.isfile(html_name) and os.path.getmtime(html_name) > os.path.getmtime(file_name):
            print(f"{file_name} was already processed, skipping")
        else:
            print(f"processing {file_name}")
            process_org(file_name)
