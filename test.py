import os


def hello(arg1):
    return os.chown(arg1, 0, 0)

def hello_2(arg1):
    a = arg1
    return a