import hashlib
from os import path
import shutil
from config import Config
from torrent import Torrent
import hashlib


class FileManager:
    """
    The file manager class handles writes and reads from tmp, original and routing table.
    It also creates pointers to routing table, as well as read and write blocks/pieces of data.
    """

    def __init__(self, torrent, peer_id):
        """
        Class constructor
        :param torrent:
        :param peer_id:
        """
        self.torrent = torrent
        self.peer_id = peer_id
        self.config = Config()
        self.path = self.torrent.path_to_temp()
        self.path_to_original_file = self.torrent.path_to_original()
        self.file_size = self.torrent.file_length()
        self.piece_size = self.torrent.piece_size()
        self.hash_info = self.torrent.info_hash()


    def create_tmp_file(self):
        """
        Creates a temporal file to flush the pieces. (i.e ages.tmp)
        :return:
        """
        with open(self.path, "wb") as out:
            out.truncate(self.file_size)

    def set_path_to_original_file(self, path):
        """
        set path to resources/shared/
        :param path:
        :return:
        """
        self.path_to_original_file = path

    def hash(self, data):
        """

        :param data:
        :return:
        """
        sha1 = hashlib.sha1()
        sha1.update(data)
        data_hashed = sha1.hexdigest()
        return data_hashed

    def get_block(self, piece_index, offset, length, path=None):
        """
        TODO: gets a block from the file in the path given as parameter
        :param piece_index: the index of the piece
        :param offset: the begin offset of the block in that piece
        :param length: the length of the block
        :param path: Note that paths may be only the original file (i.e ages.txt) or
                     the tmp file (i.e ages.tmp)
        :return:
        """
        block = None
        file = open(path, "r")
        read_size = self.piece_size
        index = 1
        while read_size < self.file_size:
            block = file.read(self.piece_size)
            if index == piece_index:
                return block[offset:offset + length]
            index += 1
            read_size += self.piece_size

        return block

    def get_piece(self, blocks):
        """
        TODO: Converts a list of blocks in a piece
        :param blocks: a list of blocks
        :return: the piece
        """
        piece = None
        # your code here
        return piece

    def flush_block(self, piece_index, block_index, block):
        """
        TODO: writes a block into the routing table. Each file in blocks folder representing a routing table must be
              named with the hash info of the torrent file.
              Each entry in routing table has the following format:
              <pointer><delimiter><block>
              pointer: A SHA1 hash of the hash info of the torrent file, piece index and block index
              delimiter: $$$
              block: the data of the block

        :param piece_index:
        :param block_index:
        :param block:
        :return: VOID
        """
        pointer = self.pointer(self.torrent.info_hash(), piece_index, block_index)
        with open(self.torrent.path_to_tmp_blocks, "a") as out:
            data = pointer + "$$$" + block
            out.write(data)

    def pointer(self, hash_info, piece_index, block_index):
        """
        Creates a pointer for a specific block
        :param hash_info:
        :param piece_index:
        :param block_index:x
        :return:
        """
        data = str(piece_index) + str(block_index) + hash_info
        data_encoded = str.encode(data)
        return str.encode(self.hash(data_encoded))

    def flush_piece(self, piece_index, piece):
        """
        TODO: write a piece in tmp file once the piece is validated with the hash of the piece
        :param piece_index:
        :param piece:
        :return: VOID
        """
        with open(self.torrent.path_to_temp(), "a") as out:
            out.write(piece)

    def get_pointers(self, hash_info, piece_index):
        """
        TODO: gets all the pointers representing a piece in the routing table
        :param hash_info:
        :param piece_index:
        :return: a list of pointers to the blocks in the same piece
        """
        pointers = []
        rt_file_path = self.torrent.path_to_tmp_blocks() + "/" + hash_info
        rt_file = open(rt_file_path, "r")
        for line in rt_file:
            pointer = line.split("$$$")[0]
            pointers.append(pointer)

        return pointers


    def decode_piece(self, piece_index):
        """
        TODO: decodes a piece from the routing table once all the blocks from that piece are completed
        :param piece_index:
        :return: the piece
        """
        piece = None
        # your code here
        return piece

    def piece_offset(self, piece_index):
        """
        :param piece_index:
        :return:
        """
        return piece_index * self.piece_size

    def block_offset(self, block_index, block_length):
        """
        :param block_index:
        :param block_length:
        :return:
        """
        return block_index * block_length

    def block_index(self, begin):
        return begin/self.torrent.block_size()

    def piece_validated(self, piece, piece_index):
        hashed_torrent_piece = self.torrent.piece(piece_index)
        hashed_piece = self.hash(piece)
        return hashed_torrent_piece == hashed_piece

    def move_tmp_to_shared(self):
        file_shared_path = "resources/shared/" + self.torrent.file_name()
        if not path.exists(file_shared_path):
            shutil.move(self.path, file_shared_path)

    def path_exist(self, path_to_file):
        return path.exists(path_to_file)

    def shared_path(self):
        file_name = self.torrent.file_name()
        shared_path = self.config.get_value("resources", "shared_files") + file_name
        if self.path_exist(shared_path):
            return shared_path
        return None