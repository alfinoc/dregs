from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, BadRequest, Unauthorized
from werkzeug.utils import redirect
from functools import partial
from math import pow

def ipToInt(ip):
   parts = map(int, ip.split('.'))  # Could reverse but who cares?
   powers = map(partial(pow, 2), range(0, 64, 8))
   return int(sum(map(lambda (x, y) : x * y, zip(parts, powers))))

class Service():
   def get_all(self, request):
      try:
         ip = ipToInt(request.args['ip'] if 'ip' in request.args else request.remote_addr)
      except:  # Default to 0 just in case.
         ip = 0
      return Response(str(ip))

   def __init__(self, template_path):
      self.url_map = Map([
         Rule('/', endpoint="all")
      ])
      self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                   autoescape=True)

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
