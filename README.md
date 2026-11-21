
This is the repository of
[org-mode](https://en.wikipedia.org/wiki/Org-mode) files for my blog
at:

<https://nworbmot.org/blog/>

Through the git versioning you can see changes I have made since
publishing each entry.

Run `python blog.py` from this directory to export changed Org posts and
refresh `rss.xml`. The feed uses the titles, dates, and summaries in
`index.mar` and includes the full exported posts. Summary rendering uses
Python-Markdown, which can be installed in the Python environment or made
available through the `markdown_py` command.

Publish `rss.xml` alongside the blog HTML. The blog index's subscribe link
is rendered from `index.mar` by the parent site's `generate.py`.
