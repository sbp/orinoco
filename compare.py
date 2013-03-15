import difflib
import html.parser
import itertools
import operator
import sys

class Parser(html.parser.HTMLParser):
    def __init__(self, *args, **kargs):
        html.parser.HTMLParser.__init__(self, *args, **kargs)
        self.avoid_collisions_nodes = []

    def handle_starttag(self, tag, attrs):
        attrs = " ".join(["=".join([a, '"%s"' % b]) for a, b in attrs])
        node = ("<%s %s>" % (tag, attrs)) if attrs else ("<%s>" % tag)
        self.avoid_collisions_nodes.append(node)

    def handle_endtag(self, tag):
        node = "</%s>" % tag
        self.avoid_collisions_nodes.append(node)

    def handle_data(self, data):
        if self.avoid_collisions_nodes:
            if not self.avoid_collisions_nodes[-1].startswith("<"):
                self.avoid_collisions_nodes[-1] += data
                return
        self.avoid_collisions_nodes.append(data)

    def handle_entityref(self, name):
        self.handle_data("&%s;" % name)

    def handle_charref(self, name):
        self.handle_data("&%s;" % name)

def character_data(node):
    return not node.startswith("<")

def content(line):
    return line[2:]

def out(text):
    # http://stackoverflow.com/questions/4601912
    sys.stdout.flush()
    sys.stdout.buffer.write(text.encode("utf-8"))

def lines(old, new):
    delta = difflib.ndiff(old, new)

    print("<!doctype html>")
    print("<style>ins.orinoco, ins.orinoco * { background: #cec; }</style>")
    print("<style>del.orinoco, del.orinoco * { background: #ecc; }</style>")
    first = operator.itemgetter(0)
    for item, group in itertools.groupby(delta, first):
        if item == "?":
            continue

        out("<!-- %s -->" % item)
        group = [content(line) for line in group]
        cdata = any(map(character_data, group))

        if cdata:
            if item == "+":
                out("<ins class='orinoco'>")
            elif item == "-":
                out("<del class='orinoco'>")

        if cdata or (item != "-"):
            for line in group:
                out(line)

        if cdata:
            if item == "+":
                out("</ins>")
            elif item == "-":
                out("</del>")

def files(a, b):
    parser_a = Parser()
    with open(a, "rb") as f:
        for line in f:
            try:
                line = line.decode("utf-8")
            except:
                continue
            parser_a.feed(line)
    old = parser_a.avoid_collisions_nodes

    parser_b = Parser()
    with open(b, "rb") as f:
        for line in f:
            try:
                line = line.decode("utf-8")
            except:
                continue
            parser_b.feed(line)
    new = parser_b.avoid_collisions_nodes

    lines(old, new)

