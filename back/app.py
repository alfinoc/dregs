from werkzeug.serving import run_simple
from wsgi import create_app
from sys import argv

if len(argv) > 1:
   app = create_app(argv[1])
else:
   app = create_app()
run_simple('localhost', 5000, app, use_debugger=True, use_reloader=True)
