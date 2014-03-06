import xml.etree.ElementTree as ET
import errno
import os
import urllib
import sys
import shutil

tree = ET.parse('dependencies.xml')
root = tree.getroot()

config = {}
packages = {}
args = {'update' : True, 'overwrite' : True}

def die(msg):
	print msg
	sys.exit(1)

def mkdir(directory, need_overwrite=True):
	if os.path.exists(directory):
		if need_overwrite and (not (args['overwrite'])):
			die("Directory " + directory + " already exists.")
	else:
		try:
			os.makedirs(directory)
		except:
			die("Couldn't make directory: " + directory)

def get_file_name(dict, prefix=""):
	if 'dlname' in dict:
		return prefix+dict['dlname']
	else:
		return prefix+dict['uri'].rpartition('/')[2].rpartition('\\')[2]

def temp_file_name(filedir, dict, prefix=""):
	return os.path.join(filedir, get_file_name(dict, prefix))

#################

for param in root.find('setup').findall('param'):
	config.update({param.attrib['name'] : param.text })


for package in root.find('packages').findall('package'):
	dict = {}
	name = package.attrib['name']

	for package_conf in package.getchildren():
		dict.update( { package_conf.tag : package_conf.text } )
	
	packages.update( { name : dict } )



tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), config['tempdir'])
mkdir(tmp_dir, False)

for name, dict in packages.iteritems():
	filename = temp_file_name(tmp_dir, dict)
	sys.stdout.write("Downloading '%s' ... "%(dict['uri']))
	sys.stdout.flush()
	response = urllib.urlretrieve(dict['uri'], filename)

	print "Done!"

for name, dict in packages.iteritems():
	src_file = temp_file_name(tmp_dir, dict)
	dst_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), dict['moveto'], get_file_name(dict))
	shutil.copy2(src_file, dst_file);



