import os
import sys
import ftplib
import pickle
from PIL import Image

def write_html(htmlname, htmlstr, folder):
	#parse folder
	fs = folder.split('/')
	print fs
	
	f_html = open(htmlname,'w')
	f_html.write(htmlstr)
	f_html.close()

	print 'uploading %s in %s...' % (htmlname, folder)

	session = ftplib.FTP('ftp.paladinofstorms.net',ftpacc,ftppass)
	
	for fold in fs:
		try: 
			session.mkd('./%s' % fold)
		except:
			print('folder %s already exists :)' % fold)
		session.cwd('./%s' % fold)
	
	f_html = open(htmlname,'rb')
	session.storbinary('STOR %s' % htmlname, f_html)
	f_html.close()
	session.quit()

def upload_image(imname, folder, exists):
	fs = folder.split('/')
	print fs
	
	print 'resizing %s...' % imname
	
	im = Image.open(imname)
	width, height = im.size
	newsize = (width/2, height/2)
	imresize = im.resize(newsize)
	
	if exists == False:
		try:
			os.mkdir('./web')
			print 'web directory created'
		except:
			print 'web directory already exists!'
	else:
		pass #we know the folder exists cause we created it in this run of the program
	
	imresize.save('./web/%s' % imname)
	
	print 'uploading %s...' % imname
	
	session = ftplib.FTP('ftp.paladinofstorms.net',ftpacc,ftppass)
	
	for fold in fs:
		if exists == False:
			try: 
				session.mkd('./%s' % fold)
			except:
				print('folder %s already exists :)' % fold)
		else:
			pass #we know the folders exist cause we created them in this run of the program
		session.cwd('./%s' % fold)
	
	f_im = open('./web/%s' % imname,'rb')
	session.storbinary('STOR %s' % imname, f_im)
	f_im.close()
	session.quit()

def pluralize(n):
	if n > 1:
		return 's'
	else:
		return ''

f = open('config.txt', 'r')
k = f.readlines()
f.close()

ftpacc = k[0].strip()
ftppass = k[1].strip()
base_img_dir = k[2].strip()

html = '<head>\n\t<link rel="stylesheet" href="ph.css" />\n</head>\n<body>\n\t<div class="title">kalassak\'s photography</div>\n'

f2p = input('name of file to process: ')

f = open('%s.txt' % f2p, 'r')
k = f.readlines()
f.close()

#construct a dictionary of all the months, projects, and images to process
with open('database.pkl', 'rb') as fd:
	d = pickle.load(fd)

new = [] #stores image file names for NEW images to upload
for line in k:
	s = line.strip().split(';')
	#month;project;image;description
	month = s[0]
	project = s[1]
	image = s[2]
	description = s[3]
	
	new_img = {'image': image, 'description': description}
	if month in d.keys():
		if project in d[month].keys():
			if new_img in d[month][project]:
				pass #skip, not new
			else:
				d[month][project].append(new_img)
				new.append(image)
		else:
			d[month][project] = []
			d[month][project].append(new_img)
			new.append(image)
	else:
		d[month] = {}
		d[month][project] = []
		d[month][project].append(new_img)
		new.append(image)
	
#begin processing...
#this might require making new folders and pages and stuff

for month in sorted(d.keys(), reverse=True):
	print 'processing %s...' % month
	
	#create month page
	html_month = '<head>\n\t<link rel="stylesheet" href="../ph.css" />\n</head>\n<body>\n\t<div class="title">%s</div>\n' % (month)
	
	n_month_imgs = 0
	for project in d[month].keys():
		print 'processing %s...' % project
		
		#create project page
		html_project = '<head>\n\t<link rel="stylesheet" href="../../ph.css" />\n</head>\n<body>\n\t<div class="title">%s</div>\n\t<table>\n' % (project)
		
		#navigate to project directory
		os.chdir('%s\\%s' % (base_img_dir, month))
		folders_exist = False
		
		n_project_imgs = 0
		for img in d[month][project]:
			n_month_imgs += 1
			n_project_imgs += 1
		
			#determine filename
			fname = '%s.JPG' % img['image'] #idk actually dynamically determine it or sth
			html_project += '\t<tr>\n\t\t<td class="image"><a href="%s"><img src="%s" width="100%%"/></a></td>\n\t\t<td class="description">%s</td>\n\t</tr>\n' % (fname, fname, img['description'])
			
			#upload image
			if img['image'] in new:
				upload_image(fname, '/%s/%s' % (month, project), folders_exist)
			
			folders_exist = True
			
		#add project to month page
		html_month += '\t<div class="folder"><a href="./%s">%s</a>  <span class="count">(%s image%s)</span></div>\n' % (project, project, n_month_imgs, pluralize(n_month_imgs))
		
		html_project += '\t</table>\n</body>'
		html_project += '\t<div class="cc"><a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="../../by-nc.png" height="40px" /></a></div>\n'
		write_html('default.html', html_project, '/%s/%s' % (month, project))
	html_month += '</body>'
	write_html('default.html', html_month, '/%s' % month)
	
	#add month to main page
	html += '\t<div class="folder"><a href="./%s">%s</a> <span class="count">(%s image%s)</span></div>\n' % (month, month, n_month_imgs, pluralize(n_month_imgs))
	
html += '\n\t<div class="cc"><a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="by-nc.png" height="40px" /></a></div>\n'
html += '</body>'
write_html('default.html', html, '')

os.chdir(sys.path[0])
with open('database.pkl', 'wb') as fd:
	pickle.dump(d, fd)

'''
			#session.cwd('/sat/%s/%s' % (sector, image_type))
			#determine how many files we have
			findr = []
			try:
				findr = session.nlst()
			except ftplib.error_perm as resp:
				if str(resp) == "550 No files found":
					print('no files in this dir')
				else:
					raise
'''