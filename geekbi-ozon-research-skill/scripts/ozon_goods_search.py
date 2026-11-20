#!/usr/bin/env python3
"""调用极鲸云 Ozon 商品搜索接口。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import (
    DEFAULT_BASE_URL, build_url, parse_int, parse_number, parse_pairs,
    validate_page, validate_range_pairs, validate_search_response, validate_site, validate_sort,
)


ENDPOINT = "/api/v1/ozon/goods/ai-search"
BASE_PARAMS = {
    "keyword", "preset", "catId", "goodsId", "mallId", "skuId", "spuId", "offerId",
    "brandId", "brand", "salesLabel", "sellerType", "fulfillmentType", "dataSource",
    "entityMode", "analyticsWindowDays", "siteId", "page", "size", "sort", "order",
}
NUMERIC_RANGE_FIELDS = {
    "sold", "sales", "daySold", "weekSold", "monthSold", "daySales", "weekSales",
    "monthSales", "weekSoldRate", "price", "currentPrice", "originalPrice", "averagePrice",
    "minSellerPrice", "gmv", "averageGmv", "similarNum", "goodsScore", "reviewNum",
    "sellerOfferCount", "remainingStock", "stock", "inStockDays", "availabilityRate",
    "impressions", "searchImpressions", "totalViews", "sessions", "searchSessions",
    "pdpSessions", "cardViews", "searchViews", "pdpAddToCart", "clicks", "addToCart",
    "cardAddToCart", "searchAddToCart", "orders", "clickThroughRate", "addToCartRate",
    "cardAddToCartRate", "searchAddToCartRate", "pdpAddToCartRate", "conversionRate",
    "adCost", "adCostShare", "adDays", "promotionDiscount", "promotionDays",
    "promotionConversionRate", "promotionRevenueShare", "returnCount", "returnAmount",
    "returnRate", "redemptionRate", "outOfStockDays", "outOfStockShare", "lostRevenue",
    "packageLengthCm", "packageWidthCm", "packageHeightCm", "packageVolumeL",
    "packageWeightKg", "volumetricWeightKg", "deliveryDays", "averageDeliveryDays",
}
INTEGER_RANGE_FIELDS = {
    "sold", "daySold", "weekSold", "monthSold", "similarNum", "reviewNum",
    "sellerOfferCount", "remainingStock", "stock", "inStockDays", "impressions",
    "searchImpressions", "totalViews", "sessions", "searchSessions", "pdpSessions",
    "cardViews", "searchViews", "pdpAddToCart", "clicks", "addToCart", "cardAddToCart",
    "searchAddToCart", "orders", "adDays", "promotionDays", "returnCount",
    "outOfStockDays", "deliveryDays",
}
DATE_RANGE_FIELDS = {"onSaleTime", "discoveredAt", "updateTime", "mallOpenTime"}
ALLOWED_PARAMS = BASE_PARAMS | {
    f"{field}{suffix}"
    for field in NUMERIC_RANGE_FIELDS | DATE_RANGE_FIELDS
    for suffix in ("Min", "Max")
}
SORT_FIELDS = {
    "updateTime", "observedAt", "sold", "sales", "totalSold", "totalSales",
    "minPrice", "maxPrice", "currentPrice", "originalPrice", "marketingPrice",
    "discountPrice", "averagePrice", "minSellerPrice", "goodsScore", "reviewNum",
    "skuReviewNum", "stock", "remainingStock", "warehouseStock", "sellerStock",
    "fboStock", "fbsStock", "crossBorderStock", "retailStock", "inStockDays",
    "daySold", "weekSold", "monthSold", "daySales", "weekSales", "monthSales",
    "daySoldRate", "weekSoldRate", "monthSoldRate", "similarNum", "sellerOfferCount",
    "offerMinPrice", "offerMaxPrice", "clickThroughRate", "addToCartRate",
    "cardAddToCartRate", "searchAddToCartRate", "pdpAddToCartRate", "onSaleTime",
    "mallOpenTime", "impressions", "sessions", "searchSessions", "pdpSessions",
    "cardViews", "searchViews", "clicks", "addToCart", "pdpAddToCart", "orders",
    "conversionRate", "adCost", "adCostShare", "adDays", "promotionDiscount",
    "promotionDays", "promotionConversionRate", "returnCount", "returnAmount",
    "returnRate", "outOfStockDays", "outOfStockShare", "lostRevenue", "gmv",
    "averageGmv", "availabilityRate", "packageLengthCm", "packageWidthCm",
    "packageHeightCm", "packageVolumeL", "packageWeightKg", "volumetricWeightKg",
    "deliveryDays", "averageDeliveryDays", "discoveredAt", "detailUpdatedAt",
    "commentUpdatedAt", "featureUpdatedAt", "offSaleTime",
}
PRESETS = {"new", "hot", "five-star", "rising"}
ENTITY_MODES = {"SKU", "SPU"}


def parse_params(raw_params):
    params, values = parse_pairs(raw_params, ALLOWED_PARAMS)
    validate_site(values)
    validate_page(values)
    validate_sort(values, SORT_FIELDS)
    validate_range_pairs(values, NUMERIC_RANGE_FIELDS, DATE_RANGE_FIELDS, INTEGER_RANGE_FIELDS)
    if "catId" in values:
        parse_int("catId", values["catId"], minimum=1)
    if "analyticsWindowDays" in values and parse_int(
        "analyticsWindowDays", values["analyticsWindowDays"]
    ) not in {7, 28}:
        raise ValueError("analyticsWindowDays 只支持 7 或 28")
    if "entityMode" in values and values["entityMode"].upper() not in ENTITY_MODES:
        raise ValueError("entityMode 只支持 SKU 或 SPU")
    if "preset" in values and values["preset"] not in PRESETS:
        raise ValueError("preset 不在当前支持的商品榜单中")
    for field in ("goodsScoreMin", "goodsScoreMax"):
        if field in values and not 0 <= parse_number(field, values[field]) <= 5:
            raise ValueError(f"{field} 必须在 0 到 5 之间")
    return params


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 商品并输出 JSON")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--param", action="append", default=[], help="查询条件，格式为 名称=值")
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = parse_params(args.param)
        payload = authenticated_json_request(
            build_url(args.base_url, ENDPOINT, params), args.base_url, args.timeout
        )
        payload = validate_search_response(payload, "Ozon 商品查询失败")
    except ActionRequired as error:
        print(json.dumps(error.public_payload(), ensure_ascii=False, indent=2))
        return 2
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        print(json.dumps({"error": True, "msg": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
