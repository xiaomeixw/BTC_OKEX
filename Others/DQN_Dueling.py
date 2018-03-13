# coding: utf-8
from __future__ import division

from sklearn import preprocessing
from Model_DQN import *
from Volume_Early_Warning import *
import pandas as pd
from OkcoinSpotAPI import *
import matplotlib.pyplot as plt
from fractions import Fraction
import warnings

warnings.filterwarnings("ignore")
Okex_Api = Okex_Api()
Coin = Okex_Api.GetCoin()
# Coin = ['snt_usdt']
Okex_Api._CoinLenth = len(Coin)
Okex_Api._KlineChosen = '1hour'
Okex_Api._Lenth = 24*1000
Okex_Api._EndLenth = 0
# now = datetime.datetime.now()
# now = now.strftime('%Y-%m-%d %H:%M:%S')
# print(now)
names = locals()
StartTime = time.time()

def Get_Dataframe(Coin):
    try:
        DataFrame = pd.DataFrame(columns=("Coin", "Cny","High","Low", "Inc", "Volume_Pre_K", "Mean_Volume_K", "_VolumeS", "_VolumeM"))
        data = pd.DataFrame(okcoinSpot.getKline(Okex_Api._Kline[Okex_Api._KlineChosen], Okex_Api._Lenth, Okex_Api._EndLenth, Coin)).iloc[:Okex_Api._Lenth-1, ]
        data[5] = data.iloc[:, 5].apply(pd.to_numeric)
        data = data[data[5] >= 1000]
        data = data.reset_index(drop=True)
        Increase = (float(data.iloc[0, 4]) - float(data.iloc[0, 1])) / float(data.iloc[0, 1]) * 100
        # Increase = str('%.2f' % (Increase) + '%')
        price = float(data.iloc[0, 4])
        Hi_price = round(float((data.iloc[0, 2]))* Okex_Api._USDT_CNY,2)
        Lo_price = round(float((data.iloc[0, 3]))* Okex_Api._USDT_CNY,2)
        Cny = round(price * Okex_Api._USDT_CNY, 2)
        Volume = float(data.iloc[0, 5])
        Volume_Mean = round(Volume/1000,2)
        Volume_Pre = round(Volume / 1000, 2)
        Volume_Pre_P = 0
        if Volume_Mean == 0:
            Volume_Inc = 0
        else:
            Volume_Inc = round(((Volume_Pre - Volume_Mean) / Volume_Mean), 2)
        Timeshrft = pd.Series({'Coin': Coin, 'Cny': Cny,'High':Hi_price,'Low':Lo_price, 'Inc': Increase, 'Volume_Pre_K': Volume_Pre,
                               'Mean_Volume_K': Volume_Mean, '_VolumeS': Volume_Pre_P, '_VolumeM': Volume_Inc})
        DataFrame = DataFrame.append(Timeshrft, ignore_index=True)
        for lenth in range(1,Okex_Api._Lenth-1):
            try:
                Increase = (float(data.iloc[lenth, 4]) - float(data.iloc[0, 1])) / float(data.iloc[0, 1]) * 100
                # Increase = str('%.2f' % (Increase) + '%')
                price = float(data.iloc[lenth, 4])
                Hi_price = round(float((data.iloc[lenth, 2])) * Okex_Api._USDT_CNY, 2)
                Lo_price = round(float((data.iloc[lenth, 3])) * Okex_Api._USDT_CNY, 2)
                Cny = round(price * Okex_Api._USDT_CNY, 2)
                Volume = data.iloc[:lenth+1, 5].apply(pd.to_numeric)
                Volume_Mean = round(Volume.mean() / 1000, 2)
                Volume_Pre = round(Volume.iloc[lenth] / 1000, 2)
                Volume_Pre_P = round((Volume[lenth] / Volume[lenth - 1])-1, 2)
                Volume_Inc = round(((Volume_Pre - Volume_Mean) / Volume_Mean), 2)
                Timeshrft = pd.Series({'Coin': Coin, 'Cny': Cny,'High':Hi_price,'Low':Lo_price, 'Inc': Increase, 'Volume_Pre_K': Volume_Pre,
                                       'Mean_Volume_K': Volume_Mean, '_VolumeS': Volume_Pre_P, '_VolumeM': Volume_Inc})
                DataFrame = DataFrame.append(Timeshrft, ignore_index=True)
            except:
                break
        return DataFrame
        # print(DataFrame)
    except:
        time.sleep(5)
        print('%sError'%Coin)

# ---------------------------------------------------------


# ## main function


# Hyper Parameters
EPISODE = 200  # Episode limitation
# 300 # Step limitation in an episode
TEST = 1  # The number of experiment test every 100 episode

def TestBack():
    # Coin = pd.read_table('Coin_Select.txt', sep=',').iloc[:5, 0].values
    # Coin = ['btc_usdt','snt_usdt','eth_usdt']
    Coin = np.loadtxt("Coin_Select.txt",dtype=np.str)
    DataLen = []
    for x in Coin:
        scaler = preprocessing.StandardScaler()
        TestData = Get_Dataframe(x)
        TestData = TestData.iloc[:, 1:]
        TestData_Initial = TestData.as_matrix()
        names['TestPrice%s' % x] = TestData.iloc[:, 0]
        names['TestPrice%s' % x] = names['TestPrice%s' % x].reshape(-1, 1)
        names['TestData%s' % x] = scaler.fit_transform(TestData_Initial)
        DataLen.append(names['TestData%s' % x].shape[0])
    lenData = min(DataLen)
    Tem = names['TestData%s' % Coin[0]]
    names['TestData%s' % Coin[0]] = Tem[:lenData]
    Data = names['TestData%s' % Coin[0]]
    for x in Coin[1:]:
        Tem = names['TestData%s' % x]
        names['TestData%s' % x] = Tem[:lenData]
        Data = np.column_stack((Data, names['TestData%s' % x]))

    env1 = TWStock(Data)
    state = env1.reset()
    agent = DQN(env1)

    Cny = 1000
    for x in Coin:
        names['Amount%s' % x] = 0
    for i in range(len(Data) - 1):
        env1.render()
        action = agent.action(state)  # direct action for test
        state, reward, done, _ = env1.step(action)

        CoinName = Coin[int(action / 3)]
        Price = names['TestPrice%s' % CoinName][i]
        # Price = scaler_Price.inverse_transform(state[0].reshape(-1,1))
        Price = round(Price[0], 2)
        if action % 3 == 1 and done is False and Cny > 0:
            print('Buy %s' % CoinName, 'Time', i, 'Price', Price)
            names['Amount%s' % CoinName] = Cny / Price
            Cny = 0
        elif action % 3 == 2 and names['Amount%s' % CoinName] > 0 and done is False:
            Cny = names['Amount%s' % CoinName] * Price
            names['Amount%s' % CoinName] = 0
            print('Sell %s' % CoinName, 'Time', i, 'Price', Price, 'Current_Profit', Cny - 1000)
    CoinPrice = 0
    for x in Coin:
        CoinPrice += names['TestPrice%s' % x][-1] * names['Amount%s' % x]
        print('Amount%s' % x, names['Amount%s' % x])
    profit = Cny + CoinPrice - 1000
    print('Profit:%d' % profit)

if __name__ == '__main__':

    # TestBack()


    # np.savetxt("Coin_Select.txt", Coin,delimiter=" ", fmt="%s")
    # Coin = np.loadtxt("Coin_Select.txt",dtype=np.str)
    Coin = ['snt_usdt']
    for x in Coin:
        while True:
            try:
                TestData = Get_Dataframe(x)
            except:
                print('Get_Dataframe Error')
                time.sleep(5)
                continue
            if TestData is not None:
                break
            print('Get %s error'%x)
        print(TestData)
