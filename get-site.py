#!/usr/bin/python

import argparse
import os
import re
import sys

def shexec(cmd):
    print '\033[0;31m{}\033[0;0m'.format(cmd)
    return os.system(cmd)

def green(str):
    return '\033[0;32m{}\033[0;0m'.format(str)

def orange(str):
    return '\033[0;33m{}\033[0;0m'.format(str)

def blue(str):
    return '\033[0;34m{}\033[0;0m'.format(str)

def error(msg):
    raise Error('{}: {}'.format(__file__, msg))

class SiteDownloader:

    def __init__(self, url, out):

        self.output = out

        if url.startswith('http://'):
            self.scheme = 'http'
            self.uri = url[7:]
        elif url.startswith('https://'):
            self.scheme = 'https'
            self.uri = url[8:]
        else:
            error('unrecognized url scheme')

        if url[-1] == '/':
            if os.system('curl -f {}index.html'.format(url)) == 0:
                self.page_type = 'html'
            elif os.system('curl -f {}index.php'.format(url)) == 0:
                self.page_type = 'php'
            else:
                error('unrecognized page type')
        else:
            error('unsupported url')

        self.downloaded = set()
        shexec('rm -rf ' + self.output)
        os.mkdir(self.output)
        os.chdir(self.output)
        self.root_path = os.getcwd()

    def get_root(self):
        return '{}://{}'.format(self.scheme, self.uri)

    def download_file(self, url):

        print green('downloading: ' + url)

        cropped_url = url.replace(self.get_root(), '')
        print green('cropped {}'.format(cropped_url))

        split = cropped_url.rsplit('/', 1)

        if len(split) == 2:
            path, filename = split
            path += '/'
            shexec('mkdir -p {}'.format(path))
            os.chdir(path)
        elif len(split) == 1:
            path = ''
            filename = split[0] or 'index.html'

        retcode = shexec('wget {}'.format(url))

        self.downloaded.add(url)

        if retcode:
            os.chdir(self.root_path)
            return None, None

        with open(filename) as f:
            content = f.read()

        os.chdir(self.root_path)

        return path, content

    def download(self):

        to_download = set()
        to_download.add(self.get_root() + 'index.' + self.page_type)

        while to_download:

            url = to_download.pop()
            url = url.rsplit('#', 1)[0]
            url = url.rsplit('?', 1)[0]

            if url in self.downloaded:
                print orange('already downloaded: ' + url)
                continue

            path, content = self.download_file(url)

            if not content:
                continue

            for m in re.finditer('(src|href)=[\'"](.+?)[\'"]', content):
                href = m.group(2)

                if href.startswith('http://') \
                    or href.startswith('https://') \
                    or href.startswith('mailto:') \
                    or href.startswith('.'):
                    print orange('ignored: ' + href)
                    continue

                print blue(href)
                if not href.startswith(self.get_root()):
                    href = '{}{}{}'.format(self.get_root(), path, href)

                to_download.add(href)

        print 'done!'

if __name__ == '__main__':

    parser = argparse.ArgumentParser('get site v0.3')
    parser.add_argument('-s', required=True, dest='url')
    parser.add_argument('-o', required=False, dest='out', default='tmpsite')

    args = parser.parse_args()

    downloader = SiteDownloader(args.url, args.out)
    downloader.download()
