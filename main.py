import requests
import json
import time
from pycoingecko import CoinGeckoAPI
import telebot
from auth_data import token

cg = CoinGeckoAPI()

URL_AUTH = 'https://api.bscscan.com/api'
KEY = 'BT27NAHYJCUWDHK1SEJYJFDTBJRGTE5QUI'
A_OPEN_BOX = '0xa8330f559e6317813940936a78b0b4597488cb7b'
A_MARKET = '0x70624F31d403b5a5505b9127663674fc1195C383'
A_TREASURY = '0x6df58f91f8bdc7f5b17e0cad3e3fc5d5ea4c92bc'

URL_PARSE_AZY = 'https://www.coingecko.com/ru/%D0%9A%D1%80%D0%B8%D0%BF%D1%82%D0%BE%D0%B2%D0%B0%D0%BB%D1%8E%D1%82%D1%8B/amazy'
URL_PARSE_AMT = 'https://coinmarketcap.com/ru/currencies/amazy-move-token/'
URL_PARSE_AMAZY = 'https://rest.amazy.io/marketplace/'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 ' \
                  'Safari/537.36 ',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


def parse_sneakers(type):
    def change_address(page, type):
        return f"https://rest.amazy.io/marketplace/?page={page}&perPage=100&type={type}"
    url = change_address(1, type)
    data = parse(url)
    if data['salesTotal'] > 100:
        for i in range(2, data['salesTotal']//100 + 2):
            data['sales'].extend(parse(change_address(i, type))['sales'])
    return data

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def parse(url):
    html = get_html(url)
    mydict = html.json()
    if html.status_code == 200:
        return mydict
    else:
        print('Error')


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="MarketplaceBoxItem_inventoryItem__2X1GD")


def read_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def writeToJSONFile(path, fileName, data):
    filePathNameWExt = './' + path + '/' + fileName
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp)


def json_get_normal(startblock, address):
    params = {
        'module': 'account',
        'action': 'txlist',
        'startblock': startblock,
        'endblock': 999999999,
        'page': 1,
        'offset': 10000,
        'sort': 'asc',
        'address': address,
        'apikey': KEY
    }
    r = requests.get(URL_AUTH, params=params)
    res = r.json()['result']
    return res


def json_get_bep20(startblock, contractAddress, address):
    params = {
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': contractAddress,
        'address': address,
        'page': 1,
        'offset': 10000,
        'startblock': startblock,
        'endblock': 999999999,
        'sort': 'asc',
        'apikey': KEY
    }
    r = requests.get(URL_AUTH, params=params)
    res = r.json()['result']
    return res


def json_export_normal(nameFile, address):
    mydata = []
    old_json = read_file(nameFile)
    if old_json[-1].get('blockNumber', '0') == '0':
        mydata = json_get_normal(1, address)
        last_block = str(int(mydata[-1]['blockNumber']) + 1)
    else:
        mydata = old_json
        last_block = str(int(old_json[-1]['blockNumber']) + 1)
    while True:
        time.sleep(1)
        mydata.extend(json_get_normal(last_block, address))
        print(last_block)
        if last_block == str(int(mydata[-1]['blockNumber']) + 1):
            break
        else:
            last_block = str(int(mydata[-1]['blockNumber']) + 1)
    writeToJSONFile('./', nameFile, mydata)


def json_export_bep20(nameFile, contractAddress, address):
    old_json = read_file(nameFile)
    if old_json[-1].get('blockNumber', '0') == '0':
        mydata = json_get_bep20(1, contractAddress, address)
        last_block = str(int(mydata[-1]['blockNumber']) + 1)
    else:
        mydata = old_json
        last_block = str(int(old_json[-1]['blockNumber']) + 1)
    while True:
        time.sleep(1)
        mydata.extend(json_get_bep20(last_block, contractAddress, address))
        print(last_block)
        if last_block == str(int(mydata[-1]['blockNumber']) + 1):
            break
        else:
            last_block = str(int(mydata[-1]['blockNumber']) + 1)
    writeToJSONFile('./', nameFile, mydata)


def get_price_cgecko(token='azy'):
    token_list = cg.get_coins_list()
    for x in token_list:
        if x['symbol'] == token.lower():
            token_id = x['id']
            break
    return cg.get_price(ids=token_id, vs_currencies='usd')[token_id]['usd']

def get_price_pcswap(contract='0xf625069dce62dF95b4910f83446954B871F0Fc4f'):
    r = requests.get('https://api.pancakeswap.info/api/v2/tokens/' + contract, params=None).text
    return f"{float(json.loads(r)['data']['price']):.{5}f}"

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=['start'])
    def start_message(message):
        command = f"Цены токенов /price \n" \
                  f"Аналитика продаж /sellstat"
        bot.send_message(message.chat.id, command)

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text.lower() == '/price':
            try:
                answer = f"AZY = {get_price_cgecko()} $\n" \
                         f"AMT = {get_price_pcswap()} $\n" \
                         f"Боксы floor price = {floor_price_sneakers()}BNB = {floor_price_sneakers() * float(get_price_pcswap('0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'))}$ \n" \
                         f"Кросы floor price = BNB = $"
                bot.send_message(message.chat.id, answer)
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "wrong"
                )
        else:
            bot.send_message(
                message.chat.id,
                "Неправильная команда - again"
            )
    bot.polling()

def floor_price_sneakers():
    data = parse_sneakers('sneakers')
    price = set()
    for x in data['sales']:
        price.add(int(x['price']))
    return min(price) / 1000000000000000000


def floor_price_box():
    pass



json_export_normal('database_open_box.json', A_OPEN_BOX)
json_export_normal('database_market.json', A_MARKET)
json_export_bep20('database_treasury.json', '0x7b665B2F633d9363b89A98b094B1F9E732Bd8F86', A_TREASURY)
#print(json_get_bep20(1, '0x7b665B2F633d9363b89A98b094B1F9E732Bd8F86', A_TREASURY)[-1])
# print(cg.get_coin_history_by_id('amazy', '01-08-2022')['market_data']['current_price']['usd'])
#print(cg.get_coins_list())
#print(get_price('BTC'))


#telegram_bot(token)

#parse_sneakers('sneakers')

#floor_price_sneakers()