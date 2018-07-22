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

def rsplit(str, delimiter=None, max=-1):
    pieces = str[::-1].split(delimiter, max)
    for x in range(0, len(pieces)):
        pieces[x] = pieces[x][::-1]
    pieces.reverse()
    return pieces

class SiteDownloader:

    def __init__(self, url):

        if url[:7] == 'http://':
            self.scheme = 'http'
            self.uri = url[7:]
        elif url[:8] == 'https://':
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
        shexec('rm -rf tmp-site')
        os.mkdir('tmp-site')
        os.chdir('tmp-site')
        self.root_path = os.getcwd()

    def get_root(self):
        return '{}://{}'.format(self.scheme, self.uri)

    def download_file(self, url):

        print green('downloading: ' + url)

        cropped_url = url.replace(self.get_root(), '')
        print green('cropped {}'.format(cropped_url))

        split = rsplit(cropped_url, '/', 1)

        if len(split) > 1:
            path, filename = split
            path += '/'
            shexec('mkdir -p {}'.format(path))
            os.chdir(path)
        elif len(split) == 1:
            if split[0] == '':
                path = ''
                filename = 'index.html'
            else:
                path = ''
                filename = split[0]

        shexec('wget {}'.format(url))
        self.downloaded.add(url)

        with open(filename) as f:
            content = f.read()

        os.chdir(self.root_path)

        return path, content


    def download(self):

        stack = []
        stack.append(self.get_root())

        dl = 0
        max_dl = 20

        while (stack):

            if dl >= max_dl:
                break

            url = stack.pop()
            url = rsplit(url, '#')[0]
            url = rsplit(url, '?')[0]

            if url in self.downloaded:
                print orange('downloaded: ' + url)
                continue

            path, content = self.download_file(url)

            for m in re.finditer('href=[\'"](.+?)[\'"]', content):
                href = m.group(1)
                print blue(href)
                if href[:len(self.scheme)] == self.scheme:
                    if href[:len(self.get_root())] == self.get_root():
                        stack.append(href)
                elif href[0] == '.':
                    pass
                else:
                    new_url = '{}{}{}'.format(self.get_root(), path, href)
                    if new_url not in self.downloaded:
                        stack.append(new_url)

            dl += 1

        print 'done!'


if __name__ == '__main__':

    parser = argparse.ArgumentParser('get site v0.1')
    parser.add_argument('-s', required=True, dest='url')

    args = parser.parse_args()

    downloader = SiteDownloader(args.url)
    downloader.download()

