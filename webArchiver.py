#!/bin/python3
import os
import hashlib
import csv
import datetime
import argparse
import shutil
import configparser


# define functions
def file_len(fname):
    """Returns the number of lines in a file."""
    if not os.path.isfile(fname):
        return(0)
    with open(fname) as f:
        count = 0
        for i, l in enumerate(f):
            count = i+1
    return(count)


def forcedir(file_path):
    """Forces a directories existence."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def hasher(filein, hname, blocksize):
    """Generates the hash of the file given."""
    htype = getattr(hashlib, hname, print)()
    if htype is None:
        print("wrong hash type")
        exit(1)
    with open(filein, 'rb') as fi:
        while True:
            data = fi.read(blocksize)
            if not data:
                break
            htype.update(data)
    return(htype.hexdigest())


def csv_find(filein, data):
    """Finds and returns the row number of the element given, in a CSV file."""
    if not os.path.isfile(filein):
        return(-1)
    with open(filein, 'rt') as fi:
        reader = csv.reader(fi, delimiter=',')
        for row in reader:
            hashout = row[1]  # location of hash
            if hashout == data:
                return(row[0])
        return(-1)


def csv_append(filein, data):
    """Appends the given data to a CSV file."""
    if not os.path.isfile(filein):
        pass
    with open(filein, 'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(data)


def file_worker(filedef, filerel):
    """Moves the file into another directory and then
    , replaces the file given with a symbolic link."""
    hashin = hasher(filedef, hashertype, hashblocksize)
    csvid = csv_find(csv1, hashin)
    if csvid == -1:
        csvid = file_len(csv1)+1
        csv_append(csv1, [csvid, hashin])
        shutil.move(filedef, archivedir1 + "/" + str(csvid))
    else:
        os.remove(filedef)
    csv_append(csv2, [datetimes, csvid, filerel])
    os.symlink(archivedir1 + "/" + str(csvid), filedef)


def folder_worker(directory):
    """Works down the directory tree of a given folder recursively."""
    for ff in os.listdir(directory):
        ffdef = directory + "/" + ff
        if os.path.isfile(ffdef):
            file_worker(ffdef, ff)
        else:
            folder_worker(ffdef)


if __name__ == "__main__":
    # set vars
    archivedir1 = os.path.expanduser("~") + "/archiver/files/"
    archivedir2 = os.path.expanduser("~") + "/archiver/archive/"
    csv1 = archivedir1 + "csv1"
    csv2 = archivedir1 + "csv2"
    datetimeformat = "%y.%m.%d-%H:%M"
    datetimes = datetime.datetime.now().strftime(datetimeformat)
    hashblocksize = 65536
    hashertype = "sha256"
    configfile = os.path.expanduser("~") + "/archiver/archiver.conf"
    # readtags
    piparser = argparse.ArgumentParser()
    piparser.add_argument("-fi", "--folderin", help="Input folder")
    piparser.add_argument("-fs", "--foldersave",
                          help="Archive save directory location")
    piparser.add_argument("-fa", "--folderarchive",
                          help="Archive archiving directory location")
    piparser.add_argument("-fl1", "--filelist1", help="Archive filelist1 location")
    piparser.add_argument("-fl2", "--filelist2", help="Archive filelist2 location")
    piparser.add_argument("-dtf", "--datetimeformat", help="Set datetime format")
    piparser.add_argument("-hb", "--hashblocksize", help="Set hash blocksize")
    piparser.add_argument("-ht", "--hashtype",
                          help="""
            Set hash type to one of:'blake2s', 'sha384',
            'sha512', 'sha3_256', 'sha256', 'md5', 'sha3_512',
            'sha3_224', 'shake_128', 'shake_256', 'sha1',
            'blake2b', 'sha224', 'sha3_384'""")
    piparser.add_argument("-c", "--configfile",
                          help="Set configfile in init format (in [DEFAULT])")
    piargs = piparser.parse_args()
    if piargs.configfile is not None:
        configfile = piargs.configfile
    # read config file
    config = configparser.ConfigParser()
    if os.path.isfile(configfile):
        config.read(configfile)
        if "DEFAULT" in config:
            if "folderarchive" in config["DEFAULT"]:
                archivedir2 = config["DEFAULT"]["folderarchive"]
            if "filelist1" in config["DEFAULT"]:
                csv1 = config["DEFAULT"]["filelist1"]
            if "filelist2" in config["DEFAULT"]:
                csv2 = config["DEFAULT"]["filelist2"]
            if "datetimeformat" in config["DEFAULT"]:
                datetimeformat = config["DEFAULT"]["datetimeformat"]
            if "hashblocksize" in config["DEFAULT"]:
                hashblocksize = int(config["DEFAULT"]["hashblocksize"])
            if "hashtype" in config["DEFAULT"]:
                hashertype = config["DEFAULT"]["hashtype"]
            if "foldersave" in config["DEFAULT"]:
                archivedir1 = config["DEFAULT"]["foldersave"]
    ##
    if piargs.folderin is None:
        print("Give input folder")
        exit(1)
    if piargs.foldersave is not None:
        archivedir1 = piargs.foldersave
    if piargs.folderarchive is not None:
        archivedir2 = piargs.folderarchive
    if piargs.filelist1 is not None:
        csv1 = piargs.filelist1
    if piargs.filelist2 is not None:
        csv2 = piargs.filelist2
    if piargs.datetimeformat is not None:
        datetimeformat = piargs.datetimeformat
    if piargs.hashblocksize is not None:
        hashblocksize = int(piargs.hashblocksize)
    if piargs.hashtype is not None:
        hashertype = piargs.hashtype
    
    
    # main program
    forcedir(archivedir1)
    forcedir(archivedir2)
    infolder = os.path.abspath(piargs.folderin)
    if not os.path.exists(infolder):
        print("Folder not found!")
        exit(1)
    if os.path.isdir(archivedir2 + "/" + os.path.basename(infolder)):
        print("Folder exists in destination!")
        exit(1)
    folder_worker(infolder)
    shutil.move(infolder, archivedir2 + "/" + os.path.basename(infolder))
    exit(0)
    
