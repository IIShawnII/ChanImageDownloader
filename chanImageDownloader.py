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

import requests, os, json, sys, argparse

#all threads in a board
URL_THREADS = "https://8ch.net/{0}/threads.json"
#all posts in a thread
URL_POSTS = "https://8ch.net/{0}/res/{1}.json"
#all boards
URL_BOARDS = "https://8ch.net/boards.json"
#old image location
URL_OLD_IMAGE = "https://media.8ch.net/{0}/src/"
#new image location
URL_NEW_IMAGE = "https://media.8ch.net/file_store/"

debug = False

def toJson( response):
    try:
        json = response.json()
        return json
    except Exception as ex:
        print( 'Problem decoding json', file=sys.stderr)
        print( ex, file=sys.stderr)
        return False

def getURL( url, streaming=False):
    try:
        response = requests.get( url, stream=streaming)
        response.raise_for_status()
        return response
    except Exception as ex:
        print( 'Problem when getting: {0}'.format(url), file=sys.stderr)
        print( ex, file=sys.stderr)
    return False


def getThreadsInBoard( board):
    threads = getURL( URL_THREADS.format(board))
    if threads:
        return [ thread['no'] for page in threads.json() for thread in page[ 'threads']]
    return False


def getFilesInThread( board, thread):
    posts = getURL( URL_POSTS.format( board, thread))
    
    if not posts:
        return False

    postsJson = toJson( posts)
    
    if not postsJson:
        return False

    def getFileDetails( post):
        ext = post.get('ext', post)
        name = post.get('filename', post) + ext
        address = post.get('tim', post) + ext
        return {"name":name, "address":address}

    files = []
    for post in postsJson['posts']:
        if post.get('ext'):
            files.append( getFileDetails( post))
        if post.get('extra_files'):
            for extra_file in post.get('extra_files'):
                files.append( getFileDetails( extra_file))

    return files


def getFile( folder, board, thread, file):
    filepath = folder + file['name']
    if not os.path.exists( filepath):
        response = getURL( URL_NEW_IMAGE + file['address'], True);
        if not response:
            response = getURL( URL_OLD_IMAGE.format( board) + file['address'], True);
        with open( filepath, 'wb') as f:
            for chunk in r.iter_content( chunk_size=1024):
                if chunk:
                    f.write( chunk)
                    f.flush()
        r.close()
        return True
    return False

def processThread( board, thread):
    print( 'Board: {0}, Thread: {1:>4} getting image list'.format( board, str(  thread)))
    files = getFilesInThread( board, thread)
    if not files:
        print( 'Board: {0}, Thread: {1} No image or thread found'.format( board, str( thread)))
        return
    
    folder = './8ch/'+ board +'/'+ str(thread) + '/'
    if not os.path.exists( folder):
        os.makedirs( folder)
    for file in files:
        if getFile( folder, board, thread, file):
            print( 'GET [Board: {0}, Thread: {1}, File: {2}]'.format( board, thread, file['name']))
        elif debug:
            print( 'Exists [Board: {0}, Thread: {1}, File: {2}]'.format( board, thread, file['name']))


def processBoard( board):
    print( 'Board: {0} getting thread list'.format( board))
    threads = getThreadsInBoard( board)
    if not threads:
        return
    if debug:
        print( threads)
    for thread in threads:
        processThread( board, thread)

def configArgParse():
    parser = argparse.ArgumentParser( description='8chan Downloader')
    parser.add_argument('-b', metavar='Board', dest='board', type=str, nargs=1, help='*Required arg. name of the board to downlaod everything within, unless thread number is provided.', required=True)
    parser.add_argument('-t', metavar='Thread', dest='thread', type=int, nargs=1, help='Optional arg. thread number. if present only the thread provided will be downloaded.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Optional arg. show extra print outs.')
    return parser

if __name__ == '__main__':
    args = configArgParse().parse_args()
    if args.debug:
        debug = True
    if args.thread:
        processThread( args.board[0], args.thread[0])
    elif args.board:
        processBoard( args.board[0])