import os

import server

def writeable_directory(path):
    writeable = os.access(path, os.W_OK)
    directory = os.path.isdir(path)

    if (not writeable) or (not directory):
        server.error(500, "Cannot write to %s" % path)
