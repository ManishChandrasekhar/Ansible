#!/usr/bin/env python3
 
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import subprocess
import json
import pwd

# Invoke with get request to http://training.linuxdojo.com:8888/<api_key>/<username>
# This will invoke "./ap site.yml" in the specififed user's ~/development/ansible dir.

# Set API key
apikey = "Oht5aV0j"



# Add ThreadingMixin to make the HTTPServer multithreaded
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


# HTTPRequestHandler class
class HTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET
    def do_GET(self):
        parts = [e.strip() for e in self.path.split("/") if e.strip()]
        found = False
        if len(parts) != 2:
            data = {"message": "bad endpoint"}
        else:
            key, user = parts
            if key != apikey:
                data = {"message": "incorrect api key"}
            else:
                try:
                    found = pwd.getpwnam(user)
                except KeyError as e:
                    data = {"message": "incorrect user"}
        if not found:
            self.send_error(401, str(data))
        else:
            ap_invoke = "su - {user} -c 'cd /home/{user}/development/ansible; ./ap site.yml'".format(user=user)
            p = subprocess.Popen(ap_invoke, shell=True, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = p.stdout.read()
            rc = p.wait()
            if rc:
                self.send_error(403, output.decode('utf8'))
            if output:
                self.wfile.write(bytes(output.decode('utf8').replace('\n', '<br/>'), "utf8"))


def run():
    bind_addr = "0.0.0.0"
    port = 8888
    print('Starting server (listening on {}:{})...'.format(bind_addr, port))
    # Server settings
    server_address = ('0.0.0.0', 8888)
    httpd = ThreadingHTTPServer(server_address, HTTPServer_RequestHandler)
    httpd.serve_forever()
 
if __name__ == "__main__": 
    run()
