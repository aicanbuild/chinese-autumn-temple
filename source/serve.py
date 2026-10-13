"""Local-only preview with enough queued connections for the scene's ES modules."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import socket

class Handler(SimpleHTTPRequestHandler):
 def log_message(self,format,*args):
  # Successful asset requests must not fill an unconsumed terminal pipe.
  if len(args)>1 and str(args[1]).startswith(('4','5')):super().log_message(format,*args)

class PreviewServer(ThreadingHTTPServer):
 address_family=socket.AF_INET6
 request_queue_size=128
 daemon_threads=True

if __name__=='__main__':
 directory=Path(__file__).resolve().parents[1]/'dist'
 server=PreviewServer(('::1',4188),partial(Handler,directory=str(directory)))
 print('Temple preview: http://localhost:4188/ (loopback only)',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close()
