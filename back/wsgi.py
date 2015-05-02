from os import path
from sys import exit
from json import load
from service import Service
from werkzeug.wsgi import SharedDataMiddleware

def _qualifyConfigFiles(issue_path, config):
   fileKeys = ['strip_path', 'resource_path', 'issue_style', 'header']
   for key in fileKeys:
      config[key] = path.join(issue_path, config[key])

def create_app(issue_path='issues/mock'):
   curr_path = path.dirname(__file__)
   template_path = path.join(curr_path, '../global')
   if not path.isdir(issue_path):
      exit('No issue directory {0}'.format(issue_path))

   config = load(open(path.join(issue_path, 'config')))
   _qualifyConfigFiles(issue_path, config)
   app = Service(template_path, config)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/global':  template_path,
      '/resources': config['resource_path']
   })
   return app
