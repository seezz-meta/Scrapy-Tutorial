import re
import json
import time
import scrapy
import numpy as np
from random import randint

class IndeedjobsSpider(scrapy.Spider):
    name = "indeedjobs"
    allowed_domains = ["za.indeed.com"]
    start_urls = ["https://za.indeed.com/jobs?q=Data+Analytics&l=South+Africa&sort=date"]

    def parse(self, response):
        print(response.url)
        # Extract job details from the search page
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
            for job in jobs_list:
                if job.get('adBlob') is None:
                    job_link = 'https://za.indeed.com' + job['link']
                    extracted_salary = job.get('extractedSalary', np.nan)
                    self.random_delay()  # Add random delay between requests
                    yield scrapy.Request(url=job_link,
                                        callback=self.parse_job,
                                        meta=self.get_request_meta(job, extracted_salary, page_num))
        
        # Follow the next page button if available
        next_button = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
        if next_button:
            self.random_delay()  # Add random delay between requests
            yield scrapy.Request('https://za.indeed.com' + next_button, callback=self.parse)

    def parse_job(self, response):
        # Extract job details from the job listing page
        yield {
            'job_id': response.meta['job_id'],
            'company': response.meta['company'],
            'company_rating': response.meta['company_rating'],
            'company_review_count': response.meta['company_review_count'],
            'display_title': response.meta['display_title'],
            'relative_time': response.meta['relative_time'],
            'job_location_city' : response.meta['jobLocationCity'],
            'job_location_state' : response.meta['jobLocationState'],
            'formatted_location': response.meta['formatted_location'],
            'extracted_salary': response.meta['extracted_salary'],
            'job_types': response.meta['job_types'],
            'job_link': response.meta['job_link'],
            'pub_date': response.meta['pub_date'],
            'job_description': response.css('div#jobDescriptionText').getall()
        }

    def get_request_meta(self, job, extracted_salary):
        return {
            'job_id': job['jobkey'],
            'company': job['company'],
            'company_rating': job['companyRating'],
            'company_review_count': job['companyReviewCount'],
            'display_title': job['displayTitle'],
            'relative_time': job['formattedRelativeTime'],
            'jobLocationCity': job['jobLocationCity'],
            'jobLocationState' : job['jobLocationState'],
            'formatted_location': job['formattedLocation'],
            'extracted_salary': extracted_salary,
            'job_types': job['jobTypes'],
            'job_link': 'https://za.indeed.com' + job['link'],
            'pub_date': job['pubDate'],
        }

    def random_delay(self):
        delay = randint(0, 6)
        time.sleep(delay)