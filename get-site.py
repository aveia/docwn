#!/usr/bin/python
import os
import sys
import argparse


def system(cmd):
    print '\033[0;31m{}\033[0;0m'.format(cmd)
    os.system(cmd)

class SiteDownloader:

    def __init__(self, url):
        self.url = url
        self.downloaded = set([])

    def download(self):
        system('rm -rf tmp-site')
        os.mkdir('tmp-site')

        os.chdir('tmp-site')
        self._download(self.url)
        os.chdir('..')

    def _download(self, url):

        if url[:7] == 'http://':
            url = url[7:]
        if url[:8] == 'https://':
            url = url[8:]

        if url[-1] == '/':
            url += 'index.php'

        url = url.strip('/')

        filename, path = url[::-1].split('/', 1)
        filename = filename[::-1]
        path = path[::-1]


        system('mkdir -p {}'.format(path))
        cwd = os.getcwd()
        os.chdir(path)
        system('wget {}'.format(url))
        os.chdir(cwd)


    def _dummy_download(self, url):
        pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser('get site')
    parser.add_argument('-s', required=True, dest='url')

    args = parser.parse_args()

    downloader = SiteDownloader(args.url)
    downloader.download()

