# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.parse import urlencode
from ..configs import API_KEY

API_KEY = "5489bb46717bb979378a0475db1e0d69"


def get_url(url):
    payload = {
        "api_key": API_KEY,
        "url": url,
    }
    proxy_url = "http://api.scraperapi.com/?" + urlencode(payload)
    return proxy_url


def queryencode(params):
    """Encodes first request to google patents to extract number of the first patent
    """
    url = "https://patents.google.com/xhr/query?url={}&exp=&"
    q = [f"{k}%3D{v}" for (k, v) in params.items()]
    return url.format("%26".join(q))


class PatentsSpider(scrapy.Spider):
    name = "fast_crawler"
    allowed_domains = ["api.scraperapi.com"]

    def url_params(self, page=0):
        params = {"q": self.keyword, "language": "ENGLISH", "num": 100, "page": page}
        return params

    def start_requests(self):
        url = queryencode(self.url_params())

        yield scrapy.Request(
            get_url(url),
            callback=self.parse,
            dont_filter=True,
            meta={"page": 0, "total_num_pages": None},
        )

    def parse(self, response):
        print(response.url)
        responsejson = json.loads(response.text)
        page_num = response.meta["page"]
        if not response.meta["total_num_pages"]:
            total_num_pages = responsejson["results"]["total_num_pages"]
        else:
            total_num_pages = response.meta["total_num_pages"]
        for res in responsejson["results"]["cluster"][0]["result"]:
            try:
                title = res["patent"].get("title")
                patent_code = res["patent"].get("publication_number")
                link = f"https://patents.google.com/patent/{patent_code}/"
                inventors = res["patent"].get("inventor")
                assignee = res["patent"].get("assignee")
                priority_date = res["patent"].get("priority_date")
                filing_date = res["patent"].get("filing_date")
                publication_date = res["patent"].get("publication_date")
                item = {
                    "title": title,
                    "link": link,
                    "publication_number": patent_code,
                    "inventors": inventors,
                    "assignee": assignee,
                    "priority_date": priority_date,
                    "filing_date": filing_date,
                    "publication_date": publication_date,
                }
                yield item
            except:
                continue
        if page_num < total_num_pages:
            page_num += 1
            url = queryencode(self.url_params(page=page_num))
            yield scrapy.Request(
                get_url(url),
                callback=self.parse,
                dont_filter=True,
                meta={"page": page_num, "total_num_pages": total_num_pages},
            )
