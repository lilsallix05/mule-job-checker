"""Explainable educational job-offer review. No network calls or persistence."""
import csv
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.0'
MAX_CHARS = 20000

def rule(key, weight, pattern, en, ms, why_en, why_ms):
    return {'id':key, 'weight':weight, 'pattern':pattern, 'title':{'en':en,'ms':ms}, 'why':{'en':why_en,'ms':why_ms}}

RULES = [
rule('transfer',50,r'\b(?:receive\s+(?:and|then|&)\s+(?:transfer|forward|send)|terima\s+(?:dan|kemudian|&)\s+(?:pindah\w*|hantar)|forward\s+(?:customer\s+)?(?:funds|payments|money)|transfer\s+(?:customer\s+)?(?:funds|payments|money)\s+to)\b','Receive and move money','Terima dan pindahkan wang','Moving someone else’s funds through your account can expose you to money-mule activity. Pause and verify the employer independently.','Memindahkan wang orang lain melalui akaun anda boleh melibatkan aktiviti akaun keldai. Berhenti dan sahkan majikan secara bebas.'),
rule('personal_account',30,r'\b(?:your\s+(?:own\s+|personal\s+)?bank\s+account|personal\s+(?:bank\s+)?account|akaun\s+bank\s+peribadi|akaun\s+anda)\b','Your account becomes the workplace','Akaun anda digunakan untuk kerja','Payroll may require an account number. Using your account to process business funds is different; ask what the account will be used for.','Gaji mungkin memerlukan nombor akaun. Memproses wang perniagaan melalui akaun anda berbeza; tanya tujuan penggunaan akaun.'),
rule('rent_account',50,r'\b(?:rent\s+(?:out\s+)?(?:your\s+)?(?:bank\s+)?account|account\s+rental|sewa\s+(?:akaun|rekening)|lend\s+(?:us\s+)?your\s+(?:bank\s+)?account)\b','Rent or lend an account','Sewa atau pinjamkan akaun','An offer to rent an account is a direct reason to stop. Keep control of your banking access.','Tawaran menyewa akaun ialah sebab jelas untuk berhenti. Kekalkan kawalan akses perbankan anda.'),
rule('otp',50,r'\b(?:share|send|provide|give|hantar|beri|kongsi)\b[^.!?\n]{0,45}\b(?:otp|tac|one.time\s+(?:password|code)|pin\s+(?:bank|number)|bank\s+pin)\b','OTP, TAC or PIN requested','Permintaan OTP, TAC atau PIN','Authentication codes and banking PINs are not job application details. Do not disclose them.','Kod pengesahan dan PIN bank bukan maklumat permohonan kerja. Jangan kongsikannya.'),
rule('bank_login',50,r'\b(?:bank(?:ing)?\s+(?:login|password|credentials)|kata\s+laluan\s+bank|online\s+banking\s+access)\b','Banking access requested','Permintaan akses perbankan','A recruiter should not need access to your online banking. Verify through your bank’s official channel.','Perekrut tidak sepatutnya memerlukan akses perbankan dalam talian anda. Sahkan melalui saluran rasmi bank.'),
rule('card',45,r'\b(?:hand\s+over|send|post|courier|serah\w*|hantar)\b[^.!?\n]{0,35}\b(?:atm\s+card|bank\s+card|debit\s+card|kad\s+(?:atm|bank|debit))\b','Hand over a bank card','Serahkan kad bank','Giving another person your card transfers control over your account. Keep cards and credentials with you.','Memberikan kad kepada orang lain menyerahkan kawalan akaun anda. Simpan kad dan maklumat akses.'),
rule('upfront',25,r'\b(?:registration\s+fee|activation\s+fee|training\s+deposit|security\s+deposit|upfront\s+(?:fee|payment)|yuran\s+(?:pendaftaran|pengaktifan)|deposit\s+(?:latihan|keselamatan))\b','Pay before starting','Bayar sebelum mula','An upfront payment can be part of an advance-fee scheme. Request written terms and independent verification before paying.','Bayaran awal boleh menjadi sebahagian penipuan bayaran pendahuluan. Dapatkan terma bertulis dan pengesahan bebas sebelum membayar.'),
rule('topup',30,r'\b(?:top\s?up|recharge|tambah\s+nilai)\b[^.!?\n]{0,55}\b(?:task|withdraw|commission|tugas|pengeluaran|komisen)\b','Top up to unlock earnings','Tambah nilai untuk keluarkan pendapatan','Being asked to add money to withdraw earnings is a strong reason to pause. Do not chase a promised balance.','Permintaan menambah wang untuk mengeluarkan pendapatan ialah sebab kukuh untuk berhenti. Jangan mengejar baki yang dijanjikan.'),
rule('crypto',22,r'\b(?:convert\s+.{0,25}(?:crypto|usdt|bitcoin)|buy\s+(?:usdt|crypto|bitcoin)|bayar\s+(?:dengan\s+)?(?:kripto|usdt)|tukar\s+.{0,20}kripto|gift\s+cards?\s+(?:as\s+)?payment)\b','Unusual payment route','Kaedah bayaran luar biasa','Crypto or gift-card transfers can be difficult to reverse. Check why a job requires you to purchase or move value.','Pemindahan kripto atau kad hadiah sukar dibatalkan. Semak mengapa kerja memerlukan anda membeli atau memindahkan nilai.'),
rule('commission',10,r'\b(?:keep\s+(?:a\s+)?(?:\d+\s*%|commission)|commission\s+(?:per|on)\s+(?:transfer|transaction)|komisen\s+(?:setiap|bagi)\s+(?:transaksi|pindahan))','Commission for moving funds','Komisen untuk pindahan wang','Commission tied to money movement deserves scrutiny, especially alongside requests to use your own account.','Komisen yang berkaitan pemindahan wang perlu disemak, terutama jika menggunakan akaun sendiri.'),
rule('secrecy',20,r'\b(?:don.t\s+tell\s+(?:the\s+bank|your\s+parents|anyone)|keep\s+(?:this|it)\s+secret|jangan\s+beritahu\s+(?:bank|sesiapa|keluarga)|rahsia\s+daripada\s+bank)\b','Keep it secret','Rahsiakan urusan','Instructions to hide the work from your bank or trusted people reduce opportunities to verify it.','Arahan merahsiakan kerja daripada bank atau orang dipercayai mengurangkan peluang untuk mengesahkannya.'),
rule('urgent',8,r'\b(?:act\s+now|limited\s+slots|today\s+only|within\s+\d+\s+minutes|segera|slot\s+terhad|hari\s+ini\s+sahaja)\b','Pressure to decide quickly','Tekanan membuat keputusan segera','Urgency is common in ordinary recruitment too. Treat it as context and take time to verify details.','Desakan juga wujud dalam pengambilan biasa. Anggapnya sebagai konteks dan luangkan masa untuk menyemak.'),
rule('messenger',5,r'\b(?:whatsapp|telegram|wechat)\b','Messaging app contact','Hubungan melalui aplikasi mesej','Messaging apps alone do not establish fraud. Confirm the person and role using an independently found company channel.','Aplikasi mesej sahaja tidak membuktikan penipuan. Sahkan individu dan jawatan melalui saluran syarikat yang dicari sendiri.'),
rule('no_interview',10,r'\b(?:no\s+interview|without\s+(?:an?\s+)?interview|tanpa\s+temu\s+duga|tak\s+perlu\s+temu\s+duga)\b','No interview or screening','Tiada temu duga atau saringan','Some short jobs have simple hiring. Combined with unusual financial tasks, absent screening deserves a closer look.','Sesetengah kerja singkat mempunyai pengambilan ringkas. Jika disertai urusan wang luar biasa, ketiadaan saringan perlu diteliti.'),
rule('easy_pay',12,r'\b(?:guaranteed\s+(?:daily\s+)?(?:income|earnings)|easy\s+money|earn\s+rm\s*\d+\s+(?:in|for)\s+\d+\s+minutes|pendapatan\s+(?:lumayan|terjamin)|wang\s+mudah)\b','Easy or guaranteed earnings','Pendapatan mudah atau terjamin','Vague income promises omit the actual work, hours and payment terms. Ask for a written job description.','Janji pendapatan kabur tidak menjelaskan tugas, waktu dan terma bayaran. Minta huraian kerja bertulis.'),
rule('tasks',8,r'\b(?:paid\s+per\s+(?:like|task|review)|like\s+(?:videos|products)|product\s+rating|bayaran\s+setiap\s+tugas|suka\s+video|beri\s+rating)\b','Paid clicks or rating tasks','Tugas klik atau penilaian berbayar','Task-based pay is not proof of a scam. Watch for escalation from small rewards to deposits or money transfers.','Bayaran berasaskan tugas bukan bukti penipuan. Awasi perubahan daripada ganjaran kecil kepada deposit atau pindahan wang.'),
rule('install',25,r'\b(?:install\s+(?:this\s+|our\s+|an?\s+)?(?:apk|anydesk|remote\s+access)|pasang\s+(?:apk|anydesk|aplikasi\s+luar))\b','Install an outside app','Pasang aplikasi luar','Unverified apps or remote-access tools can expose your device. Obtain software only after independently verifying its purpose.','Aplikasi tidak disahkan atau alat akses jauh boleh mendedahkan peranti. Sahkan tujuan perisian secara bebas dahulu.'),
rule('identity',20,r'\b(?:send|upload|hantar|muat\s+naik)\b[^.!?\n]{0,40}\b(?:ic\s+(?:photo|copy)|passport\s+(?:photo|copy)|selfie\s+with\s+(?:your\s+)?(?:ic|id)|gambar\s+ic|salinan\s+pasport)\b','Identity documents requested early','Dokumen pengenalan diminta awal','Hiring can require identity checks, but establish who receives documents, why they need them and how they protect them.','Pengambilan mungkin memerlukan semakan identiti. Sahkan penerima, tujuan dan perlindungan dokumen dahulu.'),
rule('recruit',15,r'\b(?:recruit\s+.{0,20}(?:bonus|commission)|referral\s+fee|ajak\s+kawan\s+.{0,20}(?:bonus|komisen))\b','Payment for recruiting friends','Bayaran merekrut rakan','Referral rewards can be legitimate. Examine whether recruitment replaces meaningful work or requires a payment.','Ganjaran rujukan boleh sah. Teliti sama ada perekrutan menggantikan kerja sebenar atau memerlukan bayaran.'),
rule('bank_evasion',45,r'\b(?:split\s+(?:the\s+)?(?:payments|transfers)|avoid\s+(?:bank\s+)?(?:checks|detection|limits)|tell\s+the\s+bank\s+.{0,25}(?:gift|family)|elak\s+(?:semakan|had)\s+bank|pecahkan\s+(?:bayaran|pindahan))\b','Avoid bank checks','Elakkan semakan bank','Instructions to disguise or split transfers to evade checks warrant stopping and speaking with your bank.','Arahan menyembunyikan atau memecahkan pindahan untuk mengelakkan semakan memerlukan anda berhenti dan menghubungi bank.'),
]

NEGATION = re.compile(r"\b(?:never|do\s+not|don.t|will\s+not|won.t|must\s+not|jangan|tidak\s+(?:akan|perlu)|tak\s+perlu)\b", re.I)
EXEMPT = {'secrecy'}

def analyze(text):
    if not isinstance(text,str) or len(text.strip()) < 10 or len(text) > MAX_CHARS:
        raise ValueError('Enter 10–20,000 characters of offer text.')
    flags, notes = [], []
    for r in RULES:
        evidence=[]
        for m in re.finditer(r['pattern'], text, re.I):
            # Deliberately bounded clause heuristic: negation handling is not semantic understanding.
            prefix = re.split(r'[.!?;:\n]|\b(?:but|however|tetapi|namun)\b', text[max(0,m.start()-90):m.start()], flags=re.I)[-1]
            negated = r['id'] not in EXEMPT and bool(NEGATION.search(prefix[-70:]))
            suffix = text[m.end():m.end()+25]
            if r['id']=='upfront' and (re.search(r'\bno\s*$',prefix,re.I) or re.match(r'\s+(?:is\s+)?(?:not\s+required|waived)',suffix,re.I)): negated=True
            ev = {'start':m.start(),'end':m.end(),'text':m.group()}
            if negated:
                notes.append({'rule_id':r['id'],'evidence':ev,'reason':'negated_context'})
            else: evidence.append(ev)
        if evidence:
            flags.append({k:v for k,v in r.items() if k!='pattern'} | {'evidence':evidence})
    score=min(100,sum(f['weight'] for f in flags))
    band='high' if score>=45 else 'review' if score>=18 else 'low'
    return {'version':VERSION,'score':score,'band':band,'flags':sorted(flags,key=lambda f:-f['weight']),
            'context_notes':notes,'characters':len(text),'rule_count':len(RULES),
            'uncertainty':'This is an uncalibrated rules score, not a probability or a fraud verdict. Missing flags do not establish safety.',
            'provenance':'Local analysis. No text retained by the server. No identity, company or bank verification performed.'}

def import_offers(content, kind):
    if not isinstance(content,str) or len(content.encode('utf-8'))>262144: raise ValueError('Import must be smaller than 256 KiB.')
    try:
        if kind=='json':
            rows=json.loads(content)
            if isinstance(rows,dict): rows=rows.get('offers')
        elif kind=='csv': rows=list(csv.DictReader(io.StringIO(content)))
        elif kind=='txt': rows=[{'title':'Imported offer','text':content}]
        else: raise ValueError('Choose a .txt, .csv or .json file.')
    except (json.JSONDecodeError,csv.Error) as exc: raise ValueError('Could not parse the import file.') from exc
    if not isinstance(rows,list) or not 1<=len(rows)<=100: raise ValueError('Import 1–100 offers.')
    result=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or not isinstance(row.get('text'),str): raise ValueError(f'Offer {i+1} needs a text field.')
        analyze(row['text'])
        title=row.get('title',f'Offer {i+1}')
        if not isinstance(title,str) or len(title)>160: raise ValueError('Titles must be text under 160 characters.')
        result.append({'id':str(i+1),'title':title,'text':row['text']})
    return result

def evaluate():
    rows=json.loads((ROOT/'data/offers.json').read_text())
    labels=['low','review','high']; matrix=[[0]*3 for _ in labels]; errors=[]
    for row in rows:
        pred=analyze(row['text'])['band']; matrix[labels.index(row['label'])][labels.index(pred)]+=1
        if pred!=row['label']: errors.append({'id':row['id'],'expected':row['label'],'predicted':pred})
    return {'dataset':'50 authored synthetic examples; labels are intended review priority, not real-world fraud truth.',
            'n':len(rows),'labels':labels,'confusion_matrix':matrix,'agreement':sum(matrix[i][i] for i in range(3))/len(rows),
            'disagreements':errors,'limits':'Development corpus; used while designing rules, not a held-out estimate. No diagnostic accuracy claim.'}

if __name__=='__main__':
    import argparse,sys
    p=argparse.ArgumentParser(); p.add_argument('file',nargs='?'); p.add_argument('--evaluate',action='store_true'); a=p.parse_args()
    print(json.dumps(evaluate() if a.evaluate else analyze(Path(a.file).read_text() if a.file else sys.stdin.read()),ensure_ascii=False,indent=2))
