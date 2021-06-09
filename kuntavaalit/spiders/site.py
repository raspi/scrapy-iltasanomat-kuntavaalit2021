from typing import List
from urllib.parse import urlsplit, SplitResult

import scrapy

from kuntavaalit.items import *


class SiteSpider(scrapy.Spider):
    allowed_domains: list = [
        'www.vaalikone.fi',
    ]

    start_urls: list = [
        'https://www.vaalikone.fi/kunta2021/api/districts',
    ]

    brands: List[str] = [
        'hs',  # Helsingin Sanomat
        'is',  # Ilta-Sanomat
        'sk',  # Satakunnan Kansa
        'al',  # Aamulehti
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplemented

    def load_questions(self, response: scrapy.http.TextResponse):
        data = response.json()

        url: SplitResult = urlsplit(response.url)
        p: List[str] = url.path.strip('/').split('/')
        municipalityid: int = int(p[4])
        brand: str = p[3]

        yield Question(
            url=response.url,
            data=data,
            municipalityid=municipalityid,
            brandname=brand,
        )

    def load_candidates(self, response: scrapy.http.TextResponse):
        for i in response.json():
            if '_id' in response.meta and response.meta['_id'] != i['districtId']:
                # Fetch only from single municipality
                continue

            yield scrapy.Request(
                f"https://www.vaalikone.fi/kunta2021/api/candidates/{i['id']}",
                callback=self.load_candidate,
            )

    def load_candidate(self, response: scrapy.http.TextResponse):
        data = response.json()
        yield Candidate(
            url=response.url,
            data=data,
            municipalityid=data['district']['id'],
            id=data['id'],
        )

    def load_parties(self, response: scrapy.http.TextResponse):
        yield Party(
            url=response.url,
            data=response.json(),
        )

    def load_parties_alliances(self, response: scrapy.http.TextResponse):
        url: SplitResult = urlsplit(response.url)
        p: List[str] = url.path.strip('/').split('/')
        municipalityid: int = int(p[4])

        yield PartyAlliance(
            url=response.url,
            data=response.json(),
            municipalityid=municipalityid,
        )


class KuntaSpider(SiteSpider):
    """
    Fetch all from municipality X
    """

    name = 'kunta'
    id: str = ""

    def __init__(self, id: str = ""):
        if id == "":
            id = None

        if id is None:
            raise ValueError("no id")

        self.id = id

    def parse(self, response: scrapy.http.TextResponse):
        data = response.json()
        found: bool = False
        for i in data:
            if str(i['id']) == self.id:
                found = True
                break

        if not found:
            raise ValueError(f"id {self.id} not found")

        yield Municipality(
            url=response.url,
            data=data,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties"),
            callback=self.load_parties,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties/alliances/{self.id}"),
            callback=self.load_parties_alliances,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/candidates"),
            callback=self.load_candidates,
            meta={
                '_id': int(self.id),
            },
        )

        for brand in self.brands:
            yield scrapy.Request(
                response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/themes-with-questions/{brand}/{self.id}"),
                callback=self.load_questions,
            )


class KVSpider(SiteSpider):
    """
    Fetch all
    """

    name = 'kaikki'

    def parse(self, response: scrapy.http.TextResponse):
        data = response.json()

        yield Municipality(
            url=response.url,
            data=data,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties"),
            callback=self.load_parties,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/candidates"),
            callback=self.load_candidates,
        )

        for i in data:
            yield scrapy.Request(
                response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties/alliances/{i['id']}"),
                callback=self.load_parties_alliances,
            )

            for brand in self.brands:
                yield scrapy.Request(
                    response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/themes-with-questions/{brand}/{i['id']}"),
                    callback=self.load_questions,
                )
