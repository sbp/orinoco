import html.parser
import shelve

import request

database = shelve.open

class Parser(html.parser.HTMLParser):
    def __init__(self, *args, **kargs):
        html.parser.HTMLParser.__init__(self, *args, **kargs)
        self.avoid_collisions_links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "href" in attrs:
            link = attrs["href"]
            if not "/" in link:
                if "#" in link:
                    link = link.split("#", 1)[0]
                link = request.normalise(link)
                self.avoid_collisions_links.add(link)

def parse(path):
    parser = Parser(strict=False)
    with open(path, "rb") as f:
        for line in f:
            try:
                line = line.decode("utf-8")
            except:
                continue
            parser.feed(line)
    return parser.avoid_collisions_links

def update_inbound(inbound, name, previous_links, current_links):
    for previous in previous_links:
        if not (previous in current_links):
            inbound_links = inbound.get(previous) or set()
            try:
                inbound_links.remove(name)
            except KeyError:
                continue
            inbound[previous] = inbound_links

    for current in current_links:
        if not (current in previous_links):
            inbound_links = inbound.get(current) or set()
            inbound_links.add(name)
            inbound[current] = inbound_links

def update(outbound_path, inbound_path, page_path, name):
    outbound = database(outbound_path)
    inbound = database(inbound_path)

    current_links = parse(page_path)
    previous_links = outbound.get(name) or set()

    outbound[name] = current_links
    update_inbound(inbound, name, previous_links, current_links)

    outbound.close()
    inbound.close()
