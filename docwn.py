#!/usr/bin/python
# -*- encoding: utf-8 -*-

from __future__ import print_function
import argparse
import codecs
import os
import re
import sys

def red(text):
    return '\033[0;31m{}\033[0;0m'.format(text)

def green(text):
    return '\033[0;32m{}\033[0;0m'.format(text)

def orange(text):
    return '\033[0;33m{}\033[0;0m'.format(text)

def blue(text):
    return '\033[0;34m{}\033[0;0m'.format(text)

def pink(text):
    return '\033[0;35m{}\033[0;0m'.format(text)

def error(msg):
    print(red('{}: {}'.format(__file__, msg)))
    sys.exit(1)

def shexec(cmd):
    print(orange('shexec: ' + cmd))
    retcode = os.system(cmd)
    while retcode > 255 and not retcode & 255:
        retcode = (retcode >> 8) & 255
    return retcode & 255

def mkdir(path):
    if not os.path.isdir(path):
        shexec('mkdir -p "{}"'.format(path))

class SiteDownloader(object):

    def __init__(self, url, output):

        self.output = output.rstrip('/') + '/'

        url_split = [x for x in re.split(r'^(https?)://', url) if x]
        print(url_split)
        if len(url_split) == 2:
            self.scheme, uri = url_split
        else:
            error('unrecognized url scheme')

        uri_split = uri.split('/', 1)
        self.domain = uri_split[0]
        path = '/' + uri_split[1] if len(uri_split) == 2 else '/'

        self.root_path = path.rsplit('/', 1)[0] + '/'

        shexec('rm -rf "{}"'.format(self.output))
        mkdir(self.output)
        self.local_root_path = os.getcwd()

        self.downloaded = set()
        self.to_download = set()

        self.to_download.add(self.get_root())

    def get_root(self):
        return '{}://{}{}'.format(self.scheme, self.domain, self.root_path)

    def download_file(self, url):

        if re.match(r'^{}'.format(self.get_root()), url):
            filepath = url.replace(self.get_root(), '', 1)
        else:
            print(red('won\'t download: ' + url))
            return None, None

        print(green('downloading: ' + url))

        split = filepath.rsplit('/', 1)
        path = split[0] + '/' if len(split) == 2 else ''
        filename = split[-1] or 'index.html'

        dirpath = self.output + path
        mkdir(dirpath)

        local_filepath = dirpath + filename

        retcode = shexec('wget --no-verbose -O '
            '"{}" "{}"'.format(local_filepath, url))

        self.downloaded.add(url)

        if retcode in [2, 130]:
            error('aborted!')

        if retcode:
            print(red('failed do download: ' + url))
            return None, None

        content = ''
        for e in ['utf-8', 'latin-1', 'cp1252', 'cp1250']:
            try:
                with codecs.open(local_filepath, encoding=e) as f:
                    content = f.read()
                break
            except IOError:
                print(red('failed do open: ' + local_filepath))
                return None, None
            except:
                pass

        return path, content

    def clean_up(self, url):
        url = url.rsplit('#', 1)[0]
        url = url.rsplit('?', 1)[0]
        while re.search(r'/[^/]+/\.\./', url):
            url = re.sub(r'/[^/]+/\.\./', '/', url)
        return url

    def download(self):

        to_download = set()
        to_download.add(self.get_root())

        errors = 0

        while to_download:

            print(pink('number of remaining files: ' \
                '{}\n'.format(len(to_download))))

            url = to_download.pop()

            path, content = self.download_file(url)

            if content is None:
                errors += 1
                print()
                continue

            new_files = set()
            ignored = set()

            for match in \
                re.finditer(r'(src|href|SRC|HREF)=[\'"](.+?)[\'"]', content):

                href = match.group(2)

                if href.startswith('mailto:'):
                    ignored.add(href)
                    continue

                if href.startswith('/'):
                    href = '{}://{}{}'.format(self.scheme, self.domain, href)
                elif re.match(r'^[a-z]+://', href):
                    pass
                elif not href.startswith(self.get_root()):
                    href = '{}{}{}'.format(self.get_root(), path, href)

                href = self.clean_up(href)

                if href not in self.downloaded \
                    and href not in to_download:
                    to_download.add(href)
                    new_files.add(href.rsplit('/')[-1])

            if ignored:
                print(orange('ignored: ' + ' | '.join(ignored)))

            if new_files:
                print(blue('new files: ' + ' | '.join(new_files)))

            print()

        print(green('done! no. of errors: ' + str(errors)))

if __name__ == '__main__':

    parser = argparse.ArgumentParser('docwn v0.4')
    parser.add_argument('-s', required=True, dest='url')
    parser.add_argument('-o', required=False, dest='out', default='tmpsite')

    args = parser.parse_args()

    downloader = SiteDownloader(args.url, args.out)
    downloader.download()
