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

from scope_css import consolidate
from combinations import subset

# Returns an integer rep. of the given 32-bit IP string xxx.xxx.xxx.xxx.
def ipToInt(ip):
   parts = map(int, ip.split('.'))  # Could reverse but who cares?
   powers = map(partial(pow, 2), range(0, 64, 8))
   return int(sum(map(lambda (x, y) : x * y, zip(parts, powers))))

# Returns the contents of the file with given name.
def contents(filename):
   with open(filename) as f:
      return f.read()

class Service():
   def get_all(self, request):
      config = load(open(self._joinIssue('config')))
      ip = self._ip(request)

      strips = self._getIssueStrips(self._joinIssue(config['strip_path']))
      required = [ contents(self._joinIssue(config['header'])) ]
      chosen = subset(strips, config['show'], ip)
      stripMarkup, stripStyles = consolidate(required + chosen)
      issueStyles = contents(self._joinIssue(config['issue_style']))
      return self.render('main.html', strips=stripMarkup, style=stripStyles,
                         issue_style=issueStyles)

   def _joinIssue(self, filename):
      return join(self.issue_path, filename)

   # Returns a list of all the contents of all filenames ending with '.html' in
   # given directory.
   def _getIssueStrips(self, directory):
      stripFilenames = filter(lambda f : f.endswith('.html'), ls(directory))
      stripFilenames = map(lambda f : join(directory, f), stripFilenames)
      return map(contents, stripFilenames)

   # Returns the remote IP address of the request, or 0 if IP parsing fails.
   def _ip(self, request):
      try:
         ip = ipToInt(request.args['ip'] if 'ip' in request.args else request.remote_addr)
      except:  # Default to 0 just in case.
         ip = 0
      return ip

   def __init__(self, template_path, issue_path):
      self.url_map = Map([ 
         Rule('/', endpoint="all")
      ])
      self.jinja_env = Environment(loader=FileSystemLoader(template_path))
      self.issue_path = issue_path

   def wsgi_app(self, environ, start_response):
      request = Request(environ)
      response = self.dispatch_request(request)
      return response(environ, start_response)

   def render(self, template_name, **context):
      t = self.jinja_env.get_template(template_name)
      return Response(t.render(context), mimetype='text/html')

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
