#!/usr/bin/python3
"""
Use: ./chanimagedownloader.py [-h] -b Board [-t Thread] [-d]

8chan Downloader

Required arguments:
  -b Board    name of the board to downlaod everything within,
              unless thread number is provided.
              
Optional arguments:
  -h, --help  show this help message and exit
  -t Thread   thread number. if present only the thread provided
              will be downloaded.
  -d          show extra print outs.
"""

import os
import sys
import requests
import argparse

# all threads in a board
URL_THREADS = "https://8ch.net/{0}/threads.json"
# all posts in a thread
URL_POSTS = "https://8ch.net/{0}/res/{1}.json"
# all boards
URL_BOARDS = "https://8ch.net/boards.json"
# old image location
URL_OLD_IMAGE = "https://media.8ch.net/{0}/src/"
# new image location
URL_NEW_IMAGE = "https://media.8ch.net/file_store/"

debug = False


def to_json(response):
    try:
        decode = response.json()
        return decode
    except Exception as ex:
        print('Problem decoding response', file=sys.stderr)
        print(ex, file=sys.stderr)
        return False


def get_url(url, streaming=False):
    try:
        response = requests.get(url, stream=streaming)
        response.raise_for_status()
        return response
    except Exception as ex:
        print('Problem when getting: {0}'.format(url), file=sys.stderr)
        print(ex, file=sys.stderr)
    return False


def get_threads_in_board(board):
    threads = get_url(URL_THREADS.format(board))
    if threads:
        return [thread['no'] for page in to_json(threads) for thread in page['threads']]
    return False


def get_files_in_thread(board, thread):
    posts = get_url(URL_POSTS.format(board, thread))

    if not posts:
        return False

    posts_json = to_json(posts)

    if not posts_json:
        return False

    def get_file_details(post_dic):
        ext = post_dic.get('ext', None)
        name = post_dic.get('filename', None) + ext
        address = post_dic.get('tim', None) + ext
        return {"name": name, "address": address}

    files = []
    for post in posts_json['posts']:
        if post.get('ext'):
            files.append(get_file_details(post))
        if post.get('extra_files'):
            for extra_file in post.get('extra_files'):
                files.append(get_file_details(extra_file))

    return files


def get_file(folder, board, file):
    file_path = folder + file['name']
    if not os.path.exists(file_path):
        response = get_url(URL_NEW_IMAGE + file['address'], True)
        if not response:
            response = get_url(URL_OLD_IMAGE.format(board) + file['address'], True)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return True
    return False


def process_thread(board, thread):
    print('Board: {0}, Thread: {1:>4} getting image list'.format(board, str(thread)))
    files = get_files_in_thread(board, thread)
    if not files:
        print('Board: {0}, Thread: {1} No image or thread found'.format(board, str(thread)))
        return

    folder = './8ch/' + board + '/' + str(thread) + '/'
    if not os.path.exists(folder):
        os.makedirs(folder)
    for file in files:
        if get_file(folder, board, file):
            print('GET [Board: {0}, Thread: {1}, File: {2}]'.format(board, thread, file['name']))
        elif debug:
            print('Exists [Board: {0}, Thread: {1}, File: {2}]'.format(board, thread, file['name']))


def process_board(board):
    print('Board: {0} getting thread list'.format(board))
    threads = get_threads_in_board(board)
    if not threads:
        return
    if debug:
        print(threads)
    for thread in threads:
        process_thread(board, thread)


def config_argparse():
    parser = argparse.ArgumentParser(description='8chan Downloader')
    parser.add_argument('-b', metavar='Board', dest='board', type=str, nargs=1,
                        help='*Required arg. name of the board to downlaod everything within, unless thread number is provided.',
                        required=True)
    parser.add_argument('-t', metavar='Thread', dest='thread', type=int, nargs=1,
                        help='Optional arg. thread number. if present only the thread provided will be downloaded.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Optional arg. show extra print outs.')
    return parser


if __name__ == '__main__':
    args = config_argparse().parse_args()
    if args.debug:
        debug = True
    if args.thread:
        process_thread(args.board[0], args.thread[0])
    elif args.board:
        process_board(args.board[0])
