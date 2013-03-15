import sys

def error(code, message):
    print("Status: %s" % code)
    print("Content-Type: text/plain")
    print()
    print(message)
    sys.exit(0)

def response(code, message):
    print("Status: %s" % code)
    print("Content-Type: text/plain")
    print()
    print(message)
