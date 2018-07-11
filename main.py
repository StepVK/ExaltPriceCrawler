import requests
from time import sleep
from bs4 import BeautifulSoup


class PACrawler(object):
    link_for_cookies = 'https://www.playerauctions.com/'
    link = 'https://www.playerauctions.com/path-of-exile-items/'
    servers = {'Standard': '5578', 'Hardcore': '5577', 'Essence': '7512', 'Hardcore Essence': '7513'}
    # servers = {'Standard': '5578'}
    sleep_time = 5
    # timeout for back to back queries in seconds
    query_timeout = 1
    fake_headers = {}
    base_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'cookie': 'gsScrollPos=; isFirstVist=True; CountryISOCodeSetting=RU; km_ai=DZg5xWwuS13CHnG4ehJR9dFggvc%3D; km_lv=x; channel=google.ru; gsScrollPos=; __utmx=260853068._S1F2HUSROmTUMn4jWCgvw$6651888-18:1; __utmxx=260853068._S1F2HUSROmTUMn4jWCgvw$6651888-18:1467835034:15552000; subTab=28; __utma=260853068.1326033855.1457028294.1470820718.1470827070.349; __utmc=260853068; __utmz=260853068.1465069977.187.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); CurrencyUnitSetting=USD; userSurveyCookie=CurUserNickName=&IsOperate=false; gat_UA-3406877-1=1; __asc=e645d98c15767797ad9ea75e3bd; __auc=b9bb802b1533da76679f5f74632; timeZone=180; __atuvc=0%7C35%2C74%7C36%2C46%7C37%2C4%7C38%2C2%7C39; __atuvs=57e956656aedeef2001; _ga=GA1.2.1326033855.1457028294; kvcd=1474909811906; km_vs=1; km_uq=',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
                    }

    # get server, returns params payload for exalt price for that server
    def construct_payload(self, server):
        payload = {'serverid': server,
                   'sort': 'cheapest-price',
                   'isdefault': '0',
                   'groupid': '121,780',
                   'itemid': '780'}
        return payload

    # Accepts a string of following format: 'x.xx/y' which means price_per_stack/stack_size. Returns price per one.
    def get_price_per_one(self, string):
        string = string[string.find('$')+1:]
        price = float(string[:string.find(' ')])*100
        number = int(string[string.find('/')+2:string.find('\n')])
        result = float(price)/number
        result = int(result)
        result = float(result)/100
        return result

    # returns 0 if the request just couldn't be processed and request result otherwise
    def get_a_page(self, url_address, url_params, url_headers):
        failed_attempts = 0
        while failed_attempts < 10:
            r = requests.get(url_address, params=url_params, headers=url_headers)
            # cases when we will retry
            if r.text.find('Request unsuccessful.') >= 0:
                failed_attempts += failed_attempts
            elif r.status_code in [400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412]:
                failed_attempts += failed_attempts
            # cases when we will abort trying

            # other cases = we win
            else:
                return r
            sleep(self.query_timeout)
        # seems like 10 attempts has gone through and we still returned nothing
        return 0

    def crawl2(self):
        for server in self.servers:
            server_code = self.servers[server]
            r = self.get_a_page(self.link, self.construct_payload(server_code), self.fake_headers)
            if r == 0:
                print('I have failed to fetch the %s' % self.link)
            else:
                soup = BeautifulSoup(r.content, 'html.parser')
                print('I have crawled %s for exalted price at %s' % (server, r.url))
                with open('c:\%s.txt' % server, 'wb') as file:
                    file.write(r.text.encode('utf-8', errors='replace'))
                print('Prices for %s are: ' % server)
#                print(prices)
                print('Going to sleep %d seconds now' % self.sleep_time)
                sleep(self.sleep_time)
        pass

    # let's test teh cookies
    def test_cookies(self):
        r = requests.get(self.link_for_cookies, headers=self.base_headers)
        print("These seem to be the cookies:")
        print(r.cookies.get_dict())
        self.fake_headers = dict(self.base_headers)
        self.fake_headers.update(r.cookies.get_dict())
        print('New headers look like this now: ')
        print(self.fake_headers)

# Will return 3 if crawling was not successful at any point
    def crawl(self):
        for server in self.servers:
            server_code = self.servers[server]
            r = requests.get(self.link, params=self.construct_payload(server_code), headers=self.fake_headers)
            # with open('C:\\text.html', 'w') as f:
            #    f.write(r.text)
            if r.text.find('Request unsuccessful.') >= 0:
                return 3
            soup = BeautifulSoup(r.content, 'html.parser')
            print('I have crawled %s for exalted price at %s' % (server, r.url))
            with open('c:\%s.txt' % server, 'wb') as file:
                file.write(r.text.encode('utf-8', errors='replace'))
            table = soup.find_all('div', {'id': 'offerListBox'})[0]
            # If there is a featured price block - we need contents[5], else we need 3. So we parse 5. If it's empty
            # we parse 3 after.
            prices = []
            for row in table.contents[5].find_all('tr')[1:]:
                for column in row.findAll('td'):
                    for item in column:
                        try:
                            if item.text.find('$') >= 0:
                                temp_price = self.get_price_per_one(item.text)
                                prices.append(temp_price)
                        except:
                            pass
            if len(prices) == 0:
                print('len prices seems like 0. Going for a bonus spin')
                print(prices)
                for row in table.contents[3].find_all('tr')[1:]:
                    for column in row.findAll('td'):
                        for item in column:
                            try:
                                if item.text.find('$') >= 0:
                                    temp_price = self.get_price_per_one(item.text)
                                    prices.append(temp_price)
                            except:
                                pass
            print('Prices for %s are: ' % server)
            print(prices)
            print('Going to sleep %d seconds now' % self.sleep_time)
            sleep(self.sleep_time)

        pass

my_PACrawler = PACrawler()
#if my_PACrawler.crawl() == 3:
#    print('Seems like the request failed')
my_PACrawler.test_cookies()
if my_PACrawler.crawl() == 3:
    print("Well fuck.")
