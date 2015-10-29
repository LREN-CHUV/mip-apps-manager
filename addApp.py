#!/usr/bin/env python

import argparse, shutil, os, sys
from fnmatch import fnmatch


MAX_TITLE_LEN = 5
MAX_SUBTITLE_LEN = 10


def getArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('app', help='Application identifier (used by the app developer)')
	parser.add_argument('title', help='Tile title (max '+str(MAX_TITLE_LEN)+' characters)')
	parser.add_argument('subTitle', help='Tile sub-title (max '+str(MAX_SUBTITLE_LEN)+' characters)')
	parser.add_argument('appDir', help='Directory containing the new application (<path>/app/)')
	parser.add_argument('mipDir', help='Directory containing the mip application (<path>/app/)')
	return parser.parse_args()


def checkArgs(args):
	if len(args.title) > MAX_TITLE_LEN:
		print 'Error in main : The title must not be longer than '+str(MAX_TITLE_LEN)+' characters  ! '
		sys.exit(1)
	if len(args.subTitle) > MAX_SUBTITLE_LEN:
		print 'Error in main : The sub-title must not be longer than '+str(MAX_SUBTITLE_LEN)+' characters ! '
		sys.exit(1)
	if not os.path.isdir(args.appDir):
		print 'Error in main : '+args.appDir+' is not a directory  ! '
		sys.exit(1)
	if not os.path.isdir(args.mipDir):
		print 'Error in main : '+args.mipDir+' is not a directory  ! '
		sys.exit(1)
	if not os.path.isdir(os.path.join(args.appDir, 'scripts/app/', args.app)):
		print 'Error in main : The app project '+args.app+' do not seem to exist ! '
		print 'Check that you entered the right pseudonym and the right applcation directory ! '
		sys.exit(1)
	if not os.path.isfile(os.path.join(args.mipDir, 'scripts/app/app.js')):
		print 'Error in main : '+args.mipDir+' is not a valid MIP folder ! '
		print 'The path should be something like <path>/app/ ! '
		sys.exit(1)


def copyFolderRec(src, dst):
	try:
		shutil.copytree(src, dst)	
	except OSError:
		print 'Error in copyFolderRec : Cannot copy recursively folder '+src+' to folder '+dst+' ! '
		sys.exit(1)


def writeFile(fileName, content):
	try:
		f = open(fileName, 'w')
		f.write(content)
		f.close()
	except IOError:
		print 'Error in writeFile : Cannot write in '+fileName+' file ! '
		sys.exit(1)


def findAndPrepend(fileName, pattern, incl):
	try:
		content = ''
		f = open(fileName, 'r')
		for line in f:
			if pattern in line:
				content += incl
			content += line
		f.close()
		writeFile(fileName, content)
	except IOError:
		print 'Error in findAndPrepend : Cannot read the file '+fileName+' ! '
		sys.exit(1)


def findAndAppend(fileName, pattern, incl):
	try:
		content = ''
		f = open(fileName, 'r')
		for line in f:
			content += line
			if pattern in line:
				content += incl
		f.close()
		writeFile(fileName, content)
	except IOError:
		print 'Error in findAndAppend : Cannot read the file '+fileName+' ! '
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


def main():
	# Get arguments
	args = getArgs()
	args.app = args.app.lower()
	checkArgs(args)

	# Copy application folder
	src = os.path.join(args.appDir, 'scripts/app/', args.app)
	dst = os.path.join(args.mipDir, 'scripts/app/', args.app)
	copyFolderRec(src, dst)

	# Add module in `app.js`
	path = os.path.join(args.mipDir, 'scripts/app/app.js')
	if fileContains(path, '\'chuvApp.'+args.app+'\''):
		print 'The module '+'\'chuvApp.'+args.app+'\'seems to already exist in the `app.js` file ! '
	else:
		findAndAppend(path, '//ui modules', '    \'chuvApp.'+args.app+'\',\n')

	# Add module and controller in main `index.html`
	path = os.path.join(args.mipDir, 'index.html')
	inclStr = '\n<!-- JS inclusions for external app "'+args.app+'" -->\n'
	inclStr += '<script src="scripts/app/'+args.app+'/'+args.app+'.module.js"></script>\n'
	inclStr += '<script src="scripts/app/'+args.app+'/'+args.app+'.controller.js"></script>\n'
	if fileContains(path, inclStr):
		print 'The Javascript inclusions for this app seem to already exist in the `'+path+'` file ! '
	else:
		findAndPrepend(path, '</body>', inclStr)

	# Count existing tiles
	path = os.path.join(args.mipDir, 'scripts/app/hbpapps/hbpapps.html')
	nbTiles = 1  # We count the new tile too
	try:
		f = open(path, 'r')
		for line in f:
			if 'class="tile-body"' in line:
				nbTiles += 1
		f.close
	except IOError:
		print 'main : Cannot read the file '+path+' ! '

	# Add tile in `hbpapps.html`
	if fileContains(path,'tile-'+args.app):
		print 'The tile for this app seems to already exist in the `hbpapps.html` file ! '
	else:
		tileDiv = '''        <div class="col-md-3">
            <div class="info-tile tile-'''+args.app+'''">
                <div class="tile-heading"><span>&nbsp;</span></div>
                <div class="tile-body"><span>&nbsp;</span></div>
                <a href="http://localhost:9002/#/hbpapps/'''+args.app+'''" class="tile-title">
                    <big>'''+args.title+'''</big>
                    <span>'''+args.subTitle+'''</span>
                </a>
            </div>
        </div>
'''
		
		try:
			f = open(path, 'r')
			hasFoundPattern = False
			content = ''
			divCount = 0
			for line in f:
				if '<div class="row">' in line:
					hasFoundPattern = True
				if hasFoundPattern:
					if '<div' in line:
						divCount += 1
					if '</div' in line:
						divCount -= 1
				if hasFoundPattern and divCount == 0:
					content += tileDiv
				content += line
			f.close()
			writeFile(path, content)
		except IOError:
			print 'main : Cannot read the file '+path+' ! '

	# Add CSS div
	path = os.path.join(args.mipDir, 'styles/less/virtua/dashboard.less')
	if fileContains(path,'tile-'+args.app):
		print 'The tile for this app seems to already exist in the `dashboard.less` file ! '
	else:
		cssCode = '  &.tile-'+args.app+' {\n'
		if (nbTiles+3) % 4 == 0:
			cssCode += '    background-color: rgba(222, 147, 109, 0.25);\n'  # orange
		elif (nbTiles+2) % 4 == 0:
			cssCode += '    background-color: rgba(59, 139, 144, 0.25);\n'  # blue
		elif (nbTiles+1) % 4 == 0:
			cssCode += '    background-color: rgba(158, 158, 158, 0.251);\n'  # gray
		elif nbTiles % 4 == 0:
			cssCode += '    background-color: rgba(45, 77, 79, 0.251);\n'  # indigo

		cssCode += '    background-image: url("../../scripts/app/'+args.app+'/images/logo.png");\n'
		cssCode += '''
    background-size: 80px 60px;
    background-repeat: no-repeat;

    .tile-icon {
      left: -70px;
      bottom: -80px;

      i {
        color: #999999 !important;
      }
    }

    .tile-title {
      font-size: 28px;
      font-family: 'EB Garamond', serif;
      color: #FFF;
      padding-top: 45px;
      padding-left: 75px;
      position: absolute;
      z-index: 10;
      top: 0;
      left: 0;
      letter-spacing: 0.05em;
      width: 100%;

      big {
        font-size: 50px;
        font-family: 'Open Sans Condensed', sans-serif;
        font-weight: 700;
        display: block;
        letter-spacing: 0;
        line-height: 25px;
      }

      .icon {
        display: block;
        position: absolute;
        right: 10px;
        bottom: 0px;
        height: 40px;
        width: 40px;
        line-height: 36px;
        background: #FFF;
        border-radius: 50%;
        padding: 0 12px;
        font-size: 30px;
        font-weight: 700;
        transition: all 0.3s ease;
        color: #ef3b4a;

        i {
          margin-left: 4px;
        }
      }

      &:hover {
        .icon { 
          opacity: 0.6;
        }
      }
    }
  }
'''
		findAndPrepend(path, '.tile-heading', cssCode)


if __name__ == '__main__':
	main()