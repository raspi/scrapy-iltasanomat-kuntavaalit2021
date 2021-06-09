# scrapy-sanoma-kuntavaalit2021

Fetch all from Sanoma kuntavaalit 2021 
[brands](https://www.sanoma.fi/mita-teemme/tuotteet-ja-brandit/) sites
(Helsingin sanomat, Ilta-sanomat, Satakunnan Kansa, Aamulehti)

    scrapy crawl kaikki

Fetch single municipality (179=Jyväskylä): 

    scrapy crawl kunta -a id=179

## Requirements

* Python
* [Scrapy](https://scrapy.org/)
