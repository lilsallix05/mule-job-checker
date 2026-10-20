"""Regenerates the fictional English/Malay corpus in data/offers.json and data/offers.csv."""
import json,csv
from pathlib import Path
DATA=Path(__file__).resolve().parent.parent/'data'
pairs=[
('transfer','high','Weekend payment assistant','Receive and transfer money for our clients using your personal bank account. Keep a commission. No interview.','Pembantu bayaran hujung minggu','Terima dan pindahkan wang pelanggan melalui akaun bank peribadi anda. Komisen setiap transaksi. Tanpa temu duga.'),
('rental','high','Account partnership','Rent your bank account for our settlement service. RM500 weekly. Contact Telegram for instructions.','Rakan akaun','Sewa akaun untuk perkhidmatan penyelesaian kami. RM500 seminggu. Hubungi Telegram untuk arahan.'),
('otp','high','Payroll activation','Send your OTP to our recruiter to activate payroll. Act now; limited slots.','Pengaktifan gaji','Hantar OTP kepada perekrut untuk aktifkan gaji. Segera, slot terhad.'),
('card','high','Remote cashier','Courier your debit card to the supervisor for cash collection. Training begins next week.','Juruwang jarak jauh','Hantar kad debit kepada penyelia untuk kutipan tunai. Latihan bermula minggu depan.'),
('login','high','Settlement operator','Provide your banking password for the settlement operator position. We will do the processing.','Pengendali penyelesaian','Beri kata laluan bank untuk jawatan pengendali penyelesaian. Kami akan memproses transaksi.'),
('evasion','high','Transfer support','Split payments to avoid bank checks. Work from your room and receive a daily commission.','Sokongan pindahan','Pecahkan bayaran untuk elak semakan bank. Bekerja dari bilik dan terima komisen harian.'),
('topup_chain','high','Product-task rewards','Paid per task. Top up RM200 to withdraw your commission. A registration fee is needed to join.','Ganjaran tugas produk','Bayaran setiap tugas. Tambah nilai RM200 untuk pengeluaran komisen. Yuran pendaftaran diperlukan.'),
('secret_funds','high','Private finance clerk','Forward customer funds to another account. Don’t tell the bank about this work. Keep it secret.','Kerani kewangan peribadi','Terima dan hantar wang kepada akaun lain. Jangan beritahu bank tentang kerja ini.'),
('lend_account','high','Spare-account income','Lend us your account for incoming overseas payments. Easy money, no interview.','Pendapatan akaun tambahan','Sewa akaun untuk bayaran dari luar negara. Wang mudah, tanpa temu duga.'),
('remote_device','high','Payment app assistant','Install AnyDesk for setup. Send your bank PIN to the trainer. Training deposit is refundable.','Pembantu aplikasi bayaran','Pasang AnyDesk untuk persediaan. Hantar PIN bank kepada jurulatih. Deposit latihan dipulangkan.'),
('fee','review','Data entry placement','Data entry position at a fictional agency. Pay a registration fee before receiving the written contract.','Penempatan kemasukan data','Jawatan kemasukan data di agensi rekaan. Bayar yuran pendaftaran sebelum menerima kontrak bertulis.'),
('identity','review','Event registration crew','Upload a passport copy before we reveal the venue or company details. Shifts are on Saturday.','Krew pendaftaran acara','Hantar salinan pasport sebelum kami nyatakan tempat atau syarikat. Syif pada hari Sabtu.'),
('crypto','review','Digital assistant','Buy USDT for the equipment deposit. Work involves updating a product spreadsheet each week.','Pembantu digital','Bayar dengan USDT untuk deposit peralatan. Kerja melibatkan kemas kini hamparan produk setiap minggu.'),
('apk','review','Mobile survey work','Install this APK from the recruiter to record surveys. We will explain permissions after installation.','Kerja tinjauan mudah alih','Pasang APK daripada perekrut untuk merekod tinjauan. Kebenaran diterangkan selepas pemasangan.'),
('task_escalation','review','Task account reset','Top up RM100 to withdraw earnings from completed tasks. Support is available by email.','Tetapan semula akaun tugas','Tambah nilai RM100 untuk pengeluaran pendapatan tugas yang selesai. Sokongan melalui e-mel.'),
('promise','review','Daily income opportunity','Guaranteed daily income with no interview. The exact duties will be explained after you accept.','Peluang pendapatan harian','Pendapatan terjamin tanpa temu duga. Tugas sebenar diterangkan selepas anda menerima tawaran.'),
('referral','review','Campus promoter','Recruit friends for a bonus. No interview required. The promotion terms will be shared later.','Promoter kampus','Ajak kawan untuk bonus. Tanpa temu duga. Terma promosi akan diberikan kemudian.'),
('payroll_context','review','Payroll setup question','Send your personal bank account number after signing the employment contract. Ask HR if you need help.','Soalan persediaan gaji','Berikan nombor akaun bank peribadi selepas menandatangani kontrak pekerjaan. Hubungi HR untuk bantuan.'),
('cafe','low','Campus cafe assistant','Cafe assistant, RM12 per hour. Weekend shifts, paid monthly. Contact WhatsApp to arrange an in-person interview.','Pembantu kafe kampus','Pembantu kafe, RM12 sejam. Syif hujung minggu, gaji bulanan. Hubungi WhatsApp untuk temu duga bersemuka.'),
('library','low','Library shelving','Shelve books for 8 hours weekly. Apply through the university careers office. Written terms provided at interview.','Penyusun buku perpustakaan','Susun buku selama 8 jam seminggu. Mohon melalui pejabat kerjaya universiti. Terma bertulis diberi semasa temu duga.'),
('tutor','low','Maths tutor','Teach introductory maths on Tuesdays. Applicants complete a short teaching exercise. Pay and lesson times are in the contract.','Tutor matematik','Ajar matematik asas pada hari Selasa. Pemohon melengkapkan latihan mengajar ringkas. Gaji dan waktu dalam kontrak.'),
('safety_notice','low','Recruitment safety note','We never ask you to share your OTP. Do not receive and transfer money for strangers. Check the official careers page.','Nota keselamatan pengambilan','Jangan kongsi OTP. Jangan terima dan pindahkan wang untuk orang asing. Semak laman kerjaya rasmi.'),
('lab','low','Lab inventory assistant','Count laboratory supplies with a supervisor. Paid hourly after approved timesheets. No registration fee is required.','Pembantu inventori makmal','Kira bekalan makmal bersama penyelia. Bayaran sejam selepas rekod waktu diluluskan. Tidak perlu yuran pendaftaran.'),
('design','low','Poster illustrator','Design two event posters. A written brief, revision limit and milestone payment schedule are available before acceptance.','Ilustrator poster','Reka dua poster acara. Taklimat bertulis, had pindaan dan jadual bayaran tersedia sebelum penerimaan.'),
('sports','low','Sports event steward','Guide visitors during a campus sports day. Limited slots. The organiser provides a written schedule and named supervisor.','Petugas acara sukan','Bantu pelawat semasa hari sukan kampus. Slot terhad. Penganjur menyediakan jadual bertulis dan penyelia bernama.'),
]
rows=[]
for i,(group,label,title,text,ms_title,ms) in enumerate(pairs):
    for lang,t,body in [('en',title,text),('ms',ms_title,ms)]:
        rows.append({'id':f'offer-{i+1:02d}-{lang}','family':group,'language':lang,'title':t,'text':body,'label':label,'synthetic':True,'provenance':'Authored fictional educational example, 2026-10-19; no real person or employer.'})
(DATA/'offers.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with open(DATA/'offers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
