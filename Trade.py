from Volume_Early_Warning import *


class Trade_Api(object):
    def __init__(self):
        self.Get_Coin()

    def Get_Coin(self):
        true = ''
        false = ''
        while True:
            try:
                CoinType = eval(okcoinSpot.userinfo())['info']['funds']['free']
                break
            except:
                print('GetCoin_Error')
                continue
        Coin = []
        Amount = []
        for (key, value) in CoinType.items():
            if float(value) > 0:
                key = str(key + '_usdt')
                Coin.append(key)
                Amount.append(float(value))
        self.Coin = Coin
        self.Amount = Amount

    def Check_FreezedCoin(self):
        true = ''
        false = ''
        while True:
            try:
                CoinType = eval(okcoinSpot.userinfo())['info']['funds']['freezed']
                break
            except:
                print('GetCoin_Error')
                continue
        Coin = []
        for (key, value) in CoinType.items():
            if float(value) > 0:
                key = str(key + '_usdt')
                Coin.append((key))
                print('%s Freezed:%s'%(key,value))
        return Coin

    def Sell_Coin(self):
        if self.Coin :
            for x in range(len(self.Coin)):
                # print(self.Coin[x])
                if self.Coin[x] =='usdt_usdt':
                    pass
                else:
                    okcoinSpot.trade(self.Coin[x],'sell_market',amount=self.Amount[x])


    def Buy_Coin(self,CoinName):
        if self.Coin :
            for x in range(len(self.Coin)):
                if self.Coin[x] =='usdt_usdt':
                    okcoinSpot.trade(CoinName, 'buy_market',self.Amount[x])


    # def CheckOrder(self):

if __name__ == '__main__':
    # print(okcoinSpot.trades('snt_usdt'))
    Trade_Api = Trade_Api()

    while True:
        if Trade_Api.Check_FreezedCoin():
            pass
        else:
            print('Sell Complete')
            break