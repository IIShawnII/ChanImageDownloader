# Chan Image Downloader
A python program for downloading images from 4chan style sites

for now only 8chan works

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
