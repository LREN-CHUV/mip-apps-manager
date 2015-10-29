#!/usr/bin/env python

import argparse, shutil, os, sys


def getArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('app', help='Application identifier (used by the app developer)')
	parser.add_argument('mipDir', help='Directory containing the mip application (<path>/app/)')
	return parser.parse_args()


def checkArgs(args):
	if not os.path.isdir(args.mipDir):
		print 'Error in main : '+args.mipDir+' is not a directory  ! '
		sys.exit(1)
	if not os.path.isdir(os.path.join(args.mipDir, 'scripts/app/', args.app)):
		print 'Error in main : The app project '+args.app+' do not seem to exist ! '
		print 'Check that you entered the right pseudonym and the right applcation directory ! '
		sys.exit(1)


def writeFile(fileName, content):
	try:
		f = open(fileName, 'w')
		f.write(content)
		f.close()
	except IOError:
		print 'Error in writeFile : Cannot write in '+fileName+' file ! '
		sys.exit(1)


def findAndRemove(fileName, pattern):
	try:
		content = ''
		f = open(fileName, 'r')
		for line in f:
			if pattern not in line:
				content += line
		f.close()
		writeFile(fileName, content)
	except IOError:
		print 'Error in findAndRemove : Cannot read the file '+fileName+' ! '
		sys.exit(1)


def fileContains(fileName, pattern):
	try:
		f = open(fileName, 'r')
		for line in f:
			if pattern in line:
				f.close()
				return True
		f.close()
		return False
	except IOError:
		print 'Error in fileContains : Cannot read the file '+fileName+' ! '
		sys.exit(1)


def findTagLimits(fileName, pattern, del1, del2):
	try:
		f = open(fileName, 'r')
		hasFoundPattern = False
		startLine = 0
		stopLine = 0
		divCount = 0
		lineNum = 0
		for line in f:
			lineNum += 1
			if pattern in line:
				hasFoundPattern = True
				startLine = lineNum
			elif hasFoundPattern and divCount == 0:
				stopLine = lineNum - 1
				hasFoundPattern = False
			if hasFoundPattern:
				if del1 in line:
					divCount += 1
				if del2 in line:
					divCount -= 1
		f.close()
		return (startLine, stopLine)
	except IOError:
		print 'Error in findTagLimits : Cannot read the file '+fileName+' ! '
		sys.exit(1)


def removeBetween(fileName, start, stop):
	try:
		content = ''
		f = open(fileName, 'r')
		lineNum = 0
		for line in f:
			lineNum += 1
			if lineNum < start or lineNum > stop:
				content += line
		f.close()
		writeFile(fileName, content)
	except IOError:
		print 'Error in removeBetween : Cannot read the file '+fileName+' ! '
		sys.exit(1)


def strContainsListElement(string, strList):
	for l in strList:
		if l in string:
			return True
	return False


def main():
	# Get arguments
	args = getArgs()
	args.app = args.app.lower()
	checkArgs(args)

	# Remove application folder
	appFolder = os.path.join(args.mipDir, 'scripts/app/', args.app)
	shutil.rmtree(appFolder)

	# Remove module from `app.js`
	path = os.path.join(args.mipDir, 'scripts/app/app.js')
	if fileContains(path, '\'chuvApp.'+args.app+'\''):
		findAndRemove(path, '    \'chuvApp.'+args.app+'\',\n')
	else:
		print 'The module '+'\'chuvApp.'+args.app+'\'seems to have already been deleted ! '

	# Remove module and controller inclusions from main `index.html`
	path = os.path.join(args.mipDir, 'index.html')
	linesToRm = []
	linesToRm.append('<!-- JS inclusions for external app "'+args.app+'" -->')
	linesToRm.append('<script src="scripts/app/'+args.app+'/'+args.app+'.module.js"></script>')
	linesToRm.append('<script src="scripts/app/'+args.app+'/'+args.app+'.controller.js"></script>')
	for line in linesToRm:
		findAndRemove(path, line)

	# Remove existing tiles from html
	path = os.path.join(args.mipDir, 'scripts/app/hbpapps/hbpapps.html')
	if fileContains(path,'tile-'+args.app):
			limits = findTagLimits(path, '<div class="info-tile tile-'+args.app+'">', '<div', '</div')
			removeBetween(path, limits[0]-1, limits[1]+1)
	else:
		print 'The tile for this app seems to have already been removed from the `hbpapps.html` file ! '

	# Remove tile from less file
	path = os.path.join(args.mipDir, 'styles/less/virtua/dashboard.less')
	if fileContains(path,'tile-'+args.app):
			limits = findTagLimits(path, '&.tile-'+args.app+' {', '{', '}')
			removeBetween(path, limits[0], limits[1])
	else:
		print 'The tile for this app seems to have already been removed from the `hbpapps.html` file ! '

	# Update tiles colors
	try:
		exclList = ['&.tile-orange','&.tile-blue', '&.tile-gray', '&.tile-edit']
		content = ''
		needChange = False
		cssCode = ''
		f = open(path, 'r')
		tileNum = 0 
		for line in f:
			if needChange:
				content += cssCode
				needChange = False
			else:
				content += line
				if '&.tile-' in line and not strContainsListElement(line, exclList):
					tileNum += 1
					needChange = True
					if (tileNum+3) % 4 == 0:
						cssCode = '    background-color: rgba(222, 147, 109, 0.25);\n'  # orange
					elif (tileNum+2) % 4 == 0:
						cssCode = '    background-color: rgba(59, 139, 144, 0.25);\n'  # blue
					elif (tileNum+1) % 4 == 0:
						cssCode = '    background-color: rgba(158, 158, 158, 0.251);\n'  # gray
					elif tileNum % 4 == 0:
						cssCode = '    background-color: rgba(45, 77, 79, 0.251);\n'  # indigo
		f.close()
		writeFile(path, content)
	except IOError:
		print 'Error in main : Cannot read the file '+path+' ! '
		sys.exit(1)


if __name__ == '__main__':
	main()
