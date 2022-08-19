import json
import time
import datetime
import timedelta


def read_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def functionName(mydata):
    mydata = read_file(mydata)
    my_set = set()
    for x in mydata:
        my_set.add(x['functionName'])
    print(*my_set, sep='\n')

def list_date():
    mylist = []
    start_date = datetime.datetime(2022, 8, 1)
    end_date = datetime.datetime.today()
    delta = datetime.timedelta(days=1)
    while start_date <= end_date:
        mylist.append(start_date)
        start_date += delta
    return mylist

def unpack_stat(nameFile, functionName):
    mydata = read_file(nameFile)
    my_date = []
    date_dict = {}
    for i in range(len(mydata)):
        if mydata[i]['functionName'] == functionName:
            my_date.append(mydata[i]['timeStamp'])
    for x in list_date():
        for k in my_date:
            if int(x.timestamp()) < int(k) < int(x.timestamp()) + 86399:
                date_dict[x] = date_dict.get(x, 0) + 1
    return date_dict

unpack_dict = unpack_stat('database_open_box.json', 'systemMint(address to, string _item, string _info)')
print('Статистика открытия боксов:')
for key, value in unpack_dict.items():
    print(f"{key} : {value} боксов открыто")

print()

unpack_dict = unpack_stat('database_market.json', 'buy(uint256 _amount)')
print('Статистика покупок боксов/кроссовок:')
for key, value in unpack_dict.items():
    print(f"{key} : {value} куплено")

#functionName('database_treasury.json')
#functionName('database_open_box.json')
#functionName('database_market.json')

breed_list = read_file('database_treasury.json')
breed_data = {}

for x in list_date():
    for k in breed_list:
        if int(x.timestamp()) < int(k['timeStamp']) < int(x.timestamp()) + 86399:
            if x not in breed_data:
                breed_data[x] = [0, 0]
            breed_data[x][0] += 1
            breed_data[x][1] += int(k['value']) // 1000000000000000000
print()
total = 0
print('Статистика бридов по AZY:')
for key, value in breed_data.items():
    print(f"{key} : {value[0]} бридов, {value[1]} токенов AZY оплачено")
    total += value[1]
print(total, "отправили токенов Azy в сокровищницу")


#mydata = read_file('database_market.json')
#for x in mydata:
#    if x['functionName'] == 'sell(address _reserveToken, uint256 _sellAmount, uint256 _minReturn)':
#        #print(f"Время: {x['timeStamp']} операция: {x['functionName'][:4]}")
#        time = x['timeStamp']
#    elif x['functionName'] == 'buy(uint256 _amount)':
#        if time == x['timeStamp']:
 #           print('----*********--------------**********-----------')
  #          print(f"Время: {x['timeStamp']} операция: {x['functionName'][:4]} hash {x['hash']}")
   #     print(x)


