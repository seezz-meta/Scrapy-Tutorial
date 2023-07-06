import re
import json
import scrapy
import numpy as np

class IndeedjobsSpider(scrapy.Spider):
    name = "indeedjobs"
    allowed_domains = ["za.indeed.com"]
    start_urls = ["https://za.indeed.com/jobs?q=Data+Analytics&l=South+Africa"]

    def parse(self, response):
        # Extract job details from the search page
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        json_blob = json.loads(script_tag[0])
        jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
        for job in jobs_list:
            job_link = 'https://za.indeed.com' + job['link']
            extracted_salary = job.get('extractedSalary', np.nan)

            yield scrapy.Request(url=job_link,
                                 callback=self.parse_job,
                                 meta={
                                     'job_id': job['jobkey'],
                                     'company': job['company'],
                                     'company_id': job['companyIdEncrypted'],
                                     'company_rating': job['companyRating'],
                                     'company_review_count': job['companyReviewCount'],
                                     'display_title': job['displayTitle'],
                                     'relative_time': job['formattedRelativeTime'],
                                     'location_city': job['formattedLocation'],
                                     'extracted_salary': extracted_salary,
                                     'job_types': job['jobTypes'],
                                     'job_link': job_link,
                                     'pub_date': job['pubDate'],
                                 })
        
        # Follow the next page button if available
        next_button = response.css('a[data-testid="pagination-page-next"]::attr(href)').get()
        if next_button:
            yield response.follow(next_button, callback=self.parse)

    def parse_job(self, response):
        # Extract job details from the job listing page
        yield {
            'job_id': response.meta['job_id'],
            'company': response.meta['company'],
            'company_id': response.meta['company_id'],
            'company_rating': response.meta['company_rating'],
            'company_review_count': response.meta['company_review_count'],
            'display_title': response.meta['display_title'],
            'relative_time': response.meta['relative_time'],
            'location_city': response.meta['location_city'],
            'extracted_salary': response.meta['extracted_salary'],
            'job_types': response.meta['job_types'],
            'job_link': response.meta['job_link'],
            'pub_date': response.meta['pub_date'],
            'job_description': response.css('div#jobDescriptionText').getall()
        }
