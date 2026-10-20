"""Loopback-only local application. No offer logging or persistent sessions."""
import argparse,json,mimetypes
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from checker import ROOT,RULES,analyze,import_offers,evaluate
from model import predict

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def allowed(self):
        port=self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}',f'localhost:{port}'}
    def reply(self,status,data,ctype='application/json; charset=utf-8'):
        if isinstance(data,(dict,list)): data=json.dumps(data,ensure_ascii=False).encode()
        if isinstance(data,str):data=data.encode()
        self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.allowed():return self.reply(403,{'error':'Local host only.'})
        path=urlsplit(self.path).path
        if path=='/api/library':return self.reply(200,json.loads((ROOT/'data/offers.json').read_text()))
        if path=='/api/method':return self.reply(200,{'rules':[{k:v for k,v in r.items() if k!='pattern'} for r in RULES],'rules_evaluation':evaluate(),'model_evaluation':json.loads((ROOT/'evidence/model-evaluation.json').read_text())})
        files={'/':'static/index.html','/app.js':'static/app.js','/style.css':'static/style.css','/offers.json':'data/offers.json','/offers.csv':'data/offers.csv','/campaign.md':'campaign/CAMPAIGN-KIT.md','/poster.html':'campaign/poster.html','/poster.css':'campaign/poster.css','/health':'health'}
        if path=='/health':return self.reply(200,{'status':'ok','mode':'local-only'})
        if path not in files:return self.reply(404,{'error':'Not found.'})
        p=ROOT/files[path];ctype=mimetypes.guess_type(p)[0] or 'text/plain'
        return self.reply(200,p.read_bytes(),ctype+'; charset=utf-8')
    def do_POST(self):
        if not self.allowed():return self.reply(403,{'error':'Local host only.'})
        origin=self.headers.get('Origin')
        if origin and origin not in {f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}:return self.reply(403,{'error':'Cross-origin requests are not allowed.'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.reply(415,{'error':'Use application/json.'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=300000: return self.reply(413,{'error':'Request must be 1–300,000 bytes.'})
            payload=json.loads(self.rfile.read(size))
            if not isinstance(payload,dict):raise ValueError('Expected a JSON object.')
            if self.path=='/api/analyze':
                text=payload.get('text');result=analyze(text);result['model']=predict(text);return self.reply(200,result)
            if self.path=='/api/import':return self.reply(200,{'offers':import_offers(payload.get('content'),payload.get('kind'))})
            return self.reply(404,{'error':'Not found.'})
        except (ValueError,UnicodeDecodeError) as exc:return self.reply(400,{'error':str(exc)})
    def setup(self):
        super().setup();self.connection.settimeout(15)

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18765);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
    print(f'Job offer checker: http://127.0.0.1:{a.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
