###########################################################################
## \file AppBuild.py
## \brief
## \author
###########################################################################
## \package AppBuild
## \brief
###########################################################################
import xml.etree.ElementTree as ET
import os
import urllib2
import sys
import shutil
import zipfile
import distutils.core

tree = ET.parse('dependencies.xml')
root = tree.getroot()

config = {}
packages = {}
args = {'update' : True, 'overwrite' : True}

###########################################################################
## \brief
## \param
## \return
## \author
###########################################################################
def die(msg):
	print msg
	sys.exit(1)

###########################################################################
## \brief
## \param
## \param
## \return
## \author
###########################################################################
def mkdir(directory, need_overwrite=True):
	if os.path.exists(directory):
		if need_overwrite and (not (args['overwrite'])):
			die("Directory " + directory + " already exists.")
	else:
		try:
			os.makedirs(directory)
		except:
			die("Couldn't make directory: " + directory)

###########################################################################
## \brief
## \param
## \param
## \return
## \author
###########################################################################
def get_file_name(dict, prefix=""):
	if 'dlname' in dict:
		return prefix+dict['dlname']
	else:
		return prefix+dict['uri'].rpartition('/')[2].rpartition('\\')[2]

###########################################################################
## \brief
## \param
## \param
## \return
## \author
###########################################################################
def temp_file_name(filedir, dict, prefix=""):
	return os.path.join(filedir, get_file_name(dict, prefix))

###########################################################################
## \brief
## \param
## \param
## \return
## \author
###########################################################################
def node_text(node, child):
	sub_node = node.find(child)
	
	if sub_node is not None:
		return sub_node.text
	else:
		return None

###########################################################################
###########################################################################
##############################   MAIN BODY   ##############################
###########################################################################
###########################################################################


for param in root.find('setup').findall('param'):
	config.update({param.attrib['name'] : param.text })


for package in root.find('packages').findall('package'):
	dict = {}
	name = package.attrib['name']

	for package_conf in package.getchildren():
		if package_conf.tag != 'move' and package_conf.tag != 'mkdir':
			dict.update( { package_conf.tag : package_conf.text } )

	moves = []
	for fmove in package.findall('move'):
		movdict = {}
		
		inner_source = fmove.find('innersource')
		isdir = False
		if inner_source is not None:
			if inner_source.text is None:
				inner_source_text = ""
			else:
				inner_source_text = inner_source.text
			movdict.update( { 'from' : inner_source_text } )
			if 'dir' in inner_source.attrib:
				if int(inner_source.attrib['dir']):
					isdir = True
		movdict.update( { 'isdir' 	: isdir } )

		movdict.update( { 'to' 		: node_text(fmove, 'destination') } )

		newdirs = []
		for newdir in fmove.findall('mkdir'):
			newdirs.append( { 'dirname' : newdir.text } )
		movdict.update( { 'mkdir' : newdirs } )

		moves.append(movdict)

	dict.update( { 'moves' : moves } )

	packages.update( { name : dict } )



tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), config['tempdir'])
mkdir(tmp_dir, False)

for name, dict in packages.iteritems():
	filedir = os.path.join(tmp_dir, name)
	mkdir(filedir)
	
	filename = temp_file_name(filedir, dict)
	sys.stdout.write("Downloading '%s' ... "%(dict['uri']))
	sys.stdout.flush()
	req = urllib2.Request(dict['uri'])
	rhandle = urllib2.urlopen(req)
	
	with open(filename, 'wb') as outfile:
		shutil.copyfileobj(rhandle, outfile)

	print "Done!"

for name, dict in packages.iteritems():
	dl_dir = os.path.join(tmp_dir, name)

	if int(dict['unzip']):
		zip_file = temp_file_name(dl_dir, dict)
		sys.stdout.write("unzipping " + name + " ... ")
		sys.stdout.flush()
		with zipfile.ZipFile(zip_file, 'r') as zip:
			zip.extractall(dl_dir)
		print "Done!"

	for fmove in dict['moves']:
		for newdir in fmove['mkdir']:
			mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), newdir['dirname']))
		
		if int(dict['unzip']) and fmove['from'] is not None:
			src_file = os.path.join(dl_dir, fmove['from'])
		else:
			src_file = temp_file_name(dl_dir, dict)

		dst_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), fmove['to'])
		if fmove['isdir']:
			distutils.dir_util.copy_tree(src_file, dst_file)
		else:
			shutil.copy2(src_file, dst_file);



