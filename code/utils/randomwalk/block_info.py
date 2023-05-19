from sqlite3 import Cursor

from sympy import re


class Block_info:
    def __init__(self, mined_time):
        self.mined_time = mined_time
        self.published_time = None

    def set_publish_time(self, published_time):
        self.published_time = published_time

    def get_difference(self):
        if self.published_time == None:
            raise ArithmeticError("Publish time not set yet.")
        else:
            if self.published_time - self.mined_time > 200:
                print(self.published_time, self.mined_time)
            assert self.published_time - self.mined_time >= 0
            return self.published_time - self.mined_time

    def get_publish_time(self):
        return self.published_time


class Block_info_list:
    def __init__(self):
        self.block_list = []
        self.cursor = 0
        self.cursor_for_withholding = 0

    def add_elements(self, list_of_mined_time, block_type):
        for mined_time_iter in list_of_mined_time:
            if block_type == "adversary":
                self.block_list.append(Block_info(mined_time_iter))
            elif block_type == "honest":
                self.block_list.append(Block_info(mined_time_iter))
                self.block_list[self.cursor].set_publish_time(mined_time_iter)
                self.cursor += 1

    def set_publish_time(self, published_times):
        for published_time_iter in published_times:
            self.block_list[self.cursor].set_publish_time(published_time_iter)
            self.cursor += 1

    def get_publish_time_by_index(self, index):
        return self.block_list[index].get_publish_time()

    def get_num_of_published_block(self):
        published_block_num = 0
        for idx, block_info_iter in enumerate(self.block_list):
            if block_info_iter.published_time != None:
                published_block_num += 1
            else:
                break
        return published_block_num

    def return_time_difference(self):
        time_diff = []
        for idx, block_info_iter in enumerate(self.block_list):
            try:
                # get current block time difference.
                time_difference_iter = block_info_iter.get_difference()
            # if visit to the withheld block (without publish time),
            # set the cursor to current block.
            except ArithmeticError as excp:
                assert str(excp) == "Publish time not set yet."
                # cursor is move with setting publish time, make sure the cursor is consistent with the first block without publishing time.
                assert idx == self.cursor, "idx:{}, cursor:{}".format(idx, self.cursor)
                break
            else:

                time_diff.append(time_difference_iter)
        return time_diff

    def delete_block(self, block_num):
        if block_num > 0:
            self.block_list = self.block_list[block_num:]
            if self.cursor - block_num < 0:
                self.cursor = 0
            else:
                self.cursor -= block_num

    def __str__(self):
        str = "cursor:{}\n".format(self.cursor)
        for block_info_iter in self.block_list:
            str += "generation time: {}, publish time: {}\n".format(
                block_info_iter.mined_time, block_info_iter.published_time
            )
        return str
