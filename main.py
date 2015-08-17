#! /usr/bin/env python3
# Configuration happens here
icontheme='gnome'
# End of Configuration
import os
import sys
import glob
import http.server
import socketserver
import logging
import cgi
from urllib.parse import urlparse
import xdg.DesktopEntry as entryhandler
import xdg.IconTheme as ic
workingdirectory=os.getcwd()
i = ic.IconTheme()
i.parse('/usr/share/icons/gnome/index.theme')
if not os.path.exists('system'):
	os.symlink("/", "system")
apps = []
def init():
	try:
		os.remove('index.html')
	except:
		print("Old Menu file could not be removed")
	menu = open('index.html', 'a')
	menu.write("<head><link rel='stylesheet' type='text/css' href='style.css'></head><body>")
	os.chdir('/usr/share/applications')
	id=0
	for file in glob.glob("*.desktop"):
		entry=entryhandler.DesktopEntry(filename=file)
		apps.append({'Name': entry.getName(), 'Icon':'system' + str(ic.getIconPath(entry.getIcon())), 'Exec':'xiwi '+entry.getExec(), 'id':id})				
		id=id+1
	for app in apps:
		menu.write("<div class='iconbox'><a href='index.html?id=" + str(app['id']) + "'><img class='icon' height='48' width='48' src='" + app['Icon'] + "'><br>" +app['Name'] + '</a></div>')
	menu.write('</body>')
	menu.close()

def serve():
	os.chdir(workingdirectory)
	PORT = 8000

	class ServerHandler(http.server.SimpleHTTPRequestHandler):

		def do_GET(self):
			parsed_path = urlparse(self.path)
			try:
				params = dict([p.split('=') for p in parsed_path[4].split('&')])
			except:
				params = {}
			if params:
				for app in apps:
					if str(app['id']) == str(params['id']).strip("/"):
						print(app['Name'])
						os.system(app['Exec']+'&')
			http.server.SimpleHTTPRequestHandler.do_GET(self)

		def do_POST(self):
			logging.error(self.headers)
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
				     'CONTENT_TYPE':self.headers['Content-Type'],
				     })
			for item in form.list:
				logging.error(item)
			http.server.SimpleHTTPRequestHandler.do_GET(self)
	Handler = ServerHandler
	httpd = socketserver.TCPServer(("", PORT), Handler)
	print("serving at port", PORT)
	httpd.serve_forever()

init()
serve()
