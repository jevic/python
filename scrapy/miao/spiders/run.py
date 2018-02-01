# coding:utf-8
import scrapy
from scrapy import Selector
from scrapy import Request
from miao.items import MiaoItem

class NgaSpider(scrapy.Spider):
    name = "NgaSpider"
    host = "http://www.aboutyun.com/"
    # start_urls是我们准备爬的初始页
    start_urls = [
        "http://www.aboutyun.com/forum-143-1.html",
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            # 此处将起始url加入scrapy的待爬取队列，并指定解析函数
            # scrapy会自行调度，并访问该url然后把内容拿回来
            yield Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        selector = Selector(response)
        content_list = selector.xpath("//*[@class='s xst']")
        for content in content_list:
            topic = content.xpath('string(.)').extract_first()
            #print topic
            url = content.xpath('@href').extract_first()
            #print url
 	    item = MiaoItem()
 	    item['title'] = topic
            item['url'] = url
	    yield item
            # 此处，将解析出的帖子地址加入待爬取队列，并指定解析函数
            #yield Request(url=url, callback=self.parse_topic)

    def parse_topic(self, response):
       selector = Selector(response)
       content_list = selector.xpath("//*[@class='t_f']")
       for content in content_list:
           content = content.xpath('string(.)').extract_first()
           print content

#    def parse(self, response):
#        selector = Selector(response)
#        # 在此，xpath会将所有class=topic的标签提取出来，当然这是个list
#        # 这个list里的每一个元素都是我们要找的html标签
#        content_list = selector.xpath("//*[@class='s xst']")
#        # 遍历这个list，处理每一个标签
#        for content in content_list:
#            # 此处解析标签，提取出我们需要的帖子标题。
#            topic = content.xpath('string(.)').extract_first()
#            print topic
#            # 此处提取出帖子的url地址。
#            url = self.host + content.xpath('@href').extract_first()
#            print url
