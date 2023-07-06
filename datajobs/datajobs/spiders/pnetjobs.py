import scrapy


class PnetjobsSpider(scrapy.Spider):
    name = "pnetjobs"
    allowed_domains = ["www.pnet.co.za"]
    start_urls = ["https://www.pnet.co.za/jobs/data-analyst/in-south-africa"]

    def parse(self, response):
        jobs = response.css('.res-rqk8n8')
        print(jobs)
        # for job in jobs:
        #     relative_url = job.css('.res-197as6q a::attr(href)').get()
        #     print(relative_url)

