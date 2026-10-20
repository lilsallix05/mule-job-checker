import json,unittest
from unittest.mock import patch
from checker import ROOT
from model import predict,TEST_FAMILIES
from telegram_adapter import Telegram,prepare_reply
class ModelTests(unittest.TestCase):
    def test_split_no_family_or_exact_leakage(self):
        rows=json.loads((ROOT/'data/offers.json').read_text());model=json.loads((ROOT/'data/model.json').read_text())
        train=[r for r in rows if r['id'] in model['training_ids']];test=[r for r in rows if r['family'] in TEST_FAMILIES]
        self.assertEqual((len(train),len(test)),(34,16));self.assertFalse({r['family'] for r in train}&{r['family'] for r in test});self.assertFalse({r['text'].lower() for r in train}&{r['text'].lower() for r in test})
    def test_model_finite_known_and_unknown(self):
        self.assertIn(predict('Receive and transfer money')['label'],['low','review','high']);self.assertEqual(predict('zzxxyy qqqrrr')['known_tokens'],0);self.assertEqual(predict('zzxxyy qqqrrr')['label'],'insufficient')
class AdapterTests(unittest.TestCase):
    def test_allowed_private_only(self):
        updates=json.loads((ROOT/'data/telegram-updates.json').read_text());self.assertIn('Pause and verify',prepare_reply(updates[1],{'10001'})['text']);self.assertIsNone(prepare_reply(updates[1],{'99'}));self.assertIsNone(prepare_reply(updates[2],{'99999'}))
    def test_send_contract(self):
        bot=Telegram('123456:abcdefghijklmnopqrstuvwxyz')
        with patch.object(bot,'call',return_value={}) as call:
            bot.send(10001,'Educational response');self.assertEqual(call.call_args.args[0],'sendMessage');self.assertTrue(call.call_args.args[1]['link_preview_options']['is_disabled'])
    def test_poll_contract(self):
        bot=Telegram('123456:abcdefghijklmnopqrstuvwxyz')
        with patch.object(bot,'call',return_value=[]) as call:
            self.assertEqual(bot.updates(9),[]);self.assertEqual(call.call_args.args,('getUpdates',{'offset':9,'timeout':25,'allowed_updates':['message']}))
    def test_token_not_in_failure(self):
        from urllib.error import URLError
        token='123456:abcdefghijklmnopqrstuvwxyz'
        with patch('telegram_adapter.urlopen',side_effect=URLError(token)):
            with self.assertRaises(RuntimeError) as cm:Telegram(token).updates(0)
            self.assertNotIn(token,str(cm.exception))
