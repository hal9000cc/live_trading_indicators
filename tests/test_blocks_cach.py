import pytest
import numpy as np
import os.path as path
import hashlib
from src.live_trading_indicators.datasources.blocks_cach import BlockCash


def get_data(i_block):
    return b''.join([hashlib.md5(bytes(f'block {i_block}' * i, encoding="utf-8")).digest() for i in range(1000)])


def test_blocks_cach_1(empty_test_folder):

    n_blocks = 50
    test_file_name = path.join(empty_test_folder, 'test.dat')

    datas = np.arange(n_blocks)
    np.random.shuffle(datas)

    blocks_cach = BlockCash(b'test')

    for i_block in datas:
        blocks_cach.save_block(test_file_name, i_block, n_blocks, get_data(i_block))

    for i_block in datas:
        data = blocks_cach.load_block(test_file_name, i_block)
        assert data == get_data(i_block)


def test_blocks_cach_2(empty_test_folder):

    n_blocks = 50

    datas = np.arange(n_blocks)
    np.random.shuffle(datas)

    blocks_cach = BlockCash(b'test')

    for i_block in datas:
        test_file_name = path.join(empty_test_folder, f'test{i_block // 10}.dat')
        blocks_cach.save_block(test_file_name, i_block, n_blocks, get_data(i_block))

    for i_block in datas:
        test_file_name = path.join(empty_test_folder, f'test{i_block // 10}.dat')
        data = blocks_cach.load_block(test_file_name, i_block)
        assert data == get_data(i_block)
