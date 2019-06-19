from .tools import get_page
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs
import os
import time


def item_download():
    all_items_url = 'https://lol.gamepedia.com/Portal:Items'
    file_path = 'E://lol_item'
    res = get_page(all_items_url)
    with open(os.path.join(file_path, 'all_items'), 'wb') as fd:
        fd.write(res.content)
    soup = bs(res.content, 'html.parser')
    tb = soup.find(class_='frontpagetable')
    tr = list(list(tb.children)[1].children)[-1]
    divs = tr.find('td').find_all('div', recursive=False)
    cate_list = [list(div.select('span > a')) if n%2 else str(div.find('h2').string)
                 for n, div in enumerate(divs)]
    cate_dict = dict()
    key = 'error'
    for i in cate_list:
        if type(i) is str:
            key = i
        else:
            cate_dict[key] = i
    files = os.listdir(file_path)
    for k, a_tag_list in cate_dict.items():
        if k not in files:
            os.mkdir(os.path.join(file_path, k))
        for a_tag in a_tag_list:
            url = urljoin(all_items_url, a_tag['href'])
            res = get_page(url)
            fn = str(a_tag.string)
            with open(os.path.join(file_path, k, fn), 'wb') as fd:
                fd.write(res.content)
            time.sleep(2)

