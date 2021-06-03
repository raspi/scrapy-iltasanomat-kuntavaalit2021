import scrapy

from kuntavaalit.items import *


class SiteSpider(scrapy.Spider):
    allowed_domains = [
        'www.vaalikone.fi',
    ]
    start_urls = [
        'https://www.vaalikone.fi/kunta2021/api/districts',
    ]

    def parse(self, response: scrapy.http.Response):
        raise NotImplemented

    def load_questions(self, response: scrapy.http.TextResponse):
        yield Question(
            url=response.url,
            data=response.json(),
            municipalityid=response.meta['_id'],
        )

    def load_candidates(self, response: scrapy.http.TextResponse):
        for i in response.json():
            if '_id' in response.meta and response.meta['_id'] != i['districtId']:
                continue

            yield scrapy.Request(
                f"https://www.vaalikone.fi/kunta2021/api/candidates/{i['id']}",
                callback=self.load_candidate,
            )

    def load_candidate(self, response: scrapy.http.TextResponse):
        data = response.json()
        yield Candidate(
            url=response.url,
            data=response.json(),
            municipalityid=data['district']['id'],
            id=data['id'],
        )

    def load_parties(self, response: scrapy.http.TextResponse):
        yield Party(
            url=response.url,
            data=response.json(),
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
        found: bool = False
        for i in response.json():
            if str(i['id']) == self.id:
                found = True
                break

        if not found:
            raise ValueError(f"id {self.id} not found")

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties"),
            callback=self.load_parties,
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/themes-with-questions/is/{self.id}"),
            callback=self.load_questions,
            meta={
                '_id': int(self.id),
            },
        )

        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/candidates"),
            callback=self.load_candidates,
            meta={
                '_id': int(self.id),
            },
        )


class KVSpider(SiteSpider):
    """
    Fetch all
    """

    name = 'kaikki'

    def parse(self, response: scrapy.http.TextResponse):
        yield scrapy.Request(
            response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/parties"),
            callback=self.load_parties,
        )

        for i in response.json():
            yield scrapy.Request(
                response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/themes-with-questions/is/{i['id']}"),
                callback=self.load_questions,
                meta={
                    '_id': int(i['id']),
                },
            )

            yield scrapy.Request(
                response.urljoin(f"https://www.vaalikone.fi/kunta2021/api/candidates"),
                callback=self.load_candidates,
            )
