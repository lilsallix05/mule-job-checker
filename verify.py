"""Reproducible local checks; optional browser workflow uses a fresh ephemeral server."""
import argparse,hashlib,json,os,platform,subprocess,sys,threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--browser',action='store_true');a=p.parse_args()
    os.chdir(ROOT);(ROOT/'evidence').mkdir(exist_ok=True)
    checks=[]
    def run(name,args,output,env=None):
        start=datetime.now(ZoneInfo('Asia/Kuala_Lumpur')).isoformat()
        try:
            result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=180,env=env)
            Path(output).write_text(result.stdout+result.stderr);code=result.returncode
        except subprocess.TimeoutExpired:
            Path(output).write_text('Timed out after 180 seconds.');code=124
        except FileNotFoundError:
            Path(output).write_text(f'{args[0]} is not installed.');code=127
        checks.append({'name':name,'command':args,'started_at':start,'exit_code':code,'status':'passed' if code==0 else 'failed','output':output})
    run('Python behavioral tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'],'evidence/tests.txt')
    run('Deterministic supervised training and held-out evaluation',[sys.executable,'model.py'],'evidence/model-training-output.json')
    run('Rules development-corpus evaluation',[sys.executable,'checker.py','--evaluate'],'evidence/rules-evaluation.json')
    run('Telegram fixture, no network',[sys.executable,'telegram_adapter.py','--fixture','data/telegram-updates.json'],'evidence/telegram-dry-run.json')
    run('Python syntax',[sys.executable,'-m','py_compile','checker.py','model.py','server.py','telegram_adapter.py','verify.py'],'evidence/compile.txt')
    run('Browser JavaScript syntax',['node','--check','static/app.js'],'evidence/js-syntax.txt')
    if a.browser:
        from http.server import ThreadingHTTPServer
        from server import Handler
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            env=os.environ.copy();env['APP_URL']=f'http://127.0.0.1:{server.server_port}/'
            run('Browser workflows with a fresh loopback service',['node','tests/browser.cjs'],'evidence/browser-output.txt',env)
        finally:server.shutdown();server.server_close();thread.join()
    browser_path=ROOT/'evidence/browser-verification.json';browser=None
    if browser_path.exists():
        browser=json.loads(browser_path.read_text());browser['source_matches_current']=all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected for name,expected in browser.get('source_hashes',{}).items()) and bool(browser.get('source_hashes'))
    needed=['README.md','docs/CASE-STUDY.md','docs/TELEGRAM.md','requirements.txt','package-lock.json','campaign/CAMPAIGN-KIT.md','campaign/poster.html']
    missing=[s for s in needed if not (ROOT/s).is_file()];checks.append({'name':'Required local package files','status':'passed' if not missing else 'failed','missing':missing})
    report={'project_id':'mule-job-checker','verified_at':datetime.now(ZoneInfo('Asia/Kuala_Lumpur')).isoformat(),'platform':platform.platform(),'python':sys.version,'checks':checks,'browser':browser,'status':'passed' if all(c['status']=='passed' for c in checks) else 'failed',
        'not_run':['Live Telegram polling or replies','Real PDRM lookup','Real job-offer evaluation','Fluent Malay translation review','User campaign/pilot','Production hosting and load/security audit']}
    (ROOT/'evidence/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({'status':report['status'],'checks':len(checks),'browser_source_current':browser.get('source_matches_current') if browser else None}))
    return 0 if report['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
