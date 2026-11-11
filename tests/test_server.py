import http.client
import json
from pathlib import Path
import sys
import threading
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from serve import Handler, ThreadingHTTPServer

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,body=None,headers=None):
        client=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        client.request(method,path,body,headers or {})
        response=client.getresponse();status=response.status;data=response.read();client.close();return status,data
    def test_site_served_but_source_files_denied(self):
        self.assertEqual(self.request('GET','/')[0],200)
        for path in ['/tools/serve.py','/.git/config','/data/data.json','/icons/../../README.md']:
            self.assertEqual(self.request('GET',path)[0],404)
    def test_host_and_origin_restrictions(self):
        self.assertEqual(self.request('GET','/',headers={'Host':'attacker.invalid'})[0],403)
        self.assertEqual(self.request('POST','/api/ask','{}',{'Content-Type':'application/json','Origin':'https://attacker.invalid'})[0],403)
    def test_question_response_and_payload_validation(self):
        payload={'recipe_id':'moong-dal-chilla','question':'What should I prepare first?'}
        status,raw=self.request('POST','/api/ask',json.dumps(payload),{'Content-Type':'application/json'})
        self.assertEqual(status,200);self.assertTrue(json.loads(raw)['evidence'])
        payload['labs']={'private':'not accepted'}
        self.assertEqual(self.request('POST','/api/ask',json.dumps(payload),{'Content-Type':'application/json'})[0],400)
        self.assertEqual(self.request('POST','/api/ask','[]',{'Content-Type':'application/json'})[0],400)

if __name__=='__main__': unittest.main()
