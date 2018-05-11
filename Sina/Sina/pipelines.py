# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import signals
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class SinaPipeline(object):
    def process_item(self, item, spider):
        # son_urls = item['son_urls']
        # # 因为/会被当作文件夹分隔符
        # filename = son_urls[7:-6].replace('/', '-')
        # filename += '.txt'
        # with open(item['sub_filename'] + '/' + filename, 'w') as f:
        #     f.write(item['content'])
        return item
