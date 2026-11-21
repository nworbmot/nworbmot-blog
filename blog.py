
# make the code as Python 3 compatible as possible
from __future__ import print_function, division, absolute_import

import os
import re
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urljoin
from xml.etree import ElementTree as ET


BLOG_URL = "https://nworbmot.org/blog/"
CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
ATOM_NS = "http://www.w3.org/2005/Atom"
POST_HEADING = re.compile(r"^#[ \t]+(.+)$", re.MULTILINE)
POST_LINK = re.compile(r"\[(.+)\]\(([^\s()]+)\)")
POST_DATE = re.compile(r"Date:[ \t]*(\d{4}\.\d{2}\.\d{2})")
MAIN_START = '<div id="main">'

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

{}
""".format(MAIN_START)

bottom_html ="""
<p>Copyright Tom Brown, Licensed under <a href="https://creativecommons.org/licenses/by/4.0/deed.en">CC BY 4.0</a></p>
</div>
</body>
</html>
"""

def process_org(file_name):

    print(file_name)

    subprocess.run(
        ["emacs", file_name, "--batch", "-f", "org-html-export-to-html", "--kill"],
        check=True,
    )

    file_name = file_name[:-4] + ".html"

    f = open(file_name,"r", encoding="utf-8")
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

    f = open(file_name,"w", encoding="utf-8")

    f.write(new)

    f.close()


class FeedHTML(HTMLParser):
    """Resolve relative links and images in an HTML fragment."""

    def __init__(self, html, base_url):
        super().__init__(convert_charrefs=False)
        self.base_url = base_url
        self.parts = []
        self.feed(html)
        self.close()

    def rewrite_tag(self, tag, attrs, ending):
        updated = [
            (name, urljoin(self.base_url, value) if value and name in ("href", "src") else value)
            for name, value in attrs
        ]
        if updated == attrs:
            self.parts.append(self.get_starttag_text())
            return
        attributes = "".join(
            f' {name}="{escape(value, quote=True)}"' if value is not None else f" {name}"
            for name, value in updated
        )
        self.parts.append(f"<{tag}{attributes}{ending}")

    def handle_starttag(self, tag, attrs):
        self.rewrite_tag(tag, attrs, ">")

    def handle_startendtag(self, tag, attrs):
        self.rewrite_tag(tag, attrs, " />")

    def handle_endtag(self, tag):
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")


def render_summary(summary):
    try:
        from markdown import markdown
    except ModuleNotFoundError as error:
        if error.name != "markdown":
            raise
        # The site's Markdown renderer is also available as a standalone command.
        try:
            return subprocess.run(
                ["markdown_py"], input=summary, capture_output=True, encoding="utf-8", check=True
            ).stdout.strip()
        except FileNotFoundError as error:
            raise ValueError("RSS summaries require Python-Markdown or the markdown_py command") from error
    return markdown(summary)


def read_feed_entries(directory):
    sections = POST_HEADING.split((directory / "index.mar").read_text(encoding="utf-8"))
    if len(sections) == 1:
        raise ValueError("index.mar: no post headings found")

    entries = []
    urls = set()
    line = sections[0].count("\n") + 1
    for heading, body in zip(sections[1::2], sections[2::2]):
        location = f"index.mar:{line}"
        line += body.count("\n")
        link = POST_LINK.fullmatch(heading.strip())
        if link is None:
            raise ValueError(f"{location}: expected a linked post heading")
        title, path = link.groups()
        date_line, _, summary = body.lstrip("\n \t").partition("\n")
        date = POST_DATE.fullmatch(date_line.strip())
        try:
            published = datetime.strptime(date[1] if date else "", "%Y.%m.%d")
        except ValueError as error:
            raise ValueError(f"{location}: expected a valid Date: YYYY.MM.DD for {title}") from error

        url = urljoin(BLOG_URL, path)
        if url in urls:
            raise ValueError(f"{location}: duplicate post URL {url}")
        urls.add(url)
        summary = re.sub(r"(?m)^<br\s*/?>[ \t]*\Z", "", summary.strip()).rstrip()
        entries.append((published.replace(tzinfo=timezone.utc), title, path, url, summary))
    return sorted(entries, key=lambda entry: entry[0], reverse=True)


def generate_rss(directory):
    entries = read_feed_entries(directory)
    ET.register_namespace("content", CONTENT_NS)
    ET.register_namespace("atom", ATOM_NS)
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Tom Brown’s blog"
    ET.SubElement(channel, "link").text = BLOG_URL
    ET.SubElement(channel, "description").text = "Tom Brown on future scenarios for the energy system."
    ET.SubElement(
        channel, f"{{{ATOM_NS}}}link", href=urljoin(BLOG_URL, "rss.xml"),
        rel="self", type="application/rss+xml",
    )

    for published, title, path, url, summary in entries:
        html = (directory / path).read_text(encoding="utf-8")
        _, start, content = html.partition(MAIN_START)
        content, footer, _ = content.rpartition(bottom_html.strip())
        if not start or not footer or not content.strip():
            raise ValueError(f"{path}: could not find the exported article body")

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", isPermaLink="true").text = url
        ET.SubElement(item, "pubDate").text = format_datetime(published, usegmt=True)
        ET.SubElement(item, "description").text = "".join(FeedHTML(render_summary(summary), BLOG_URL).parts)
        ET.SubElement(item, f"{{{CONTENT_NS}}}encoded").text = "".join(FeedHTML(content.strip(), url).parts)

    ET.indent(rss)
    feed = ET.tostring(rss, encoding="utf-8", xml_declaration=True) + b"\n"
    ET.fromstring(feed)
    output = directory / "rss.xml"
    if output.exists() and output.read_bytes() == feed:
        return
    with TemporaryDirectory(dir=directory) as temporary_directory:
        temporary_feed = Path(temporary_directory) / output.name
        temporary_feed.write_bytes(feed)
        temporary_feed.replace(output)
    print(f"Updated {output.name}")


if __name__ == "__main__":
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

    try:
        generate_rss(Path("."))
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"RSS generation failed: {error}") from error
