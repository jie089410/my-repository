# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy_redis.spiders import RedisSpider
# 设置编码的终极方式
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from Sina.items import SinaItem


class SinaSpider(RedisSpider):
    name = 'sina'
    redis_key = "sinaspider:start_urls"
    # allowed_domains = ['sina.com.cn']
    # start_urls = ["http://news.sina.com.cn/guide/"]
    # 国内 http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=100&tag=1&format=json&page=1
    # 国际 http://news.sina.com.cn/world/
    # 社会 http://news.sina.com.cn/society/

    # 动态获取域范围
    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(SinaSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        # 将返回的json数据转换成python对象
        js = json.loads(response.body)
        # 取出键为result的值
        result = js['result']
        for article in result['data']:
            item = SinaItem()
            item['article_urls'] = article['url']
            request = scrapy.Request(url=item['article_urls'], meta={'meta_article': item}, callback=self.article_parse,
                                     dont_filter=True)
            request.meta["PhantomJs"] = True
            yield request

    def article_parse(self, response):
        # 提取response的元数据，即item对象
        item = response.meta['meta_article']

        # 制定规则提取文章内容
        title = response.xpath("//h1[@class='main-title']/text()").extract()
        content_list = response.xpath("//div[@class='article']/p/text()").extract()
        pub_time = response.xpath("//span[@class='date']/text()").extract()
        total_num = response.xpath("//span[@class='num']/text()").extract()
        # 将p标签的内容合并在一起
        content = "".join(content_list)
        item['title'] = title[0] if len(title) > 0 else "NULL"
        item['pub_time'] = pub_time[0] if len(pub_time) > 0 else "NULL"
        item['total_num'] = total_num[0] if len(total_num) > 0 else "NULL"
        item['content'] = content

        # 制定评论详情页的规则，提取评论详情页的url
        # //a[contains(@href,'group=0')]/@href
        comment_url = response.xpath("//a[contains(@href,'group=0')]/@href").extract()
        # 有少量新闻评论加载时在新闻页插件加载的，需要剔除出去

        if len(comment_url) > 0 and comment_url[0].startswith("http"):
            item['comment_url'] = comment_url[0]
        else:
            item['comment_url'] = "NULL"

        # 发送请求到每个帖子的评论页
        if item['comment_url'] != "NULL":
            # 制定规则爬取每篇评论，需利用phantomjs+selenium自动加载更多评论

            request = scrapy.Request(url=item['comment_url'], meta={'meta_final': item}, callback=self.comment_parse, \
                                     dont_filter=True)
            request.meta['PhantomJs'] = True
            yield request
        else:
            item['comments'] = "NULL"
            yield item

    def comment_parse(self, response):
        # 提取response的元数据，即item对象
        # print "#" * 20
        item = response.meta['meta_final']
        comments = []
        # 找出最新评论所在父级节点
        nodes = response.xpath("//div[@class='latest-wrap']//div[@class='item clearfix']")
        for node in nodes:
            comment = {}
            # 用户名
            username = node.xpath(".//div[@class='head']/a/@title").extract()
            comment["username"] = username[0] if len(username) > 0 else "NULL"
            # 用户所在地区
            user_location = node.xpath(".//span[@class='area']/text()").extract()
            comment["user_location"] = user_location[0] if len(user_location) > 0 else "NULL"
            # 评论时刻
            comment_time = node.xpath(".//span[@class='time']/text()").extract()
            comment['comment_time'] = comment_time[0] if len(comment_time) > 0 else "NULL"
            # 评论内容
            user_comment = node.xpath(".//div[@class='txt']/text()").extract()
            comment["user_comment"] = user_comment[0] if len(user_comment) > 0 else "NULL"

            comments.append(comment)
        item['comments'] = comments
        yield item





