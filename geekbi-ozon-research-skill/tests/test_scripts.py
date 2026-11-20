import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ozon_category_info
import ozon_category_list
import ozon_category_search
import ozon_goods_info
import ozon_goods_search
import ozon_keyword_info
import ozon_keyword_search
import ozon_mall_info
import ozon_mall_search
import ozon_review_search
import ozon_site_list
from ozon_search_common import build_url, validate_object_response, validate_search_response


class ParameterTests(unittest.TestCase):
    def test_goods_accepts_supported_filters(self):
        params = ozon_goods_search.parse_params([
            "siteId=1", "entityMode=SPU", "analyticsWindowDays=28", "catId=123",
            "soldMin=100", "priceMax=5000", "goodsScoreMin=4.5",
            "fulfillmentType=RFBS", "sort=sold", "order=desc", "page=1", "size=100",
        ])
        self.assertIn(("entityMode", "SPU"), params)

    def test_goods_rejects_unsupported_or_unsafe_values(self):
        for value in (
            "siteId=0", "analyticsWindowDays=30", "entityMode=PRODUCT",
            "goodsScoreMax=6", "sort=unknownField", "order=descend", "imageUrl=x",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ozon_goods_search.parse_params([value])
        with self.assertRaises(ValueError):
            ozon_goods_search.parse_params(["page=3", "size=100"])

    def test_other_capability_filters(self):
        self.assertIn(("preset", "china"), ozon_mall_search.parse_params([
            "preset=china", "mallStarMin=4", "sort=monthSold", "order=desc",
        ]))
        self.assertIn(("parentCatId", "0"), ozon_category_search.parse_params([
            "parentCatId=0", "itemCountMin=10", "sort=itemCount", "order=desc",
        ]))
        self.assertIn(("keyword", "наушники"), ozon_keyword_search.parse_params([
            "keyword=наушники", "monthSoldMin=10", "sort=monthSold", "order=desc",
        ]))
        self.assertIn(("goodsId", "123"), ozon_review_search.parse_params([
            "goodsId=123", "score=1", "sort=helpful", "order=desc",
        ]))

    def test_identifier_commands(self):
        with self.assertRaises(ValueError):
            ozon_goods_info.build_params(" ", None, 1, 7)
        with self.assertRaises(ValueError):
            ozon_mall_info.build_params(" ", 1)
        with self.assertRaises(ValueError):
            ozon_category_info.build_params(0, 1)
        with self.assertRaises(ValueError):
            ozon_keyword_info.build_params(None, None, 1)
        self.assertEqual(ozon_category_list.build_params(0, 1)[0], ("parentCatId", "0"))


class ContractTests(unittest.TestCase):
    def test_site_resolution(self):
        sites = [{
            "siteId": 1, "siteUID": "ru", "country": "RU", "name": "俄罗斯",
            "currency": "RUB", "siteHost": "www.ozon.ru",
        }, {
            "siteId": 2, "siteUID": "kz", "country": "KZ", "name": "哈萨克斯坦",
            "currency": "KZT", "siteHost": "ozon.kz",
        }]
        self.assertEqual(ozon_site_list.resolve_site(sites, "俄罗斯")[0]["siteId"], 1)
        self.assertEqual(ozon_site_list.resolve_site(sites, "ru")[0]["currency"], "RUB")
        self.assertEqual(ozon_site_list.resolve_site(sites, "哈萨克斯坦")[0]["siteId"], 2)

    def test_response_contracts_and_encoding(self):
        search = {"code": 0, "data": {"total": 1, "list": [{}], "site": {"siteId": 1}}}
        self.assertEqual(validate_search_response(search, "失败"), search)
        detail = {
            "code": 0,
            "data": {"goods": {}, "history": [], "skus": [], "site": {"siteId": 1}},
        }
        self.assertEqual(validate_object_response(detail, "goods", "失败"), detail)
        self.assertEqual(
            build_url("https://example.test/", "/search", [("keyword", "wireless mouse")]),
            "https://example.test/search?keyword=wireless+mouse",
        )


if __name__ == "__main__":
    unittest.main()
