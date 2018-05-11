# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaItem(scrapy.Item):

    # 文章链接
    article_urls = scrapy.Field()
    # 文章标题内容
    title = scrapy.Field()
    # 文章发布时间
    pub_time = scrapy.Field()
    # 文章内容
    content = scrapy.Field()
    # 评论参与人数
    total_num = scrapy.Field()
    # 评论页链接
    comment_url = scrapy.Field()
    # 每篇文章的评论
    comments = scrapy.Field()
