#! /usr/bin/env python

# WebHost.py
# defines:
#	WebHost:
#		cherrypy wrapper for hosting a "/static" folder
#		allows WebInterface objects to serve dynamic content
#		  alongside the "/static" folder
#	WebInterface:
#		"purely virtual" class for a dynamic web interface
#
# made by Joshua Huseman, jhuseman@nd.edu
# Created: 06/08/2016
# Updated: 06/13/2016
# Updated: 08/01/2017 - removed logging to screen
# Updated: 06/16/2018 - removed cherrypy dependency, instead using python built-in BaseHTTPServer

from datetime import datetime
import BaseHTTPServer
import mimetypes
import json
import os

WebServerNameAndVer = "WebHost/1.0.0"

def generate_redirect_page(dest):
	return """
		<!DOCTYPE html>
		<html>
			<head>
				<META http-equiv="refresh" content="0;URL={dest}">
				<title>WebHost Redirect</title>
			</head>
			<body>
				There is no information at this page.
				If you are not redirected to {dest} immediately, you can click <a href="{dest}">here</a>.
				<script>
					window.location = "{dest}";
					window.location.replace("{dest}");
					window.location.href = "{dest}";
				</script>
			</body>
		</html>
	""".format(dest=dest)

class WebHost(object):
	def __init__(self,port=80,host='0.0.0.0',log_function=None,staticdir="static",staticindex="index.html", error_404_page_func=None):
		self.port = port
		self.host = host
		self.dispatcher = WebDispatcher(host=self.host, port=self.port, log_function=log_function, staticdir=staticdir, staticindex=staticindex, error_404_page_func=error_404_page_func)

		self.resource_list = []
		self.docs = WebDocs(self)

	def start_service(self):
		# # output resource list (for debug)
		# print "All Resources:"
		# print self.resource_list
		self.dispatcher.start_service()
	
	def stop_service(self):
		self.dispatcher.stop_service()

	def get_dispatcher(self):
		return self.dispatcher

	def log_connection(self,interface,resource,action,method):
		log_entry = {
			"docstring":getattr(interface,action).__doc__,
			"function_name":getattr(interface,action).__name__,
			"resource":resource,
			"method":method,
		}
		self.resource_list.append(log_entry)

class WebDispatcher(object):
	class WebRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
		def send_header_as_code(self, status_code, url):
			"""send the header of the response with the given status code"""
			mime_url = url
			if mime_url[-1]=='/':
				mime_url = url+"index.html"
			mime_type = mimetypes.MimeTypes().guess_type(mime_url)[0]
			if mime_type is None:
				mime_type = "text/html"
			self.send_response(status_code)
			self.send_header("Content-type", mime_type)
			self.end_headers()
		
		def do_HEAD(self):
			"""Respond to a HEAD request."""
			self.send_header_as_code(200, self.path)
		
		def GENERAL_REQ_HANDLER(self,callback):
			"""Respond to a GET request."""
			body_len_str = self.headers.getheader('Content-Length')
			if body_len_str is None:
				body_len = 0
				body = None
			else:
				body_len = int(body_len_str)
				body = self.rfile.read(body_len)
			ret_data = callback(url=self.path, method=self.command, headers=self.headers, body=body)
			if ret_data is None:
				self.send_header_as_code(404, '404.html')
				self.wfile.write(self.get_404_page(url=self.path))
			else:
				self.do_HEAD()
				self.wfile.write(ret_data)
		
		def log_message(self, format, *args):
			if not self.log_string is None:
				self.log_string("%s - - [%s] %s" %
					(self.client_address[0],
					self.log_date_time_string(),
					format%args))
		
		def log_string(self, data):
			print(data)
		
		def get_404_page(self, url=""):
			return "<head><title>Error response</title></head>"+ \
			"<body><h1>Error response</h1><p>Error code 404.<p>Message: Unsupported method ('POST')."+ \
			"<p>Error code explanation: 404 = Nothing matches the given URI.</body>"
	
	def __init__(self, host="0.0.0.0", port=80, log_function=None, staticdir="static", staticindex="index.html", error_404_page_func=None):
		self.host = host
		self.port = port
		self.log_function = log_function
		self.staticdir = staticdir
		self.staticindex = staticindex
		self.error_404_page_func = error_404_page_func
		self.request_handler_class = self.WebRequestHandler
		self.resource_dict = {}
		self.set_default_handler("GET", self.default_GET_handler)
		setattr(self.request_handler_class, 'log_string', classmethod(self.log_string))
		setattr(self.request_handler_class, 'get_404_page', classmethod(self.get_404_page))
		self.httpd = BaseHTTPServer.HTTPServer((self.host, self.port), self.request_handler_class)
	
	def split_url_params(self, url):
		split_url = url.split('/:')
		prefix = split_url[0]
		param_count = len(split_url)-1
		return (prefix, param_count)
	
	def get_possible_split_url_params(self, url):
		ret = []
		split_url = url.split('/')
		remaining = split_url
		removed = []
		while len(remaining)>0:
			prefix = '/'.join(remaining)
			param_count = len(split_url)-len(remaining)
			params = removed[:param_count]
			if (prefix+'/')==url:
				ret.append((prefix, param_count, params))
				param_count = param_count-1
				params = removed[:param_count]
			ret.append((prefix, param_count, params))
			removed = [remaining[-1]] + removed
			remaining = remaining[:-1]
		return ret

	def connect(self, resource, callback, method):
		if method not in self.resource_dict:
			self.initialize_request_handler(method)
		(url_prefix, url_param_count) = self.split_url_params(resource)
		if url_prefix not in self.resource_dict[method]['resources']:
			self.resource_dict[method]['resources'][url_prefix] = {}
		self.resource_dict[method]['resources'][url_prefix][url_param_count] = callback
	
	def initialize_request_handler(self, method):
		def req_method_handler(request_handler_instance):
			self.request_handler_class.GENERAL_REQ_HANDLER(request_handler_instance, self.request_handler)
		if method not in self.resource_dict:
			self.resource_dict[method] = {'default':None,'resources':{}}
			do_command = 'do_'+method
			setattr(self.request_handler_class, do_command, req_method_handler)

	def request_handler(self, url=None, method=None, headers=None, body=None):
		if method in self.resource_dict:
			url_no_browseparams = url.split('?')[0] # remove and ignore anything after a question mark
			for (url_prefix, url_param_count, params) in self.get_possible_split_url_params(url_no_browseparams):
				if url_prefix in self.resource_dict[method]['resources']:
					if url_param_count in self.resource_dict[method]['resources'][url_prefix]:
						return self.resource_dict[method]['resources'][url_prefix][url_param_count](*params)
			if not self.resource_dict[method]['default'] is None:
				return self.resource_dict[method]['default'](url=url_no_browseparams, headers=headers, body=body)
		return None
	
	def set_default_handler(self, method, handler):
		if not method in self.resource_dict:
			self.initialize_request_handler(method)
		self.resource_dict[method]['default'] = handler
	
	def default_GET_handler(self, url=None, headers=None, body=None):
		url_relative = url[1:]
		index_relative = os.path.join(url_relative,self.staticindex)
		url_relative_static = os.path.join(self.staticdir,url_relative)
		index_relative_static = os.path.join(self.staticdir,index_relative)
		check_paths = [index_relative, url_relative, index_relative_static, url_relative_static]
		for path in check_paths:
			if os.path.exists(path):
				if os.path.isfile(path):
					with open(path) as fp:
						data = fp.read()
					return data
				else:
					return self.get_dir_page(path)
		return None
	
	def log_string(self, request_handler_instance, data):
		if not self.log_function is None:
			self.log_function(data)

	def start_service(self):
		self.service_running = True
		while self.service_running:
			self.httpd.handle_request()
		self.httpd.server_close()
		self.service_running = False
	
	def stop_service(self):
		self.service_running = False
	
	def get_address_string(self):
		return "{server} Server at {host} Port {port}".format(server=WebServerNameAndVer, host=self.host, port=self.port)
	
	def get_dir_page(self, path):
		if path[-1]!='/':
			return generate_redirect_page('/'+path+'/')
		data = ('<html><head><title>Index of {path}</title></head><body><h1>Index of {path}</h1><table>'+\
			'<tr><th valign="top"></th><th>Name</th><th>Last modified</th><th>Size</th></tr>'+\
			'<tr><th colspan="5"><hr></th></tr>'+\
			'<tr><td valign="top"></td><td><a href="..">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - </td></tr>').format(
				path="/"+path
			)
		for filename in os.listdir(path):
			fullpath = os.path.join(path,filename)
			if os.path.isdir(fullpath):
				if filename[-1]!='/':
					filename = filename + '/'
			filestat = os.stat(fullpath)
			size = filestat.st_size
			size_str = str(size)
			if size>(1<<10):
				size_str = str(size/(1<<10))+"K"
			if size>(1<<20):
				size_str = str(size/(1<<20))+"M"
			if size>(1<<30):
				size_str = str(size/(1<<30))+"G"
			if size>(1<<40):
				size_str = str(size/(1<<40))+"T"
			data = data + '<tr><td valign="top"></td><td><a href="{filename}">{filename}</a></td><td align="right">{lastmodified}</td><td align="right">{size}</td></tr>'.format(
				filename=filename,
				lastmodified=datetime.fromtimestamp(filestat.st_mtime),
				size=size_str
			)
		data = data + (('<tr><th colspan="5"><hr></th></tr></table>'+\
			'<address>{address}</address>'+\
			'</body></html>').format(
				address=self.get_address_string()
			))
		return data
	
	def get_404_page(self, request_handler_instance, url=""):
		if not self.error_404_page_func is None:
			return self.error_404_page_func(url=url)
		return ("<html><head><title>404 Not Found</title></head>"+\
		"<body><h1>Not Found</h1><p>The requested URL {url} was not found on this server.</p><hr>"+\
		"<address>{address}</address>"+\
		"</body></html>").format(url=url, address=self.get_address_string())
		

class WebInterface(object):
	"""
	Allows for easily defining web interfaces for the server.

	Expects the variable "self.host" to be set to a WebHost
	object before calling "connect()".

	See implementation of __init__ class for an example initialization.
	"""

	def __init__(self):
		# starts a WebHost on port 80 that
		self.host = WebHost(80)
		self.host.start_service()

		# # add lines like the following:
		# self.connect('/test/:id','GET_ID','GET')
		# self.connect('/test/:id',self.GET_ID,'GET')
		# # to call member function GET_ID() with the argument after "/test/" when a GET request
		# # is received for "/test/<any text here>"
	
	def connect(self, resource, action, method):
		callback = getattr(self, action)
		self.connect_callback(resource, callback, method)
	
	def connect_callback(self,resource,callback,method):
		"""
		connects a specified callback (function) in this object
		to the specified resource (URL)
		and http method (GET/PUT/POST/DELETE)
		"""
		self.dispatcher = self.host.get_dispatcher()
		self.dispatcher.connect(resource, callback, method)
		# log this connection on the host
		self.host.log_connection(self,resource,callback.__name__,method)

class WebDocs(WebInterface):
	def __init__(self,host):
		self.host = host
		# self.connect('/','ROOT_REDIRECT','GET')
		self.connect('/docs/','GET_DOCS','GET')
		self.connect('/docs/json/','GET_DOCS_JSON','GET')

	def ROOT_REDIRECT(self):
		"""redirects to /static/ directory"""
		return generate_redirect_page("/static/")

	def GET_DOCS(self):
		"""return the documentation page in HTML format"""
		resources = ""
		for resource in self.host.resource_list:
			resource_html = """
				<tr>
					<td><a href="{resource}">{resource}</a></td>
					<td>{method}</td>
					<td>{function_name}</td>
					<td>{docstring}</td>
				</tr>
			""".format(
				resource = resource["resource"],
				method = resource["method"],
				function_name = resource["function_name"],
				docstring = resource["docstring"].replace("\n","<br />"),
			)
			resources = resources+resource_html
		return """
			<!DOCTYPE html>
			<html>
				<head>
					<title>WebHost Documentation</title>
				</head>
				<body>
					<table border="1">
						<tr>
							<th>Resource</th>
							<th>Method</th>
							<th>Function Name</th>
							<th>Docstring</th>
						</tr>
						{resources}
					</table>
				</body>
			</html>
		""".format(resources=resources)

	def GET_DOCS_JSON(self):
		"""return the documentation page in JSON format"""
		return json.dumps(self.host.resource_list)

if __name__ == '__main__':
	"""
	serves only a static folder in the local 'static' directory
	"""
	host = WebHost(80)
	host.start_service()
