from wsgiref.simple_server import make_server, WSGIServer
from socketserver import ThreadingMixIn


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    pass


if __name__ == "__main__":
    from app import app
    import sys

    httpd = make_server("", int(sys.argv[1]), app, ThreadingWSGIServer)
    try:
        httpd.serve_forever()
    except:
        httpd.shutdown()
        httpd.server_close()
        # app.run(host="localhost", port=8080, debug=True)
