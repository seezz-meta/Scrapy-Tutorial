import scrapy
import time
from random import randint

class PnetjobsSpider(scrapy.Spider):
    name = "pnetjobs"
    allowed_domains = ["www.pnet.co.za"]
    start_urls = ["https://www.pnet.co.za/jobs/data-analyst?page=100"]

    def parse(self, response):
        jobs_links = response.css('article a.res-v1ywpt::attr(href)').getall()
        if len(jobs_links) > 0:
            for job in jobs_links:
                job_url =  'https://www.pnet.co.za' + job
                self.random_delay()
                yield scrapy.Request(job_url, callback=self.parse_job, meta={'url': job_url, 'page_link' : response.css('li.res-k9shkt a.res-wkn4mv::attr(href)').get()})

        next_button = response.css('ul.res-lfh80t li.res-k9shkt:last-child a::attr(href)').get()
        if next_button is not None:
            self.random_delay()
            yield scrapy.Request(next_button, callback=self.parse)


    def parse_job(self, response):
        company = response.css('a.listing-content-provider-1mru2ru::text').get()
        if not company:
            company = response.css('a.at-listing-nav-company-name-link::text').get()

        display_title = response.css('span.listing-content-provider-ve1ux::text').get()
        if not display_title:
            display_title = response.css('h1.at-listing-nav-listing-title::text').get()

        location = response.css('li.at-listing__list-icons_location span.listing-content-provider-ceirlr::text').get()
        if not location:
            location = response.css('li.listing-list.at-listing__list-icons_location span:not(.iconic)::text').get()

        contract_types = response.css('li.listing-content-provider-92djlq.at-listing__list-icons_contract-type span.listing-content-provider-ceirlr::text').get()
        if not contract_types:
            contract_types = response.css('li.at-listing__list-icons_contract-type::text').getall()
        job_type = response.css('li.at-listing__list-icons_work-type span.listing-content-provider-ceirlr::text').get()
        if not job_type:
            job_type = response.css('li.at-listing__list-icons_work-type::text').getall()

        published_date = response.css('li.at-listing__list-icons_date span.listing-content-provider-ceirlr::text').get()
        if not published_date:
            published_date = response.css('li.listing-list.at-listing__list-icons_date span.date-time-ago::attr(data-date)').get()

        salary = response.css('li.at-listing__list-icons_salary span.listing-content-provider-ceirlr::text').get()
        if not salary:
            salary = response.css('li.at-listing__list-icons_salary::text').getall()

        eeaa = response.css('li.at-listing__list-icons_eeaa span.listing-content-provider-ceirlr::text').get()
        if not eeaa:
            eeaa = response.css('li.listing-list.at-listing__list-icons_eeaa::text').getall()

        description = response.css('article.listing-content-provider-1ond6j9').getall()
        if not description:
            description = response.css('div.listing__main-content').getall()

        yield {
            'company': company,
            'display_title': display_title,
            'location': location,
            'contract_types': contract_types,
            'job_type': job_type,
            'job_link': response.meta['url'],
            'published_date': published_date,
            'salary': salary,
            'eeaa': eeaa,
            'description': description,
            'page_num' : response.meta['page_link'],
        }

    def random_delay(self):
        delay = randint(0, 6)
        time.sleep(delay)