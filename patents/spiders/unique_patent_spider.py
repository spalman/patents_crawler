# -*- coding: utf-8 -*-
import scrapy
import requests
from urllib.parse import urlencode
from ..configs import API_KEY

# API_KEY = "5489bb46717bb979378a0475db1e0d69"


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
    name = "patents_crawler"
    allowed_domains = ["api.scraperapi.com"]

    def url_params(self, page=0):
        params = {"q": self.keyword, "language": "ENGLISH", "page": page, "num": 100}
        return params

    def start_requests(self):
        url = queryencode(self.url_params())
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
            },
            timeout=10,
        )
        r = response.json()
        total_num_pages = r["results"]["total_num_pages"]
        num_page = r["results"]["num_page"]
        while num_page < total_num_pages:
            for res in r["results"]["cluster"][0]["result"]:
                patent_number = res["patent"]["publication_number"]
                url = (
                    f"https://patents.google.com/patent/{patent_number}/en?"
                    + urlencode(self.url_params())
                )
                yield scrapy.Request(
                    get_url(url), callback=self.parse, dont_filter=True, meta={},
                )

            num_page += 1
            url = queryencode(self.url_params(page=num_page))
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
                },
                timeout=10,
            )
            r = response.json()

    def parse(self, response):
        print(response.url)

        title = response.xpath("//span[@itemprop='title']/text()").get()
        patent_code = response.xpath('//dd[@itemprop="publicationNumber"]/text()').get()
        link = f"https://patents.google.com/patent/{patent_code}/"
        inventors = response.xpath('//meta[@scheme="inventor"]/@content').getall()
        assignee = response.xpath('//meta[@scheme="assignee"]/@content').getall()
        current_status = response.xpath('//span[@itemprop="status"]/text()').get()
        expiration = response.xpath('//time[@itemprop="expiration"]/text()').get()
        priority_date = response.xpath('//time[@itemprop="priorityDate"]/text()').get()
        filing_date = response.xpath('//time[@itemprop="filingDate"]/text()').get()
        publication_date = response.xpath(
            '//time[@itemprop="publicationDate"]/text()'
        ).get()
        pdf_link = response.xpath('//a[@itemprop="pdfLink"]/@href').get()
        item = {
            "title": title,
            "link": link,
            "publication_number": patent_code,
            "inventors": inventors,
            "assignee": assignee,
            "current_status": current_status,
            "expiration": expiration,
            "priority_date": priority_date,
            "filing_date": filing_date,
            "publication_date": publication_date,
            "pdf_link": pdf_link,
        }
        yield item

