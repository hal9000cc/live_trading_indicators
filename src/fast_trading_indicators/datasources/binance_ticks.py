import os.path as path
import urllib
from common import *

__all__ = ['datasource_name', 'init', 'BASE_URL', 'timeframe_day_data']

BASE_URL = 'https://data.binance.vision/'

source_data_path = None


def datasource_name():
    return 'binance_ticks'


def init(**kwargs):
    global source_data_path

    source_data_path = path.join(SOURCES_DATA_PATH, datasource_name())


#def get_tick_file_name(symbol, date):
#    return f'{symbol}-{date.year:04d}-{date.month:02d}-{symbol.day:02d}.{ext}'


# def download_file(base_path, file_name, date_range=None, folder=None):
#
#     download_path = "{}{}".format(base_path, file_name)
#     if folder:
#         base_path = os.path.join(folder, base_path)
#     if date_range:
#         date_range = date_range.replace(" ","_")
#         base_path = os.path.join(base_path, date_range)
#     save_path = get_destination_dir(os.path.join(base_path, file_name), folder)
#
#
#     if os.path.exists(save_path):
#         print("\nfile already exists! {}".format(save_path))
#         return save_path
#
#     # make the directory
#     if not os.path.exists(base_path):
#         Path(get_destination_dir(base_path)).mkdir(parents=True, exist_ok=True)
#
#     try:
#         download_url = get_download_url(download_path)
#         dl_file = urllib.request.urlopen(download_url)
#         length = dl_file.getheader('content-length')
#         if length:
#             length = int(length)
#             blocksize = max(4096,length//100)
#
#         with open(save_path, 'wb') as out_file:
#             dl_progress = 0
#             print("\nFile Download: {}".format(save_path))
#             while True:
#                 buf = dl_file.read(blocksize)
#                 if not buf:
#                     break
#                 dl_progress += len(buf)
#                 out_file.write(buf)
#                 done = int(50 * dl_progress / length)
#                 sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50-done)) )
#                 sys.stdout.flush()
#
#         return save_path

def download_tick_day_file(tick_day_file_name):

    download_url = urllib.parse.urljoin(BASE_URL, tick_day_file_name)

    dl_file = urllib.request.urlopen(download_url)
    length = dl_file.getheader('content-length')
    if length:
        length = int(length)
        blocksize = max(4096, length//100)



    pass


def remote_day_file_name(symbol, date):
    return f'{symbol.upper()}-trades-{date}.zip'


def timeframe_day_data_from_file(file_name):
    pass


def timeframe_day_data(symbol, timeframe, date):

    tick_day_file_name = remote_day_file_name(symbol, date)
    tick_day_file_name_in_source = path.join(source_data_path, tick_day_file_name)

    if not path.isfile(tick_day_file_name_in_source):
        download_tick_day_file(tick_day_file_name)

    return timeframe_day_data_from_file(tick_day_file_name_in_source)
