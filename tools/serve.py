"""Serve only the public app and bounded local cooking search. Python standard library only."""
import argparse
import json
import os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlsplit
import mimetypes
import threading
from cooking_assistant import answer

ROOT=Path(__file__).resolve().parent.parent
MODEL=os.environ.get('KITCHEN_MODEL','')
SLOTS=threading.BoundedSemaphore(2)

class Handler(BaseHTTPRequestHandler):
    def allowed_host(self):
        return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
    def respond(self,status,value):
        data=json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.allowed_host(): return self.respond(403,{'error':'Local host required'})
        path=unquote(urlsplit(self.path).path)
        if path=='/api/status': return self.respond(200,{'mode':'model-assisted-retrieval' if MODEL else 'recipe-search','model_configured':bool(MODEL)})
        if path=='/': path='/index.html'
        relative=path.lstrip('/')
        if relative not in {'index.html','sw.js','manifest.webmanifest'} and not relative.startswith('icons/'):
            return self.respond(404,{'error':'Not found'})
        file=(ROOT/relative).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file(): return self.respond(404,{'error':'Not found'})
        body=file.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-cache');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body)
    def do_POST(self):
        if not self.allowed_host(): return self.respond(403,{'error':'Local host required'})
        origin=self.headers.get('Origin')
        allowed={f'http://localhost:{self.server.server_port}',f'http://127.0.0.1:{self.server.server_port}'}
        if origin and origin not in allowed: return self.respond(403,{'error':'Same-origin requests only'})
        if self.path!='/api/ask': return self.respond(404,{'error':'Not found'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json': return self.respond(415,{'error':'JSON required'})
        try: length=int(self.headers.get('Content-Length','0'))
        except ValueError: return self.respond(400,{'error':'Invalid length'})
        if not 0<length<=4096: return self.respond(413,{'error':'Request too large or empty'})
        if not SLOTS.acquire(blocking=False): return self.respond(429,{'error':'Assistant busy; retry shortly'})
        try:
            self.connection.settimeout(30)
            payload=json.loads(self.rfile.read(length))
            if not isinstance(payload,dict) or set(payload)-{'question','recipe_id'}: return self.respond(400,{'error':'Only a question and recipe ID are accepted'})
            recipes=json.loads((ROOT/'data/data.json').read_text(encoding='utf-8'))['recipes']
            recipe=next((r for r in recipes if r['id']==payload.get('recipe_id')),None)
            if not recipe: return self.respond(404,{'error':'Recipe not found'})
            self.respond(200,answer(recipe,payload.get('question'),MODEL))
        except (ValueError,TypeError,TimeoutError): self.respond(400,{'error':'Invalid cooking request'})
        finally: SLOTS.release()
    def log_message(self,fmt,*args):
        # Do not log questions or personal recipe context.
        pass

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'Kitchen: http://127.0.0.1:{server.server_port} — '+('optional local model enabled' if MODEL else 'local recipe search; no model required'),flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
