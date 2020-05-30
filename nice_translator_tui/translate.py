import requests
import re
from html.parser import HTMLParser

import http.client
import hashlib
import urllib
import random
import json
import pkg_resources

app_id = ''
secret_key = ''
target_languages = [
    'zh', 
    'en',
]

data = pkg_resources.resource_string(__name__, "config.json")
cfg = json.loads(data)
app_id = cfg['app_id']
secret_key = cfg['secret_key']
if cfg.get('target_languages') is not None:
    target_languages = cfg.get('target_languages')

httpClient = None
fromLang = 'auto'

def translate_with_baidu(q, to):
    myurl = '/api/trans/vip/translate'
    toLang = to   #译文语种
    salt = random.randint(32768, 65536)
    sign = app_id + q + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + app_id + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
    salt) + '&sign=' + sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)
        return result
    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()

def get_translate_with_baidu(q, to):
    if app_id is '':
        return {
            'title': 'Configurations required',
            'subtitle': '百度翻译',
            'from': 'ERROR',
            'to': 'Error'
        }
    else :
        rs = translate_with_baidu(q, to)
        if rs.get('error_code') is not None:
            rs['trans_result'] = [{'dst': rs['error_msg']}]
            rs['from'] = 'ERROR'
            rs['to'] = 'Error occur when requesting Baidu API, code: ' + rs['error_code']
        return {
            'title': rs['trans_result'][0]['dst'],
            'subtitle': '百度翻译: ' + rs['from'] + ' to ' + rs['to'],
            'from': rs['from'].strip(),
            'to': rs['to'].strip()
        }

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        if len(attrs) > 0:
            if attrs[0][1].startswith('synoid'):
                self.__buf__.append('\nsynoid\n')
            if attrs[0][1].startswith('antoid'):
                self.__buf__.append('\nantoid\n')

    def handle_endtag(self, tag):
        if tag.startswith('li') or tag.startswith('div'):
            self.__buf__.append('\n')

    def handle_data(self, data):
        if len(data) > 0:
            self.__buf__.append(data)

    def feed(self, feed, buf):
        self.__buf__ = buf
        return super().feed(feed)

parser = MyHTMLParser()

def translate(q):
    finalrs = []
    tab = ' ' * 8
    html = requests.get('https://cn.bing.com/dict/search?q={q}'.format(q = q)).text
    hd_area_pattern = re.compile(r'<div class="hd_area">')
    hd_area_rs = hd_area_pattern.search(html)

    if (hd_area_rs is not None):
        prus_head_pattern = re.compile(r'<div class="hd_prUS b_primtxt">')
        prus_head_rs = prus_head_pattern.search(html)
        prus_end_pattern = re.compile(r'<\/div>')
        if (prus_head_rs is not None):
            finalrs.append('[词汇发音]')
            finalrs.append('')
            prus_end_rs = prus_end_pattern.search(html, prus_head_rs.span()[1])
            prus_html = html[prus_head_rs.span()[1]:prus_end_rs.span()[0]]
            prus_html = prus_html.split('美&#160;')
            finalrs.append('{:>9}{}{}'.format('US', tab, prus_html[1]))

            pr_head_pattern = re.compile(r'<div class="hd_pr b_primtxt">')
            pr_head_rs = pr_head_pattern.search(html)
            pr_end_pattern = re.compile(r'<\/div>')
            pr_end_rs = pr_end_pattern.search(html, pr_head_rs.span()[1])
            pr_html = html[pr_head_rs.span()[1]:pr_end_rs.span()[0]]
            pr_html = pr_html.split('英&#160;')
            finalrs.append('{:>9}{}{}'.format('UK', tab, pr_html[1]))
            finalrs.append('')

        finalrs.append('[词典释义]')
        finalrs.append('')
        finalrs.append('')
        ul_head_pattern = re.compile(r'<ul>')
        ul_head_rs = ul_head_pattern.search(html, hd_area_rs.span()[1])
        # dictionary result handle
        if (ul_head_rs.span()[0] - hd_area_rs.span()[1] < 3000):
            ul_end_pattern = re.compile(r'<\/ul>')
            ul_end_rs = ul_end_pattern.search(html, ul_head_rs.span()[1])
            
            list_html = html[ul_head_rs.span()[1]:ul_end_rs.span()[0]]
            buf = []
            parser.feed(list_html, buf)
            for i in buf:
                if i == '\n':
                    finalrs.append(i.strip())
                elif not i.startswith(';'):
                    if (finalrs[-1] == ''):
                        finalrs[-1] = '{:>9}{}'.format(finalrs[-1].strip() + i.strip().replace('网络', 'net.'), tab)
                    else :
                        finalrs[-1] = finalrs[-1] + i.strip() + ';'

        # form result hanlde
        hd_if_head_pattern = re.compile(r'<div class="hd_if">')
        hd_if_head_rs = hd_if_head_pattern.search(html, hd_area_rs.span()[1])

        if hd_if_head_rs is not None:
            finalrs.append('[形式变换]')
            finalrs.append('')
            finalrs.append('{:>9}{}{}'.format('do.', tab, q))
            finalrs.append('')
            hd_if_end_pattern = re.compile(r'</div>')
            hd_if_end_rs = hd_if_end_pattern.search(html, hd_if_head_rs.span()[1])
            form_list_html = html[hd_if_head_rs.span()[0]:hd_if_end_rs.span()[1]]
            form_buf = []
            parser.feed(form_list_html, form_buf)
            for r in form_buf:
                if r == '\xa0\xa0':
                    finalrs.append('')
                else:
                    if r.endswith('：'):
                        rstrip = r.strip().replace('第三人称单数：', 'dose.').replace('现在分词：', 'doing.').replace('过去式：', 'did.').replace('过去分词：', 'done.').replace('复数：', '+s.').replace('比较级：', 'more.').replace('最高级：', 'most.')
                        finalrs[-1] = '{:>9}{}'.format(finalrs[-1] + rstrip, tab)
                    else:
                        finalrs[-1] = finalrs[-1] + r.strip()

        # colid result handle
        wd_div_head_pattern = re.compile(r'<div class="wd_div">')
        wd_div_head_rs = wd_div_head_pattern.search(html, hd_area_rs.span()[1])

        if wd_div_head_rs is not None:
            wd_div_end_pattern = re.compile(r'<div class="df_div">')
            wd_div_end_rs = wd_div_end_pattern.search(html, wd_div_head_rs.span()[1])
            wd_div_html = html[wd_div_head_rs.span()[0]:wd_div_end_rs.span()[0]]
            wd_buf = []
            parser.feed(wd_div_html, wd_buf)
            wd_buf_str = ''.join(wd_buf).replace('同义词', '').replace('搭配', '').replace('反义词', '')
            
            colid_zoom = ''
            antoid_zoom = ''
            synoid_zoom = ''
            split_antoid = wd_buf_str.split('antoid')
            if len(split_antoid) is 2:
                colid_zoom = split_antoid[0]
                split_synoid = split_antoid[1].split('synoid')
                if len(split_synoid) is 2:
                    antoid_zoom = split_synoid[0]
                    synoid_zoom = split_synoid[1]
                else :
                    antoid_zoom = split_antoid[1]
            else:
                split_synoid = wd_buf_str.split('synoid')
                if len(split_synoid) is 2:
                    colid_zoom = split_synoid[0]
                    synoid_zoom = split_synoid[1]
                else :
                    colid_zoom = wd_buf_str
            
            colid_list = list(filter(lambda x: x != '', colid_zoom.split('\n')))
            antoid_list = list(filter(lambda x: x != '', antoid_zoom.split('\n')))
            synoid_list = list(filter(lambda x: x != '', synoid_zoom.split('\n')))


            if len(colid_list) > 0:
                finalrs.append('[搭配]')
                finalrs.append('')
                for i, p in enumerate(colid_list):
                    if i % 2 is 0:
                        finalrs.append('{:>9}{}{}'.format(p.strip(), tab, colid_list[i + 1].strip().replace(',', '，')))
                finalrs.append('')


            if len(antoid_list) > 0:
                finalrs.append('[反义词]')
                finalrs.append('')
                for i, p in enumerate(antoid_list):
                    if i % 2 is 0:
                        finalrs.append('{:>9}{}{}'.format(p.strip(), tab, antoid_list[i + 1].strip().replace(',', '，')))
                finalrs.append('')

            if len(synoid_list) > 0:
                finalrs.append('[同义词]')
                finalrs.append('')
                for i, p in enumerate(synoid_list):
                    if i % 2 is 0:
                        finalrs.append('{:>9}{}{}'.format(p.strip(), tab, synoid_list[i + 1].strip().replace(',', '，')))
                finalrs.append('')
    
    else :
        def wq(target_language):
            return get_translate_with_baidu(q, target_language)

        tab2 = 5
        baidu_tran_rs = list(map(wq, target_languages))
        finalrs.append('[原句]')
        finalrs.append('')
        finalrs.append(' ' * tab2 + q)
        finalrs.append('')
        finalrs.append('[句子翻译]')
        finalrs.append('')
        for tran_rs in baidu_tran_rs:
            if tran_rs['from'] != tran_rs['to']:
                finalrs.append(' ' * tab2 + '-> {}'.format(tran_rs['to']))
                finalrs.append(' ' * tab2 + tran_rs['title'])  
                finalrs.append('')
                if tran_rs['from'] == 'ERROR':
                    finalrs.append(' ' * tab2 + 'Please check your appid and secret_key configurations')
                    finalrs.append('')
                    finalrs.append(' ' * tab2 + pkg_resources.resource_filename(__name__, "config.json"))
                    break

    return finalrs

def pf(rs):
    for r in rs:
        print(r)

if __name__ == '__main__':
    # pf(translate('我'))
    # print('-' * 100)
    # pf(translate('get it done'))
    # print('-' * 100)
    pf(translate('新年好，恭喜发财，利是到来'))