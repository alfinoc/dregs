from werkzeug.serving import run_simple
from wsgi import create_app
from sys import argv
from os import getcwd, path

cached = '-c' in argv

if len(argv) > 1:
   app = create_app(path.join(getcwd(), argv[1]), cached=cached)
else:
   app = create_app(cached=cached)

run_simple('localhost', 5000, app, use_debugger=True, use_reloader=True)
