import unittest

from haggle_agent import Brief, Buyer, simulate, tournament

B = Brief(1200, 850, 1000, rounds=8, leverage=["a competitor quoted lower"])


class Tests(unittest.TestCase):
    def test_brief_validation(self):
        with self.assertRaises(ValueError):
            Brief(1000, 900, 800)

    def test_offers_monotonic_and_capped(self):
        for strat in ("boulware", "linear", "conceder"):
            buyer = Buyer(B, strat)
            offers = [buyer.offer(r, []) for r in range(B.rounds)]
            self.assertEqual(offers, sorted(offers))
            self.assertLessEqual(max(offers), B.walkaway)
            self.assertLess(offers[0], B.target)

    def test_boulware_holds_firmer_than_conceder(self):
        bw, cc = Buyer(B, "boulware"), Buyer(B, "conceder")
        bw_offers = [bw.offer(r, []) for r in range(4)]
        cc_offers = [cc.offer(r, []) for r in range(4)]
        self.assertLess(bw_offers[3], cc_offers[3])

    def test_deal_within_zopa(self):
        res = simulate(B, seller_reserve=900)
        self.assertEqual(res["outcome"], "deal")
        self.assertTrue(900 <= res["price"] <= 1000)
        self.assertGreater(res["savings"], 0)

    def test_no_deal_without_zopa(self):
        res = simulate(B, seller_reserve=1100)
        self.assertEqual(res["outcome"], "no_deal")

    def test_accept_cheap_ask_immediately(self):
        res = simulate(Brief(1000, 990, 995, rounds=4), seller_reserve=100, seller_e=50)
        self.assertEqual(res["outcome"], "deal")

    def test_message_and_tournament(self):
        self.assertIn("final offer", Buyer(B).message(1000, B.rounds - 1))
        rows = tournament(B)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(0 <= r["deal_rate"] <= 1 for r in rows))


if __name__ == "__main__":
    unittest.main()
