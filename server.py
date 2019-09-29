from wsgiref.simple_server import make_server
from main import application
httpd = make_server('', 8888, application)
print("Serving HTTP on port 8888...")
httpd.serve_forever()
