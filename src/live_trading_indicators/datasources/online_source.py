from abc import ABC, abstractmethod


class OnlineSource:

    @staticmethod
    @abstractmethod
    def datasource_name():
        pass

    @abstractmethod
    def bars_online_request(self, symbol, timeframe, time_start, time_end):
        pass
