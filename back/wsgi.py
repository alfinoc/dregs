from os import path 
from service import Service
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   currPath = path.dirname(__file__)
   template_path = path.join(currPath, '../global')
   issue_path = 'issues/mock'
   app = Service(template_path, issue_path)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/global':  path.join(path.dirname(__file__), '../global'),
      '/resources': path.join(path.dirname(__file__), '../{0}/resources'.format(issue_path))
   })
   return app
