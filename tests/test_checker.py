import unittest
from checker import analyze, RULES, import_offers

class CheckerTests(unittest.TestCase):
    def test_transfer_is_priority(self):
        r = analyze('Use your personal bank account to receive and transfer money. Keep a commission.')
        self.assertEqual(r['band'], 'high')
        self.assertIn('transfer', [f['id'] for f in r['flags']])
    def test_malay_transfer(self):
        self.assertEqual(analyze('Terima dan pindahkan wang menggunakan akaun bank peribadi anda.')['band'], 'high')
    def test_messenger_alone_is_weak(self):
        r = analyze('Campus cafe assistant. RM12 hourly. Contact us on WhatsApp for an interview.')
        self.assertEqual(r['band'], 'low')
    def test_negated_request_is_context(self):
        r = analyze('We never ask you to share your OTP. Do not receive and transfer money for strangers.')
        self.assertFalse(r['flags'])
        self.assertTrue(r['context_notes'])
    def test_contrast_does_not_hide_request(self):
        self.assertEqual(analyze('We never ask for passwords, but share your OTP for this role.')['band'],'high')
        self.assertEqual(analyze('Do not delay: share your OTP for payroll activation.')['band'],'high')
    def test_repetition_does_not_inflate(self):
        t = 'Pay a registration fee today.'
        self.assertEqual(analyze(t)['score'], analyze(t*5)['score'])
    def test_twenty_bilingual_flags(self):
        self.assertEqual(len(RULES),20)
        self.assertTrue(all(r['title']['ms'] and r['why']['ms'] for r in RULES))
    def test_bad_input(self):
        for x in ['', '  ', 'abc', None, 'x'*20001]:
            with self.assertRaises(ValueError): analyze(x)
    def test_import_csv_quotes(self):
        rows = import_offers('title,text\n"Night, shift","A library assistant position with hourly pay."', 'csv')
        self.assertEqual(rows[0]['title'], 'Night, shift')
    def test_import_rejects_invalid(self):
        with self.assertRaises(ValueError): import_offers('[{"title":"x"}]','json')
    def test_evidence_offsets(self):
        t = '✨ Student job! Share your OTP to activate payroll.'
        r = analyze(t)
        self.assertTrue(r['flags'])
        for f in r['flags']:
            for e in f['evidence']: self.assertEqual(t[e['start']:e['end']],e['text'])

if __name__ == '__main__': unittest.main()
