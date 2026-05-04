import os
import fnmatch

def get_request_files(path, pattern):
    return fnmatch.filter(os.listdir(path), pattern)