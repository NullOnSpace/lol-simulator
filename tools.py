import requests


def get_page(url):
    max_try = 100
    headers = {'User-Agent': """User-Agent:Mozilla/5.0 """
                             """(Macintosh; Intel Mac OS X 10_12_3) """
                             """AppleWebKit/537.36 """
                             """(KHTML, like Gecko) """
                             """Chrome/56.0.2924.87 Safari/537.36"""
               }
    while True:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            break
        except requests.exceptions.RequestException as e:
            print(url, 'with', max_try, 'tries:', e)
            max_try -= 1
            if not max_try:
                raise
    return r
