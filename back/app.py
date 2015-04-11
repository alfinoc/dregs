from werkzeug.serving import run_simple
from wsgi import create_app

run_simple('localhost', 5000, create_app(), use_debugger=True, use_reloader=True)
