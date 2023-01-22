import logging
import sqlite3
import sqlite3 as sql
import numpy as np
from enum import IntEnum
import importlib
import os
import multiprocessing
from ..indicator_data import OHLCV_day
from ..constants import TIME_TYPE, PRICE_TYPE, VOLUME_TYPE, TIME_UNITS_IN_ONE_SECOND
from ..exceptions import *

DATABASE_VERSION = 3


class CompressionType(IntEnum):
    no = 0
    gzip = 1
    bz2 = 2
    lz4 = 3
    auto = 4

    @staticmethod
    def cast(str_type):
        return getattr(__class__, str_type)


class Sqlite3Cache:

    def __init__(self, config):

        self.database_file = config['quotation_database']
        self.compression_type = CompressionType.cast(config['compression_type'])
        self.compression_modules = dict()

        database_folder = os.path.split(self.database_file)[0]
        if not os.path.isdir(database_folder):
            os.makedirs(database_folder)

        self.sl3base = sql.connect(self.database_file, isolation_level=None)

        cursor = self.sl3base.cursor()
        check_bars_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotes'")
        if check_bars_table.fetchone() is None:
            self.init_database()
            return

        self.database_config = self.get_config()
        version = int(self.database_config['version'])

        if version != DATABASE_VERSION:
            self.convert_database()
            self.database_config = self.get_config()

        assert int(self.database_config['version']) == DATABASE_VERSION

    def convert_database(self):

        version = int(self.database_config['version'])
        if version > DATABASE_VERSION:
            raise LTIException(f'Unsupported version of the database: {version}. Update the live_trading_indicators library.')

        if version == 1:
            self.convert_1_2()
            version = 2

        if version == 2:
            self.convert_2_3()
            version = 3

    @staticmethod
    def day_to_int(day_date):
        return int(day_date.astype('datetime64[D]').astype(np.int64))

    @staticmethod
    def day_from_int(day_int):
        return np.datetime64(day_int, 'D')

    def get_config(self):

        cursor = self.sl3base.cursor()

        check_config_table = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config'")
        if check_config_table.fetchone() is None:
            return {'version': '1'}

        config_table = cursor.execute("SELECT name, value FROM config")
        return {name: value for name, value in config_table.fetchall()}

    def get_compression_module(self, compression_type):

        compression_module = self.compression_modules.get(compression_type)
        if compression_module is not None:
            return compression_module

        if compression_type == CompressionType.gzip:
            return importlib.import_module('zlib')
        elif compression_type == CompressionType.bz2:
            return importlib.import_module('bz2')
        elif compression_type == CompressionType.lz4:
            return importlib.import_module('lz4.frame')
        else:
            raise NotImplementedError(f'Unknown compression type: {compression_type}')

    def compress_numpy(self, array, compression_type):

        if compression_type == CompressionType.no:
            return array.tobytes()

        compression_module = self.get_compression_module(compression_type)
        return compression_module.compress(array.tobytes())

    def decompress_numpy(self, array_compressed_bytes, dtype, compression_type):

        if compression_type == CompressionType.no:
            array_bytes = array_compressed_bytes
        else:
            compression_module = self.get_compression_module(compression_type)
            array_bytes = compression_module.decompress(array_compressed_bytes)

        return np.frombuffer(array_bytes, dtype=dtype)

    def init_database(self):
        cursor = self.sl3base.cursor()
        cursor.executescript("""

            BEGIN TRANSACTION;
                            
            CREATE TABLE config (
                name TEXT NOT NULL,
                value);
                                
            CREATE TABLE quotes (
                source	TEXT NOT NULL,
                symbol	TEXT NOT NULL,
                timeframe	INTEGER NOT NULL,
                day	INTEGER NOT NULL,
                compression_type	INT,
                time	BLOB,
                open	BLOB,
                high	BLOB,
                low	BLOB,
                close	BLOB,
                volume	BLOB,
                PRIMARY KEY(source, symbol, timeframe, day));
                
            INSERT INTO config(name, value) VALUES ("version", """ + f'"{DATABASE_VERSION}"' + """);
            
            COMMIT TRANSACTION;
        """)

    def convert_1_2(self):

        logging.info('Start database conversion from version 1 to 2...')
        cursor = self.sl3base.cursor()
        cursor.executescript("""

            BEGIN TRANSACTION;
            
            CREATE TABLE quotes_new (
                source	TEXT NOT NULL,
                symbol	TEXT NOT NULL,
                timeframe	INTEGER NOT NULL,
                day	INTEGER NOT NULL,
                compression_type	INT,
                time	BLOB,
                open	BLOB,
                high	BLOB,
                low	BLOB,
                close	BLOB,
                volume	BLOB,
                PRIMARY KEY(source, symbol, timeframe, day)
            );

            INSERT INTO quotes_new (source, symbol, timeframe, day, compression_type, time, open, high, low, close, volume)             
            SELECT source, symbol, timeframe, day, compression_type, time, open, high, low, close, volume
            FROM quotes;
            
            DROP TABLE quotes;
            ALTER TABLE quotes_new RENAME TO quotes;
    
            CREATE TABLE config (
                name TEXT NOT NULL,
                value);
                
            INSERT INTO config(name, value) VALUES ("version", "2");
            
            COMMIT TRANSACTION;
            VACUUM;
        
        """)

        logging.info('Database conversion completed.')

    def convert_2_3(self):

        logging.info('Start database conversion from version 1 to 2...')
        cursor = self.sl3base.cursor()
        cursor.executescript("""
            BEGIN TRANSACTION;
            
            CREATE TEMPORARY TABLE bad_names
            AS
            SELECT source, symbol, timeframe, day
            FROM quotes
            WHERE
                symbol <> lower(symbol);
                
            INSERT INTO quotes(source, symbol, timeframe, day, compression_type, time, open, high, low, close, volume)
            SELECT q.source, lower(q.symbol), q.timeframe, q.day, q.compression_type, q.time, q.open, q.high, q.low, q.close, q.volume
            FROM
                bad_names bn
                JOIN quotes q ON q.source = bn.source AND q.symbol = bn.symbol AND q.timeframe = bn.timeframe AND q.day = bn.day
            ON CONFLICT DO NOTHING;
            
            DELETE FROM quotes
            WHERE ROWID IN (
                SELECT q.ROWID
                FROM
                    quotes q JOIN bad_names bn ON q.source = bn.source AND q.symbol = bn.symbol AND q.timeframe = bn.timeframe AND q.day = bn.day
            );
            
            DROP TABLE bad_names;
            
            UPDATE config SET value = '3' WHERE name = 'version';
            
            COMMIT TRANSACTION;
            VACUUM;
        """)
        logging.info('Database conversion completed.')

    def save_day(self, source, symbol, timeframe, day_date, bar_data):
        assert isinstance(bar_data, OHLCV_day)

        logging.debug(f'saving to sql {source} {symbol} {timeframe} {day_date}')

        if self.compression_type == CompressionType.auto:
            if timeframe.value <= 1 * TIME_UNITS_IN_ONE_SECOND:
                compression_type = CompressionType.lz4
            elif timeframe.value <= 5 * 60 *  TIME_UNITS_IN_ONE_SECOND:
                compression_type = CompressionType.gzip
            else:
                compression_type = CompressionType.bz2
        else:
            compression_type = self.compression_type

        params = {
            'source': source,
            'symbol': symbol.lower(),
            'timeframe': timeframe,
            'day': self.day_to_int(day_date),
            'compression_type': compression_type.value
        }

        data_is_empty = bar_data.is_empty()
        for data_name in ('time', 'open', 'high', 'low', 'close', 'volume'):
            params[data_name] = b'' if data_is_empty else self.compress_numpy(bar_data.data[data_name], compression_type)

        cursor = self.sl3base.cursor()

        try:
            cursor.execute("""
                INSERT INTO quotes(source, symbol, timeframe, day, compression_type, time, open, high, low, close, volume)
                VALUES (:source, :symbol, :timeframe, :day, :compression_type, :time, :open, :high, :low, :close, :volume)
                """, params)
        except sqlite3.IntegrityError:
            logging.warning(f're-updating quotes: {source} {symbol} {timeframe:s} {day_date}')

    def load_day(self, source, symbol, timeframe, day_date):

        params = {
            'source': source,
            'symbol': symbol.lower(),
            'timeframe': timeframe,
            'day': self.day_to_int(day_date)
        }

        cursor = self.sl3base.cursor()
        query_result = cursor.execute("""
            SELECT
                time, open, high, low, close, volume, compression_type
            FROM
                quotes
            WHERE
                source = :source AND symbol = :symbol AND timeframe = :timeframe AND day = :day
        """, params)

        day_data = query_result.fetchone()
        if day_data is None:
            return None

        if len(day_data[0]) == 0:
            return OHLCV_day.empty_day(symbol, timeframe, source, day_date, False)

        compression_type = CompressionType(day_data[6])

        day_data_decompress = {
            'symbol': symbol,
            'timeframe': timeframe,
            'source': source,
            'is_incomplete_day': False
        }

        blob_types = [TIME_TYPE] + [PRICE_TYPE] * 4 + [VOLUME_TYPE]
        for i_blob, blob_name in enumerate(('time', 'open', 'high', 'low', 'close', 'volume')):
            blob_type = blob_types[i_blob]
            day_data_decompress[blob_name] = self.decompress_numpy(day_data[i_blob], blob_type, compression_type)

        return OHLCV_day(day_data_decompress)
