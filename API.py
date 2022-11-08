from tqsdk import TqApi, TqAuth, TqAccount
from tqsdk.ta import *
from datetime import date
from tqsdk import TqBacktest, TargetPosTask ,TqSim
class CtpGateway():
    def __init__(self):
        super().__init__()
        self.Strategy_lsit = []
        self.订阅合约周期 = []           
    def send_order(self, symbol, direction, offset, volume, price):
        quote = self.api.get_quote(symbol)
        # 输出 ni2206 的最新行情时间和最新价
        print(quote.datetime,quote.bid_price1,quote.ask_price1, quote.last_price)
        if direction == "BUY":
            price = quote.ask_price1
        else:
            price = quote.bid_price1
        return self.api.insert_order(symbol=symbol, direction=direction, offset=offset, volume=volume, limit_price=price)
    def get_position(self, symbol = None):
        return self.api.get_position(symbol)
    def get_account(self, account = None):
        return self.api.get_account(account)
    def update_Bar(self, Bar):
        symbol = Bar.symbol[0]
        duration = Bar.duration[0]
        for i in self.Strategy_lsit:
            if symbol in i.symbol_lsit:
                if duration == i.BarType:
                    i.on_bar(Bar)          
    def update_tick(self, tick):
        for i in self.Strategy_lsit:
            if tick.instrument_id in i.symbol_lsit:
                i.on_tick(tick)

    def add_Strategy(self, Strategy):
        """
        Add Strategy.
        """
        Strategy.SetAPI(self)
        self.Strategy_lsit.append(Strategy)
        for symbol in Strategy.symbol_lsit:
            if symbol not in self.订阅合约周期:
                self.订阅合约周期.append([symbol,Strategy.BarType])
        return Strategy
    def add_Config(self, setting):
        # self.api = TqApi(TqAccount(setting["broker_id"], setting["account_id"], setting["password"]), auth=TqAuth(setting["Tqaccount"], setting["Tqpassword"]))
        # self.api = TqApi(auth=TqAuth(setting["Tqaccount"], setting["Tqpassword"]))
        # self.api = TqApi(backtest=TqBacktest(start_dt=date(2022, 10, 15), end_dt=date(2022, 11, 1)), auth=TqAuth(setting["Tqaccount"], setting["Tqpassword"]))
        self.api = TqApi(TqSim(init_balance=100000), auth=TqAuth(setting["Tqaccount"], setting["Tqpassword"]))
    def Start(self):
        klines = [self.api.get_kline_serial(x[0], x[1]) for x in self.订阅合约周期]  # 86400: 最大是日线
        # quote_list = [self.api.get_quote(x[0]) for x in self.订阅合约周期] 
        while True:
            self.api.wait_update()
            # for K in quote_list:
                # if self.api.is_changing(K, "last_price"):
                    # self.update_tick(K)
            for i in klines:
                if self.api.is_changing(i.iloc[-1], "datetime"):  # 如果产生一根新日线 (即到达下一个交易日): 重新获取上下轨
                    self.update_Bar(i)
