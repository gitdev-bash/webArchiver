#!/bin/python3
import os
import hashlib
import csv
import datetime
import argparse
import shutil
import configparser
#set vars
archivedir1=os.path.expanduser("~") + "/archiver/files/"
archivedir2=os.path.expanduser("~") + "/archiver/archive/"
csv1=archivedir1 + "csv1"
csv2=archivedir1 + "csv2"
datetimeformat="%y.%m.%d-%H:%M"
datetimes=datetime.datetime.now().strftime(datetimeformat)
hashblocksize=65536
hashertype="sha256"
configfile=os.path.expanduser("~") + "/archiver/archiver.conf"
#readtags
piparser = argparse.ArgumentParser()
piparser.add_argument("-fi", "--folderin", help="Input folder")
piparser.add_argument("-fs", "--foldersave", help="Archive save directory location")
piparser.add_argument("-fa", "--folderarchive", help="Archive archiving directory location")
piparser.add_argument("-fl1", "--filelist1", help="Archive filelist1 location")
piparser.add_argument("-fl2", "--filelist2", help="Archive filelist2 location")
piparser.add_argument("-dtf", "--datetimeformat", help="Set datetime format")
piparser.add_argument("-hb", "--hashblocksize", help="Set hash blocksize")
piparser.add_argument("-ht", "--hashtype", help="Set hash type to one of:'blake2s', 'sha384', 'sha512', 'sha3_256', 'sha256', 'md5', 'sha3_512', 'sha3_224', 'shake_128', 'shake_256', 'sha1', 'blake2b', 'sha224', 'sha3_384'")
piparser.add_argument("-c", "--configfile", help="Set configfile in init format (in [DEFAULT])")
piargs = piparser.parse_args()
if piargs.configfile is not None:
	configfile=piargs.configfile
#read config file
config = configparser.ConfigParser()
if os.path.isfile(configfile):	
	config.read(configfile)
	if "DEFAULT" in config:
		if "folderarchive" in config["DEFAULT"]:
			archivedir2=config["DEFAULT"]["folderarchive"]
		if "filelist1" in config["DEFAULT"]:
			csv1=config["DEFAULT"]["filelist1"]
		if "filelist2" in config["DEFAULT"]:
			csv2=config["DEFAULT"]["filelist2"]
		if "datetimeformat" in config["DEFAULT"]:
			datetimeformat=config["DEFAULT"]["datetimeformat"]
		if "hashblocksize" in config["DEFAULT"]:
			hashblocksize=config["DEFAULT"]["hashblocksize"]
		if "hashtype" in config["DEFAULT"]:
			hashertype=config["DEFAULT"]["hashtype"]
		if "foldersave" in config["DEFAULT"]:
			archivedir1=config["DEFAULT"]["foldersave"]
##
if piargs.folderin is None:
	print("Give input folder")
	exit(1)
if piargs.foldersave is not None:
	archivedir1=piargs.foldersave
if piargs.folderarchive is not None:
	archivedir2=piargs.folderarchive
if piargs.filelist1 is not None:
	csv1=piargs.filelist1
if piargs.filelist2 is not None:
	csv2=piargs.filelist2
if piargs.datetimeformat is not None:
	datetimeformat=piargs.datetimeformat
if piargs.hashblocksize is not None:
	hashblocksize=piargs.hashblocksize
if piargs.hashtype is not None:
	hashertype=piargs.hashtype
#define functions
def file_len(fname):
	if False == os.path.isfile(fname):
		return(0)
	with open(fname) as f:
		count=0
		for i, l in enumerate(f):
			count=i+1
	return(count)
def forcedir(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)
def hasher(filein, hname, blocksize):
	if hname="blake2s":
		htype=hashlib.blake2s
	elif hname="sha384":
		htype=hashlib.sha384
	elif hname="sha512":
		htype=hashlib.sha512
	elif hname="sha3_256":
		htype=hashlib.sha3_256
	elif hname="sha256":
		htype=hashlib.sha256
	elif hname="md5":
		htype=hashlib.md5
	elif hname="sha3_512":
		htype=hashlib.sha3_512
	elif hname="sha3_224":
		htype=hashlib.sha3_224
	elif hname="shake_128":
		htype=hashlib.shake_128
	elif hname="shake_256":
		htype=hashlib.shake_256
	elif hname="sha1":
		htype=hashlib.sha1
	elif hname="blake2b":
		htype=hashlib.blake2b
	elif hname="sha224":
		htype=hashlib.sha224
	elif hname="sha3_384":
		htype=hashlib.sha3_384
	else:
		print("wrong hash type")
		exit(1)
	with open(filein, 'rb') as fi: 
		while True: 
			data = fi.read(blocksize) 
			if not data:
				break
			htype.update(data) 
	return(htype.hexdigest())
def csver(filein, operation, data):
	if operation=="find":
		if False == os.path.isfile(filein):
			return("False")
		with open(filein, 'rt') as fi:
			reader = csv.reader(fi, delimiter=',')
			for row in reader:
				hashout=row[1] #location of hash
				if hashout == data:
					return(row[0])
			return("False")
	elif operation=="append":
		if False == os.path.isfile(filein):
			pass
		with open(filein,'a') as fd:
			writer = csv.writer(fd)
			writer.writerow(data)
def wfile(filedef, filerel):
	hashin=hasher(filedef, hashertype, hashblocksize)
	csvid=csver(csv1, "find",hashin)
	if csvid=="False":
		csvid=file_len(csv1)+1
		csver(csv1, "append", [csvid, hashin])
		os.replace(filedef, archivedir1 + "/" + str(csvid))
	else:
		os.remove(filedef)
	csver(csv2, "append", [datetimes, csvid, filerel])
	os.symlink(archivedir1 + "/" + str(csvid), filedef)
def wfolder(directory):
	for ff in os.listdir(directory):
		ffdef=directory + "/" + ff
		if os.path.isfile(ffdef):
			wfile(ffdef, ff)
		else:
			wfolder(ffdef)
#main program
forcedir(archivedir1);forcedir(archivedir2)
infolder=os.path.abspath(piargs.folderin)
if not os.path.exists(infolder):
	print("Folder not found!")
	exit(1)
wfolder(infolder)
shutil.move(infolder, archivedir2 + "/")
exit(0)
