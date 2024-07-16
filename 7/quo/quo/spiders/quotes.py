import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    max_count_follow = 1

    def parse(self, response):
        quotes = response.xpath('//div[contains(@class, "row")]/div[contains(@class, "col-md-8")]'
                                '/div[contains(@class, "quote")]')
        for quote in quotes:
            text_xpath = './/span[contains(@class, "text")]/text()'
            text = quote.xpath(text_xpath).get()
            author_xpath = './/span/small[contains(@class, "author")]/text()'
            author = quote.xpath(author_xpath).get()

            yield {
                'text': text,
                'author': author
            }

        next_page_btn = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page_btn and self.max_count_follow:
            self.max_count_follow -= 1
            yield response.follow(next_page_btn, callback=self.parse)
