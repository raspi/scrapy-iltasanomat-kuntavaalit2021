# scrapy-iltasanomat-kuntavaalit2021
Fetch all from [Iltasanomat Kuntavaalit 2021](https://www.vaalikone.fi/kunta2021/is) site

    scrapy crawl kaikki

Fetch single municipality (179=Jyväskylä): 

    scrapy crawl kunta -a id=179

## Requirements

* Python
* [Scrapy](https://scrapy.org/)
