# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from settings import USER_AGENTS
from selenium import webdriver
from lxml import etree
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from scrapy.contrib.downloadermiddleware.httpproxy import HttpProxyMiddleware
import signal
import random
import time
import requests
import base64
import scrapy


# User-Agent 下载中间件
class RandomUserAgent(object):
    def __init__(self):
        # 初始化User-Agent'
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) \
        Chrome/22.0.1207.1 Safari/537.1"

    def process_request(self, request, spider):
        # 随机选中User-Agent
        self.user_agent = random.choice(USER_AGENTS)
        request.headers.setdefault('User-Agent', self.user_agent)


# ip_port 下载中间件
class RandomProxy(object):
    def __init__(self):
        self.proxy_auth = ""
        self.proxy_api = "http://dps.kuaidaili.com/api/getdps/?orderid=958655825381063&num=50&ut=1&sep=3"
        # 返回的时代理ip:port列表
        self.proxy_list = requests.get(self.proxy_api).text.split()

    def process_request(self, request, spider):
        proxy = random.choice(self.proxy_list)
        base64_userpass = base64.b64encode(self.proxy_auth)
        request.meta['proxy'] = "http://" + proxy
        # if self.proxy_auth != None:
        request.headers['Proxy-Authorization'] = "Basic " + base64_userpass


# article PhantomJs中间件
class ArticlePhantomJsMiddleware(object):
    def process_request(self, request, spider):
        if request.meta.has_key('PhantomJs'):
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            # 睡眠1.5秒等待PhantomJs加载资源
            time.sleep(1.5)
            body = driver.page_source
            url = driver.current_url
            # driver.service.process.send_signal(signal.SIGTERM)
            # 不使用driver.quit防止出现double free，即释放两次资源
            driver.close()
            return scrapy.http.HtmlResponse(url, body=body, request=request, encoding='utf-8')


# comment PhantomJs中间件
class CommentPhantomJsMiddleware(object):
    def process_request(self, request, spider):
        if request.meta.has_key('PhantomJs'):
            driver = webdriver.PhantomJS()
            # 注意可能有的帖子无评论
            driver.get(request.url)
            time.sleep(0.5)
            selector = etree.HTML(driver.page_source)
            # 循环退出条件：当页面加载更多的a标签不存在时
            while selector.xpath("//div[@class='more']/a"):
                selector = etree.HTML(driver.page_source)
                # 一直点击加载更多
                driver.find_element_by_class_name("more").click()

            body = driver.page_source
            url = driver.current_url
            # 解决driver.quit出现错误
            driver.service.process.send_signal(signal.SIGTERM)
            driver.quit()
            # 返回处理后请求响应
            return scrapy.http.HtmlResponse(url, body=body, request=request, encoding='utf-8')



