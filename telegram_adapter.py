"""Optional Telegram bot. Offline fixtures and dry-run polling are the defaults."""
import argparse,json,os,re,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from checker import analyze

class Telegram:
    def __init__(self,token):
        if not re.fullmatch(r'\d{5,}:[A-Za-z0-9_-]{20,}',token or ''):raise ValueError('Set a valid TELEGRAM_BOT_TOKEN in the process environment.')
        self._base='https://api.telegram.org/bot'+token+'/'
    def call(self,method,payload):
        if method not in {'getUpdates','sendMessage'}:raise ValueError('Unsupported Telegram method.')
        req=Request(self._base+method,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
        try:
            with urlopen(req,timeout=35) as response:data=json.load(response)
        except (URLError,HTTPError,TimeoutError):raise RuntimeError('Telegram request failed. Check network/token/permissions; credentials omitted.') from None
        if not data.get('ok'):raise RuntimeError('Telegram rejected the request; inspect bot configuration.')
        return data['result']
    def updates(self,offset):return self.call('getUpdates',{'offset':offset,'timeout':25,'allowed_updates':['message']})
    def send(self,chat_id,text):return self.call('sendMessage',{'chat_id':chat_id,'text':text[:4000],'link_preview_options':{'is_disabled':True}})

def prepare_reply(update,allowed):
    msg=update.get('message',{});chat=msg.get('chat',{})
    if chat.get('type')!='private' or str(chat.get('id')) not in allowed:return None
    text=msg.get('text','')
    if text.startswith('/start'):
        result='Pause job checker: paste a redacted job offer (10–20,000 characters). Telegram receives your messages. No server text retention; delete sensitive details first. Rules are educational, not proof of fraud or safety.'
    elif not text:return None
    else:
        try:
            r=analyze(text);labels={'high':'Pause and verify','review':'Clarify details','low':'Fewer signals found'}
            result=f"{labels[r['band']]} — {r['score']}/100 rule points (not a probability).\n"+'\n'.join('- '+f['title']['en']+': '+f['why']['en'] for f in r['flags'])+'\nVerify the employer independently. Keep OTPs, passwords and bank cards private. Manual PDRM check: https://semakmule.rmp.gov.my/\nNo flags does not mean safe.'
        except ValueError as e:result=str(e)
    return {'chat_id':chat['id'],'text':result}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path);p.add_argument('--poll',action='store_true');p.add_argument('--once',action='store_true');p.add_argument('--send-replies',action='store_true',help='Explicitly enable outgoing Telegram messages for allowlisted private chats.');p.add_argument('--offset-file',type=Path,default=Path('work/telegram-offset.json'));args=p.parse_args()
    allowed=set(filter(None,os.environ.get('TELEGRAM_ALLOWED_CHAT_IDS','').split(',')))
    if args.fixture:
        if args.send_replies:p.error('Fixture mode cannot send messages.')
        updates=json.loads(args.fixture.read_text());allowed=allowed or {'10001'}
        print(json.dumps([r for u in updates if (r:=prepare_reply(u,allowed))],indent=2));return
    if not args.poll:p.error('Choose --fixture for offline analysis or --poll for live updates.')
    if not allowed:p.error('Set TELEGRAM_ALLOWED_CHAT_IDS to a comma-separated allowlist.')
    bot=Telegram(os.environ.get('TELEGRAM_BOT_TOKEN',''));offset=0
    if args.offset_file.exists():offset=int(json.loads(args.offset_file.read_text())['offset'])
    while True:
        for update in bot.updates(offset):
            reply=prepare_reply(update,allowed)
            if reply:
                if args.send_replies:bot.send(**reply)
                else:print(json.dumps({'dry_run':True,'reply':reply},ensure_ascii=False),flush=True)
            offset=max(offset,int(update['update_id'])+1)
            args.offset_file.parent.mkdir(parents=True,exist_ok=True)
            temporary=args.offset_file.with_suffix('.tmp');temporary.write_text(json.dumps({'offset':offset}));temporary.replace(args.offset_file)
        if args.once:return
        time.sleep(.25)
if __name__=='__main__':
    try:main()
    except (RuntimeError,ValueError) as e:print(str(e),file=sys.stderr);sys.exit(1)
    except KeyboardInterrupt:pass
