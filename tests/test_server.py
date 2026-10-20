import http.client,json,threading,unittest
from http.server import ThreadingHTTPServer
from server import Handler
class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.port=cls.server.server_port
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,data=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port);h={'Content-Type':'application/json'};h.update(headers or {})
        c.request(method,path,json.dumps(data) if data is not None else None,h);r=c.getresponse();body=r.read();status=r.status;response_headers=dict(r.getheaders());c.close();return status,body,response_headers
    def test_analyze_live_http(self):
        status,body,h=self.request('POST','/api/analyze',{'text':'Receive and transfer money in this new job.'})
        self.assertEqual(status,200);self.assertEqual(json.loads(body)['band'],'high');self.assertEqual(h['Cache-Control'],'no-store')
    def test_validation(self):
        for value in [{'text':''},{'text':123},[],{'text':'x'*20001}]:self.assertEqual(self.request('POST','/api/analyze',value)[0],400)
    def test_cross_origin(self):self.assertEqual(self.request('POST','/api/analyze',{'text':'An ordinary library assistant job.'},{'Origin':'https://untrusted.example'})[0],403)
    def test_host(self):self.assertEqual(self.request('GET','/',headers={'Host':'untrusted.example'})[0],403)
    def test_media_type(self):self.assertEqual(self.request('POST','/api/analyze',{'text':'An ordinary library assistant job.'},{'Content-Type':'text/plain'})[0],415)
    def test_static_allowlist(self):
        for path in ['/checker.py','/../data/model.json','/work/telegram-offset.json']:self.assertEqual(self.request('GET',path)[0],404)
    def test_library(self):
        status,body,_=self.request('GET','/api/library');self.assertEqual(status,200);self.assertEqual(len(json.loads(body)),50)
    def test_import_real_http(self):
        status,body,_=self.request('POST','/api/import',{'kind':'json','content':'[{"title":"Role","text":"A supervised laboratory inventory role."}]'})
        self.assertEqual(status,200);self.assertEqual(len(json.loads(body)['offers']),1)
    def test_no_offer_in_logs(self):
        from unittest.mock import patch
        with patch('sys.stderr.write') as write:self.request('POST','/api/analyze',{'text':'SECRET DATA with an ordinary part time role.'});write.assert_not_called()
