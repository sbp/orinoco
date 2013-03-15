import os
import shutil
import sys
import time

import authenticate
import check
import links
import request
import server

def handle(user):
    start = time.time()
    unixtime = int(time.time())


    # 1. get paths and check permissions

    docroot = request.root(os.environ)
    check.writeable_directory(docroot)

    name = request.name(os.environ)
    page_path = os.path.join(docroot, name)

    versions = os.path.join(docroot, "site", "versions")
    check.writeable_directory(versions)

    version_name = "%s_%s_%s" % (unixtime, user, name)
    version_path = os.path.join(versions, version_name)

    if os.path.isfile(version_path):
        server.error(500, "You can't save more than once per second")


    # 2. write a temporary file

    try:
        temp_path = os.path.join(docroot, version_name)

        with open(temp_path, "wb") as temp:
            for line in sys.stdin.buffer:
                temp.write(line)
            if not line.endswith(b"\n"):
                temp.write(b"\n")
            temp.flush()
            os.fsync(temp.fileno())
    except Exception as err:
        server.error(500, "Could not make a temporary file: %s" % err)


    # 3. test for duplicates

    if os.path.isfile(page_path):
        old_size = os.path.getsize(page_path)
        new_size = os.path.getsize(temp_path)

        if old_size == new_size:
            import zlib

            old_check = 0
            with open(page_path, "rb") as f:
                for line in f:
                    old_check = zlib.adler32(line, old_check)

            new_check = 0
            with open(temp_path, "rb") as f:
                for line in f:
                    new_check = zlib.adler32(line, new_check)

            if old_check == new_check:
                os.remove(temp_path)
                server.error(500, "Won't save duplicate pages")


    # 4. copy temporary file to backup

    try:
        shutil.copy2(temp_path, version_path)
    except Exception as err:
        os.remove(temp_path)
        server.error(500, "Could not archive backup version: %s" % err)


    # 5. move temporary file into place

    existing = os.path.exists(page_path)

    try:
        shutil.move(temp_path, page_path)
    except Exception as err:
        os.remove(temp_path)
        server.error(500, "Could not move temporary file into place: %s" % err)

    size = os.path.getsize(page_path)
    took = time.time() - start
    message = "%s bytes, in %ss" % (size, round(took, 3))

    if existing:
        server.response(200, message)
    else:
        server.response(201, message)


    # 6. add metadata to change log

    changes_path = os.path.join(versions, "changes.log")
    entry = "%s %s %s\n" % (unixtime, user, name)

    with open(changes_path, "a") as f:
        f.write(entry)
        f.flush()
        os.fsync(f.fileno())


    # 7. scan for links and update database

    outbound_path = os.path.join(versions, "outbound.db")
    inbound_path = os.path.join(versions, "inbound.db")

    links.update(outbound_path, inbound_path, page_path, name)
