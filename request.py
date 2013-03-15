import server

def root(env):
    try:
        docroot = env["DOCUMENT_ROOT"]
    except KeyError:
        server.error(500, "Document root not specified")

    return docroot

def normalise(name):
    if (not name) or (name == "."):
        name = "index.html"
    if not name.endswith(".html"):
        name += ".html"

    return name

def name(env):
    try:
        name = env["REQUEST_URI"]
    except KeyError:
        server.error(400, "Request URI not specified")

    if name.startswith("/"):
        name = name[1:]

    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if set(name) - allowed:
        server.error(403, "This page name is not allowed")

    name = normalise(name)

    # redundant
    if "_" in name:
        server.error(403, "Underscores in page names are not allowed")

    # redundant
    if "/" in name:
        server.error(403, "Nested directory editing is not allowed")

    return name
