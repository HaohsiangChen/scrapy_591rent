# -*- coding: utf-8 -*-
import logging
import scrapy
import json
from ajilog import logger
from spider591.items import Rent591Item
from w3lib.html import remove_tags
from datetime import datetime

class Rent591CrawlerSpider(scrapy.Spider):

    name = 'rent_591_crawler'
    except_msg = []
    rec_per_page = 30

    def start_requests(self):
        yield scrapy.Request(
            'https://rent.591.com.tw/?kind=0&region=1',
            callback=self.gen_token
        )

    def gen_token(self, response):
        self.csrf = response.css('meta[name="csrf-token"]').xpath('@content').extract_first()
        for cookie in response.headers.getlist('Set-Cookie'):
            cookie_tokens = cookie.decode('utf-8').split('; ')
            if cookie_tokens and cookie_tokens[0].startswith('591_new_session='):
                self.session_token = cookie_tokens[0].split('=')[1]
                break
        cities = {
            '台北市': 1,
            '新北市': 3
            #'花蓮市' : 23
            #'澎湖縣' : 24
        }
        for city_name, city_num in cities.items():
            req = scrapy.Request(
                url = f'https://rent.591.com.tw/home/search/rsList?region={city_num}',
                headers = {
                    'Cookie': '591_new_session={};'.format(
                        self.session_token
                    ),
                    'X-CSRF-TOKEN': self.csrf
                },
                cookies = {'urlJumpIp': city_num},
                callback = self.gen_rent_list)

            req.meta['city_name'] = city_name
            req.meta['city_num'] = city_num
            yield req

    def gen_rent_list(self, response):
        data = json.loads(response.body_as_unicode())
        total_records = int(data['records'].replace(',', ''))
        pages = total_records // self.rec_per_page + 1
        city_num = response.meta['city_num']
        city_name = response.meta['city_name']

        for page in range(pages):
            req = scrapy.Request(
                url = f'https://rent.591.com.tw/home/search/rsList?region={city_num}&firstRow={page * 30}',
                headers = {
                    'Cookie': '591_new_session={};'.format(self.session_token),
                    'X-CSRF-TOKEN': self.csrf
                },
                cookies = {'urlJumpIp': city_num},
                callback = self.gen_rent_detail)

            req.meta['city_name'] = city_name
            req.meta['city_num'] = city_num
            yield req

    def gen_rent_detail(self, response):
        data = json.loads(response.body_as_unicode())
        for info in data['data']['data']:
            house_id = info['houseid']
            req = scrapy.Request(
                url = f'https://rent.591.com.tw/rent-detail-{house_id}.html',
                callback = self.get_rent_detail
            )

            if 'boy' in info['condition']:
                req.meta['sex_limited'] = 1
            elif 'girl' in info['condition']:
                req.meta['sex_limited'] = 2
            else:
                req.meta['sex_limited'] = 0
            req.meta['house_id'] = house_id
            req.meta['city_name'] = response.meta['city_name']
            req.meta['owner'] = info['linkman']
            req.meta['owner_sex'] = 1 if '先生' in info['linkman'] else 2
            req.meta['owner_type'] = info['nick_name'].split()[0]
            req.meta['price'] = int(info['price'].replace(',', ''))

            yield req

    def get_rent_detail(self, response):
        try:
            item = Rent591Item()
            detail = response.xpath('//div[@class="detailInfo clearfix"]//li')
            item['house_type'] = ''
            item['house_status'] = ''
            item['phone_number'] = ''
            for d in detail:
                det = remove_tags(''.join(d.get().split())).split(':')
                if det[0] == '型態':
                    item['house_type'] = det[1]
                elif det[0] == '現況':
                    item['house_status'] = det[1]

            item['datetime'] = datetime.now()
            item['house_id'] = response.meta['house_id']
            item['city_name'] = response.meta['city_name']
            item['price'] = response.meta['price']
            item['sex_limited'] = response.meta['sex_limited']
            item['phone_number'] = response.xpath('//span[@class="dialPhoneNum"]').xpath('@data-value').extract_first()
            if item['phone_number'] == '':
                item['phone_number'] = response.xpath('//div[@class="hidtel"]/text()').extract_first()
            item['owner'] = response.meta['owner']
            item['owner_type'] = response.meta['owner_type']
            item['owner_sex'] = response.meta['owner_sex']

            yield item

        except Exception as e:
            self.except_msg.append({
                'house_id': response.meta['house_id'],
                'message': str(e)
            })
        finally:
            logging.debug(self.except_msg)