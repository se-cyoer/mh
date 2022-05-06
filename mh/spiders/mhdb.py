import scrapy
from mh.items import ManhuaItem
from scrapy_splash import SplashRequest

script = '''
function main(splash,args)
    assert(splash:go(args.url))
    assert(splash:wait(0.5))
    return splash:html()
end
 '''


class MhdbSpider(scrapy.Spider):
    name = 'mhdb'
    # allowed_domains = ['www.manhuadb.com']
    start_urls = ['http://www.manhuadb.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={'lua_source': script}, endpoint='execute')

    def parse(self, response):
        cartoon = response.css(
            'div[class="col-2 col-sm-1 px-1"]')
        for i in cartoon:
            items = ManhuaItem()
            url = i.css('a::attr(href)').get()
            url = response.urljoin(url)
            items['cartoon_type'] = i.css('a::text').get()
            items['cartoon_url'] = url
            request = SplashRequest(
                url=url, callback=self.next_parse, args={'lua_source': script}, endpoint='execute',
                meta={'item': items})
            # yield items
            if url:
                yield request

    def next_parse(self, response):
        reslut = response.css(
            'div[class="media comic-book-unit"]')
        for i in reslut:
            item = response.meta['item']
            url = response.urljoin(
                i.css('h2[class="h3 my-0"]>a::attr(href)').get())
            item['next_name'] = i.css('h2[class="h3 my-0"]>a::text').get()
            item['serialize'] = i.css(
                'span[class="badge badge-success"]::text').get()
            item['sub_type'] = str(i.css('span[class="badge badge-info"]::text').get(
            )) + ' ' + str(i.css('span[class="badge badge-warning"]::text').get())
            item['next_book_url'] = url
            item['next_image_url'] = i.css(
                'a[class="d-block"]>img::attr(src)').get()
            if url:
                yield SplashRequest(url=url, callback=self.read_mh, args={'lua_source': script}, endpoint='execute',
                                    meta={'item': item})

    def read_mh(self, response):
        item = response.meta['item']
        item['describe'] = response.css('p[class="comic_story"]::text').get()
        url = response.urljoin(response.css(
            'div[class="actions"]>a::attr(href)').get())
        item['book_url'] = url
        if url:
            yield SplashRequest(url=url, callback=self.browser_parse, args={'lua_source': script}, endpoint='execute',
                                meta={'item': item})

    def browser_parse(self, response):
        item = response.meta['item']
        url = response.css(
            'div[class="text-center pjax-container"]>img::attr(src)').get()
        item['image_url'] = url
        yield item
