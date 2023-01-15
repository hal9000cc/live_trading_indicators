from abc import ABC, abstractmethod


class OnlineSource:

    @abstractmethod
    def datasource_name(self):
        pass

    @abstractmethod
    def bars_online_request(self, symbol, timeframe, time_start, time_end):
        pass

