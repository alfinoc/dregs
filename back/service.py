from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from werkzeug.utils import redirect
from functools import partial
from math import pow
from os import listdir as ls
from os.path import join
from json import load
from codecs import open

from scope_css import consolidate
from combinations import subset

# Returns an integer rep. of the given 32-bit IP string xxx.xxx.xxx.xxx.
def ipToInt(ip):
   parts = map(int, ip.split('.'))  # Could reverse but who cares?
   powers = map(partial(pow, 2), range(0, 64, 8))
   return int(sum(map(lambda (x, y) : x * y, zip(parts, powers))))

# Returns the contents of the file with given name.
def contents(filename):
   with open(filename, 'r', 'utf-8') as f:
      return f.read()

class Service():
   # Cached top level endpoint.
   def get_all(self, request):
      ip = self._ip(request)

      if not self.cache.exists():
         page = self._generatePage(ip)
      else:
         page = self.cache.get(ip)
         if page == None:  # Cache miss.
            page = self._generatePage(ip)         
            self.cache.set(ip, page)

      return Response(page, mimetype='text/html')

   # Generates the page contents for a dregs serve from merged strip files. Returned page
   # omits the Response wrapper.
   def _generatePage(self, ip):
      strips = self._getIssueStrips(self.config['strip_path'])
      required = [ contents(self.config['header']) ]
      chosen = subset(strips, self.config['show'], ip)
      issueStyles = contents(self.config['issue_style'])
      stripMarkup, stripStyles = consolidate(required + chosen)
      return self.render('main.html',
                         strips=stripMarkup,
                         style=stripStyles,
                         issue_style=issueStyles)

   # Returns a list of all the contents of all filenames ending with '.html' in
   # given directory.
   def _getIssueStrips(self, directory):
      stripFilenames = filter(lambda f : f.endswith('.html'), ls(directory))
      stripFilenames = map(lambda f : join(directory, f), stripFilenames)
      stripFilenames = sorted(stripFilenames)
      return map(contents, stripFilenames)

   # Returns the remote IP address of the request, or 0 if IP parsing fails.
   def _ip(self, request):
      try:
         ip = ipToInt(request.args['ip'] if 'ip' in request.args else request.remote_addr)
      except:  # Default to 0 just in case.
         ip = 0
      return ip

   def __init__(self, template_path, config, cache=None):
      self.url_map = Map([
         Rule('/', endpoint="all")
      ])
      self.jinja_env = Environment(loader=FileSystemLoader(template_path), autoescape=False)
      self.config = config
      self.cache = PageCache(cache, len(self._getIssueStrips(self.config['strip_path'])))

   def wsgi_app(self, environ, start_response):
      request = Request(environ)
      response = self.dispatch_request(request)
      return response(environ, start_response)

   def render(self, template_name, **context):
      t = self.jinja_env.get_template(template_name)
      return t.render(context)

   def __call__(self, environ, start_response):
      return self.wsgi_app(environ, start_response)

   def dispatch_request(self, request):
      adapter = self.url_map.bind_to_environ(request.environ)
      try:
         endpoint, values = adapter.match()
         response = getattr(self, 'get_' + endpoint)(request, **values)
         return response
      except HTTPException, e:
         return e

class PageCache:
   def __init__(self, client, keyMod):
      self.keyMod = keyMod
      self.client = client
      if client != None:
         self.flush()

   def exists(self):
      return self.client != None

   def get(self, ip):
      return self.client.get(str(ip % self.keyMod))

   def set(self, ip, page):
      return self.client.set(str(ip % self.keyMod), page)

   def flush(self):
      return self.client.flush_all()
