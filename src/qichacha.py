from collections import OrderedDict
from urllib import parse
from urllib.error import HTTPError

import openpyxl
import requests
from hyper.contrib import HTTP20Adapter
from lxml import etree


class Qichacha(object):

    def __init__(self, key):
        self.key = key

    def request(self, method, url, **kwargs):
        try:
            return requests.request(method, url, **kwargs)
        except HTTPError as error:
            print('HTTPError:', error)
        except ConnectionError as error:
            print('ConnectionError:', error)

    def get_html(self, url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
            'cookie': 'zg_did=%7B%22did%22%3A%20%22177b45ebe6d6f0-0eef23443e7ffc-a7f1a3e-e1000-177b45ebe6e90c%22%7D; UM_distinctid=177b45ebf00180-0ab0ac9158b72f-a7f1a3e-e1000-177b45ebf016d0; QCCSESSID=618urq0h8k0k834u6ai9c8cip1; CNZZDATA1254842228=561696775-1613634868-https%253A%252F%252Fwww.baidu.com%252F%7C1613980483; hasShow=1; acw_tc=1b13fa2116139868678788863ea322f5da2fb5b791cfd586a27bf3fb10; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201613987031949%2C%22updated%22%3A%201613987795083%2C%22info%22%3A%201613638844023%2C%22superProperty%22%3A%20%22%7B%5C%22%E5%BA%94%E7%94%A8%E5%90%8D%E7%A7%B0%5C%22%3A%20%5C%22%E4%BC%81%E6%9F%A5%E6%9F%A5%E7%BD%91%E7%AB%99%5C%22%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qcc.com%22%2C%22cuid%22%3A%20%22undefined%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%7D'
        }
        session = requests.session()
        result = parse.urlparse(url)
        prefix = result.scheme + '://' + result.netloc
        session.mount(prefix, HTTP20Adapter())
        response = session.request('get', url, headers=headers)
        response.encoding = 'utf-8'
        return response.text

    def search(self):
        url = 'https://www.qcc.com/web/search?key=%s' % self.key
        html = self.get_html(url)
        selector = etree.HTML(html)
        items = selector.xpath("//div[@class='maininfo']")
        companies = []
        for item in items:
            href = item.xpath("a[@class='title']/@href")
            status = item.xpath("span[@class='nstatus text-success']/text()")
            if href and status:
                status = status[0]
                if status == '存续' or status == '在业':
                    href = href[0]
                    company = self.get_detail(href)
                    companies.append(company)
        return companies

    def get_detail(self, url):
        html = self.get_html(url)
        selector = etree.HTML(html)
        company = OrderedDict()
        content = selector.xpath("//div[@class='content']")[0]
        company['name'] = content.xpath("//h1/text()")[0]
        ntable = selector.xpath("//table[@class='ntable']")[0]
        company['legalRepresentative'] = ntable.xpath("//h2[@class='seo font-20']/text()")[0].strip()
        company['registrationStatus'] = ntable.xpath("//td[text()='登记状态']/following-sibling::td[1]/text()")[0].strip()
        company['dateOfEstablishment'] = ntable.xpath("//td[text()='成立日期']/following-sibling::td[1]/text()")[
            0].strip()
        company['registeredCapital'] = ntable.xpath("//td[text()=' 注册资本 ']/following-sibling::td[1]/text()")[0].strip()
        company['paidInCapital'] = ntable.xpath("//td[text()=' 实缴资本 ']/following-sibling::td[1]/text()")[0].strip()
        company['dateOfApproval'] = ntable.xpath("//td[text()='核准日期']/following-sibling::td[1]/text()")[0].strip()
        company['creditCode'] = ntable.xpath("//td[text()='统一社会信用代码']/following-sibling::td[1]/text()")[0].strip()
        company['organizationCode'] = ntable.xpath("//td[text()='组织机构代码']/following-sibling::td[1]/text()")[0].strip()
        company['businessRegistrationNumber'] = ntable.xpath("//td[text()='工商注册号']/following-sibling::td[1]/text()")[
            0].strip()
        company['taxpayerIdentificationNumber'] = ntable.xpath("//td[text()='纳税人识别号']/following-sibling::td[1]/text()")[
            0].strip()
        company['importAndExportEnterpriseCode'] = ntable.xpath(
            "//td[text()='进出口企业代码']/following-sibling::td[1]/text()")[0].strip()
        company['industry'] = ntable.xpath("//td[text()='所属行业']/following-sibling::td[1]/text()")[0].strip()
        company['companyType'] = ntable.xpath("//td[text()='企业类型']/following-sibling::td[1]/text()")[0].strip()
        company['businessTerm'] = ntable.xpath(
            "//td[text()='\n                营业期限\n            ']/following-sibling::td[1]/text()")[0].strip()
        company['registrationAuthority'] = ntable.xpath("//td[text()='登记机关']/following-sibling::td[1]/text()")[
            0].strip()
        company['staffSize'] = ntable.xpath(
            "//td[text()='\n                人员规模\n            ']/following-sibling::td[1]/text()")[0].strip()
        company['numberOfInsured'] = ntable.xpath(
            "//td[text()='\n                参保人数\n            ']/following-sibling::td[1]/text()")[0].strip()
        company['region'] = ntable.xpath("//td[text()='所属地区']/following-sibling::td[1]/text()")[0].strip()
        company['nameUsedBefore'] = ntable.xpath(
            "//td[text()='\n                曾用名\n            ']/following-sibling::td[1]/text()")[0].strip()
        company['englishName'] = ntable.xpath("//td[text()='英文名']/following-sibling::td[1]/text()")[0].strip()
        company['businessAddress'] = ntable.xpath("//td[text()='企业地址']/following-sibling::td[1]/text()")[0].strip()
        company['businessScope'] = ntable.xpath("//td[text()='经营范围']/following-sibling::td[1]/text()")[0].strip()
        return company

    def start(self):
        companies = self.search()
        if companies:
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            worksheet.append([
                '企业',
                '法定代表人',
                '登记状态',
                '成立日期',
                '注册资本',
                '实缴资本',
                '核准日期',
                '统一社会信用代码',
                '组织机构代码',
                '工商注册号',
                '纳税人识别号',
                '进出口企业代码',
                '所属行业',
                '企业类型',
                '营业期限',
                '登记机关',
                '人员规模',
                '参保人数',
                '所属地区',
                '曾用名',
                '英文名',
                '企业地址',
                '经营范围'
            ])
            for company in companies:
                worksheet.append([
                    company['name'],
                    company['legalRepresentative'],
                    company['registrationStatus'],
                    company['dateOfEstablishment'],
                    company['registeredCapital'],
                    company['paidInCapital'],
                    company['dateOfApproval'],
                    company['creditCode'],
                    company['organizationCode'],
                    company['businessRegistrationNumber'],
                    company['taxpayerIdentificationNumber'],
                    company['importAndExportEnterpriseCode'],
                    company['industry'],
                    company['companyType'],
                    company['businessTerm'],
                    company['registrationAuthority'],
                    company['staffSize'],
                    company['numberOfInsured'],
                    company['region'],
                    company['nameUsedBefore'],
                    company['englishName'],
                    company['businessAddress'],
                    company['businessScope']
                ])
            workbook.save(self.key + '.xlsx')


def main():
    key = '腾讯'
    qichacha = Qichacha(key)
    qichacha.start()


if __name__ == '__main__':
    main()
