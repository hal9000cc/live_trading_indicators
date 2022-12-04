import os
import os.path as path
import numpy as np
import zlib
import construct as cs
from ..exceptions import *

FILE_VERSION = 2


class BlockCache:

    def __init__(self, file_signature):

        assert type(file_signature) == bytes
        self.file_signature = file_signature

        self.open_file = None
        self.open_file_name = None
        self.open_file_n_blocks = None
        self.open_file_block_offset = None
        self.open_file_block_length = None

    def get_header_struct(self):
        return cs.Struct(
            'signature' / cs.Const(self.file_signature),
            'file_version' / cs.Int16ub,
            'n_blocks' / cs.Int16ub
        )

    @staticmethod
    def get_allocate_table_struct(n_blocks):
        assert type(n_blocks) == int
        return cs.Struct(
            'block_offset' / cs.Int32sb[n_blocks],
            'block_length' / cs.Int32sb[n_blocks]
        )

    def build_header(self):

        header = {
            'file_version': FILE_VERSION,
            'n_blocks': self.open_file_n_blocks
        }

        return self.get_header_struct().build(header)

    def build_allocate_table(self):
        return self.get_allocate_table_struct(self.open_file_n_blocks).build({
            'block_offset': self.open_file_block_offset,
            'block_length': self.open_file_block_length
        })

    def flush_headers(self):
        assert self.open_file is not None

        self.open_file.seek(0)

        self.open_file.write(self.build_header())
        self.open_file.write(self.build_allocate_table())

        self.open_file.flush()

    def create_new_file(self, file_name, n_blocks):
        assert type(n_blocks) == int

        file_folder = path.split(file_name)[0]
        if not path.isdir(file_folder):
            os.makedirs(file_folder)

        self.open_file_n_blocks = n_blocks
        self.open_file_block_offset = -np.ones(n_blocks, dtype=np.int32)
        self.open_file_block_length = np.zeros(n_blocks, dtype=np.int32)

        file_name_tmp = f'{file_name}.tmp'
        self.open_file = open(file_name_tmp, 'wb+')
        self.flush_headers()
        self.close_block_file()

        if path.isfile(file_name):
            os.remove(file_name)

        os.rename(file_name_tmp, file_name)

    def open_block_file(self, file_name):

        if self.open_file is not None:

            if self.open_file_name == file_name:
                return

            self.close_block_file()

        open_file = None

        try:

            open_file = open(file_name, 'rb+')

            header_struct = self.get_header_struct()
            header = header_struct.parse(open_file.read(header_struct.sizeof()))

            if header.signature != self.file_signature:
                raise LTIExceptionBadDataCachFile()

            self.open_file_n_blocks = header.n_blocks

            allocate_table_struct = self.get_allocate_table_struct(header.n_blocks)
            allocate_table = allocate_table_struct.parse(open_file.read(allocate_table_struct.sizeof()))

            self.open_file_block_offset = allocate_table.block_offset
            self.open_file_block_length = allocate_table.block_length
            self.open_file_name = file_name
            self.open_file = open_file

        except Exception as error:
            if open_file is not None:
                open_file.close()
            raise

    def close_block_file(self):

        if self.open_file is None:
            return

        self.open_file.close()
        self.open_file = None

    def __del__(self):
        self.close_block_file()

    def save_block(self, file_name, block_index, n_blocks, data):

        if not path.isfile(file_name):
            self.create_new_file(file_name, n_blocks)

        self.open_block_file(file_name)

        assert self.open_file_block_offset[block_index] < 0

        block_offset = self.open_file.seek(0, 2)
        block_length = self.open_file.write(zlib.compress(data))

        self.open_file_block_offset[block_index] = block_offset
        self.open_file_block_length[block_index] = block_length
        self.flush_headers()

    def load_block(self, file_name, block_index):

        if not path.isfile(file_name):
            return None

        self.open_block_file(file_name)

        block_offset = self.open_file_block_offset[block_index]
        if block_offset < 0:
            return None

        self.open_file.seek(block_offset)
        buffer = self.open_file.read(self.open_file_block_length[block_index])

        return zlib.decompress(buffer)
