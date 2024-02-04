"""
关注公众号:投图匠
"""

from API import *	

class MACDStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["INE.sc2212", "SHFE.sn2212","SHFE.ni2211","SHFE.ag2212"]  #订阅合约
        self.BarType = BarType.Min  #K线周期
    def on_tick(self, tick=None):
        print(tick.instrument_name)
        print(tick.exchange_id)
        print(tick.last_price)
        print(tick.volume)
        print(tick.price_tick)
        print(tick.volume_multiple)
        print(tick.datetime)
        print("="*90)
    def on_bar(self, Bar=None):
        print("MACDStrategy策略数据更新")
        # print(Bar)
        macd = MACD(Bar, 12, 26, 9)
        # print(list(macd["diff"]))
        # print(list(macd["dea"]))
        # print(list(macd["bar"]))
        # # # direction(str)"BUY", "SELL"):
        # ##offset (str): "OPEN", "CLOSE" 或 "CLOSETODAY"  \(上期所和原油分平今/平昨, 平今用"CLOSETODAY", 平昨用"CLOSE"; 其他交易所直接用"CLOSE" 按照交易所的规则平仓)
        # order = self.send_order(symbol=SYMBOL, direction="BUY", offset="OPEN", volume=3, limit_price=3607)
        # symbol = Bar.symbol[0]
        # print(self.get_account())
        # print(self.get_position(symbol))
        # print(self.get_position())
        symbol = Bar.symbol[0]
        position = self.get_position(symbol)
        diff = list(macd["bar"])
        if position.pos_long == 0 and position.pos_short == 0:
            # 开多头判断，最近一根K线收盘价在短期均线和长期均线之上，前一根K线收盘价位于K线波动范围底部25%，最近这根K线收盘价位于K线波动范围顶部25%
            if diff[-1] >= float(0) and diff[-2] <= float(0):
                order = self.send_order(symbol=symbol, direction="BUY", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)

            # 开空头判断，最近一根K线收盘价在短期均线和长期均线之下，前一根K线收盘价位于K线波动范围顶部25%，最近这根K线收盘价位于K线波动范围底部25%
            elif diff[-1] <= float(0) and diff[-2] >= float(0):
                order = self.send_order(symbol=symbol, direction="SELL", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)

        # 多头持仓止损策略
        elif position.pos_long > 0:
            if diff[-1] >= float(0) and diff[-2] <= float(0):
                if position.pos_long_today > 0 and position.exchange_id=="SHFE" or position.pos_long_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSETODAY", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSE", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)
                # 在两根K线较低点减一跳，进行多头止损
                # kline_low = min(Bar.iloc[-2].low, Bar.iloc[-3].low)
        # 空头持仓止损策略
        elif position.pos_short > 0:
            # 在两根K线较高点加一跳，进行空头止损
            # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)
            if diff[-1] <= float(0) and diff[-2] >= float(0):
                if position.pos_short_today > 0 and position.exchange_id=="SHFE" or position.pos_short_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSETODAY", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSE", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)      
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)      
                # 在两根K线较高点加一跳，进行空头止损
                # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)  
class MAStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["SHFE.cu2212"]  #订阅合约
        self.BarType = BarType.Min  #K线周期
    def on_tick(self, tick=None):
        print(tick.instrument_name,tick.last_price)
        print("="*90)
    def on_bar(self, Bar=None):
        print("MAStrategy策略数据更新")
        # print(Bar)
        ma = MA(Bar, 30)

        # print(self.get_account())
        short_avg = MA(Bar, 30)["ma"]  # 短周期
        long_avg = MA(Bar, 60)["ma"]  # 长周期
        # print(short_avg,long_avg)
        symbol = Bar.symbol[0]
        position = self.get_position(symbol)
        if position.pos_long == 0 and position.pos_short == 0:
            # 开多头判断，最近一根K线收盘价在短期均线和长期均线之上，前一根K线收盘价位于K线波动范围底部25%，最近这根K线收盘价位于K线波动范围顶部25%
            if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] > short_avg.iloc[-1]:
                order = self.send_order(symbol=symbol, direction="BUY", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)

            # 开空头判断，最近一根K线收盘价在短期均线和长期均线之下，前一根K线收盘价位于K线波动范围顶部25%，最近这根K线收盘价位于K线波动范围底部25%
            elif short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] > long_avg.iloc[-1]:
                order = self.send_order(symbol=symbol, direction="SELL", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)

        # 多头持仓止损策略
        elif position.pos_long > 0:
            if short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] > long_avg.iloc[-1]:
                if position.pos_long_today > 0 and position.exchange_id=="SHFE" or position.pos_long_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSETODAY", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSE", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)
                # 在两根K线较低点减一跳，进行多头止损
                # kline_low = min(Bar.iloc[-2].low, Bar.iloc[-3].low)
        # 空头持仓止损策略
        elif position.pos_short > 0:
            if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] > short_avg.iloc[-1]:
                if position.pos_short_today > 0 and position.exchange_id=="SHFE" or position.pos_short_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSETODAY", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSE", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)     
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)    
                # 在两根K线较高点加一跳，进行空头止损
                # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)  
class KDJStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["SHFE.rb2301"]  #订阅合约
        self.BarType = BarType.Min  #K线周期
    def on_tick(self, tick=None):
        print(tick.instrument_name,tick.last_price)
        print("="*90)
    def on_bar(self, Bar=None):
        print("KDJStrategy策略数据更新")
        # print(Bar)
        kdj = KDJ(Bar, 9, 3, 3)
        # print(list(kdj["k"]))
        # print(list(kdj["d"]))
        # print(list(kdj["j"]))
        symbol = Bar.symbol[0]
        position = self.get_position(symbol)
        K = list(kdj["k"])
        if position.pos_long == 0 and position.pos_short == 0:
            # 开多头判断，最近一根K线收盘价在短期均线和长期均线之上，前一根K线收盘价位于K线波动范围底部25%，最近这根K线收盘价位于K线波动范围顶部25%
            if K[-1] >= float(50) and K[-2] <= float(50):
                order = self.send_order(symbol=symbol, direction="BUY", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)

            # 开空头判断，最近一根K线收盘价在短期均线和长期均线之下，前一根K线收盘价位于K线波动范围顶部25%，最近这根K线收盘价位于K线波动范围底部25%
            elif K[-1] <= float(50) and K[-2] >= float(50):
                order = self.send_order(symbol=symbol, direction="SELL", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)

        # 多头持仓止损策略
        elif position.pos_long > 0:
            if K[-1] >= float(50) and K[-2] <= float(50):
                if position.pos_long_today > 0 and position.exchange_id=="SHFE" or position.pos_long_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSETODAY", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSE", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)
                # 在两根K线较低点减一跳，进行多头止损
                # kline_low = min(Bar.iloc[-2].low, Bar.iloc[-3].low)
        # 空头持仓止损策略
        elif position.pos_short > 0:
            if K[-1] <= float(50) and K[-2] >= float(50):
                if position.pos_short_today > 0 and position.exchange_id=="SHFE" or position.pos_short_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSETODAY", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSE", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)  
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)     
                # 在两根K线较高点加一跳，进行空头止损
                # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)  
class RSIStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["CFFEX.IF2212","CFFEX.IH2212","CFFEX.IC2212","CFFEX.T2212"]  #订阅合约
        self.BarType = BarType.Min  #K线周期
    def on_tick(self, tick=None):
        print(tick.instrument_name,tick.last_price)
        print("="*90)
    def on_bar(self, Bar=None):
        print("RSIStrategy策略数据更新")
        rsi = RSI(Bar, 7)
        # print(list(rsi["rsi"]))
        # 开仓判断
        rsi = list(rsi["rsi"])
        symbol = Bar.symbol[0]
        position = self.get_position(symbol)
        print(position)
        if position.pos_long == 0 and position.pos_short == 0:
            # 开多头判断，最近一根K线收盘价在短期均线和长期均线之上，前一根K线收盘价位于K线波动范围底部25%，最近这根K线收盘价位于K线波动范围顶部25%
            if rsi[-1] >= float(50) and rsi[-2] <= float(50):
                order = self.send_order(symbol=symbol, direction="BUY", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)

            # 开空头判断，最近一根K线收盘价在短期均线和长期均线之下，前一根K线收盘价位于K线波动范围顶部25%，最近这根K线收盘价位于K线波动范围底部25%
            elif rsi[-1] <= float(50) and rsi[-2] >= float(50):
                order = self.send_order(symbol=symbol, direction="SELL", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)

        # 多头持仓止损策略
        elif position.pos_long > 0:
            if rsi[-1] >= float(50) and rsi[-2] <= float(50):
                if position.pos_long_today > 0 and position.exchange_id=="SHFE" or position.pos_long_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSETODAY", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSE", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)
                # 在两根K线较低点减一跳，进行多头止损
                # kline_low = min(Bar.iloc[-2].low, Bar.iloc[-3].low)
        # 空头持仓止损策略
        elif position.pos_short > 0:
            if rsi[-1] <= float(50) and rsi[-2] >= float(50):
                if position.pos_short_today > 0 and position.exchange_id=="SHFE" or position.pos_short_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSETODAY", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSE", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)  
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)        
                # 在两根K线较高点加一跳，进行空头止损
                # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)        
class 止损止盈Strategy(Strategy):
    def __init__(self):
        super().__init__()
        self.symbol_lsit = ["CFFEX.IF2212"]  #订阅合约
        self.BarType = BarType.Min  #K线周期
    def on_tick(self, tick=None):
        print(tick.instrument_name,tick.last_price)
        print("="*90)
    def on_bar(self, Bar=None):
        print("RSIStrategy策略数据更新")
        rsi = RSI(Bar, 7)
        # print(list(rsi["rsi"]))
        # 开仓判断
        rsi = list(rsi["rsi"])
        symbol = Bar.symbol[0]
        position = self.get_position(symbol)
        print(position)
        if position.pos_long == 0 and position.pos_short == 0:
            # 开多头判断，最近一根K线收盘价在短期均线和长期均线之上，前一根K线收盘价位于K线波动范围底部25%，最近这根K线收盘价位于K线波动范围顶部25%
            if rsi[-1] >= float(50) and rsi[-2] <= float(50):
                order = self.send_order(symbol=symbol, direction="BUY", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)

            # 开空头判断，最近一根K线收盘价在短期均线和长期均线之下，前一根K线收盘价位于K线波动范围顶部25%，最近这根K线收盘价位于K线波动范围底部25%
            elif rsi[-1] <= float(50) and rsi[-2] >= float(50):
                order = self.send_order(symbol=symbol, direction="SELL", offset="OPEN", volume=3, price=Bar.iloc[-1].close)
                print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)

        # 多头持仓止损策略
        elif position.pos_long > 0:
            if rsi[-1] >= float(50) and rsi[-2] <= float(50):
                if position.pos_long_today > 0 and position.exchange_id=="SHFE" or position.pos_long_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSETODAY", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="SELL", offset="CLOSE", volume=position.pos_long, price=Bar.iloc[-1].close)
                    print(order)
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)
                # 在两根K线较低点减一跳，进行多头止损
                # kline_low = min(Bar.iloc[-2].low, Bar.iloc[-3].low)
        # 空头持仓止损策略
        elif position.pos_short > 0:
            if rsi[-1] <= float(50) and rsi[-2] >= float(50):
                if position.pos_short_today > 0 and position.exchange_id=="SHFE" or position.pos_short_today > 0 and position.exchange_id=="INE":
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSETODAY", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)
                else:
                    order = self.send_order(symbol=symbol, direction="BUY", offset="CLOSE", volume=position.pos_short, price=Bar.iloc[-1].close)
                    print(order)  
            else:
                print("最新价位:%.2f ，未满足开仓条件" % Bar.iloc[-1].close)        
                # 在两根K线较高点加一跳，进行空头止损
                # kline_high = max(Bar.iloc[-2].high, Bar.iloc[-3].high)      

Config = {'broker_id':'经纪', 'account_id':'交易账号', 'password':'交易密码','Tqaccount':'天勤账号', 'Tqpassword':'天勤密码'}
if __name__ == '__main__':
    t = CtpGateway()
    t.add_Strategy(MACDStrategy())
    t.add_Strategy(MAStrategy())
    t.add_Strategy(KDJStrategy())
    t.add_Strategy(RSIStrategy())
    t.add_Config(Config)
    t.Start()
