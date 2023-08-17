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
        page_num = response.url
        # Extract job details from the search page
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
            for job in jobs_list:
                if job.get('adBlob') is None:
                    job_link = 'https://za.indeed.com' + job.get('link', np.nan)
                    self.random_delay()  # Add random delay between requests
                    yield scrapy.Request(url=job_link,
                                        callback=self.parse_job,
                                        meta=self.get_request_meta(job, page_num))
        
        # Follow the next page button if available
        next_button = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
        if next_button:
            self.random_delay()  # Add random delay between requests
            yield response.follow('https://za.indeed.com' + next_button, callback=self.parse)

    def parse_job(self, response):
        # Extract job details from the job listing page
        yield {
            'page_url': response.meta['page_url'],
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
            'salary_from_job_link' : response.css('div.css-gle1f1.e1xnxm2i0 div.css-tvvxwd.ecydgvn1::text').get(default=np.nan),
            'job_type_from_job_link' : response.css('div.css-m539th.eu4oa1w0 div.css-tvvxwd.ecydgvn1::text').get(default=np.nan),
            'pub_date': response.meta['pub_date'],
            'job_description': response.css('div#jobDescriptionText').getall(),
        }

    def get_request_meta(self, job, page_num):
        return {
            'job_id': job.get('jobkey', np.nan),
            'company': job.get('company', np.nan),
            'company_rating': job.get('companyRating', np.nan),
            'company_review_count': job.get('companyReviewCount', np.nan),
            'display_title': job.get('displayTitle', np.nan),
            'relative_time': job.get('formattedRelativeTime', np.nan),
            'jobLocationCity': job.get('jobLocationCity', np.nan),
            'jobLocationState' : job.get('jobLocationState', np.nan),
            'formatted_location': job.get('formattedLocation', np.nan),
            'extracted_salary': job.get('extractedSalary', np.nan),
            'job_types': job.get('jobTypes', np.nan),
            'job_link': 'https://za.indeed.com' + job.get('link', np.nan),
            'pub_date': job.get('pubDate', np.nan),
            'page_url': page_num
        }

    def random_delay(self):
        delay = randint(0, 6)
        time.sleep(delay)
