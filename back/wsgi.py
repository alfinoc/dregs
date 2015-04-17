from os import path
from sys import exit
from service import Service
from werkzeug.wsgi import SharedDataMiddleware

def create_app(issue_path='issues/mock'):
   currPath = path.dirname(__file__)
   template_path = path.join(currPath, '../global')
   issue_path = path.join(currPath, '../' + issue_path)
   if not path.isdir(issue_path):
      exit('No issue directory {0}'.format(issue_path))
   app = Service(template_path, issue_path)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/global':  path.join(path.dirname(__file__), '../global'),
      '/resources': path.join(path.dirname(__file__), '../{0}/resources'.format(issue_path))
   })
   return app
