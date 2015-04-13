from os import path 
from service import Service
from werkzeug.wsgi import SharedDataMiddleware

def create_app():
   currPath = path.dirname(__file__)
   template_path = path.join(currPath, '../global')
   app = Service(template_path)
   app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/global':  path.join(path.dirname(__file__), '../global'),
   })
   return app
