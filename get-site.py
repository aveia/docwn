#!/usr/bin/python
# -*- encoding: utf-8 -*-

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
    return os.system(cmd)

class SiteDownloader(object):

    def __init__(self, url, out):

        self.output = out

        url_split = [x for x in re.split(r'^(https?)://', url) if x]
        if len(url_split) == 2:
            self.scheme, self.uri = url_split
        else:
            error('unrecognized url scheme')

        if url[-1] != '/':
            error('unsupported url')

        self.downloaded = set()
        shexec('rm -rf ' + self.output)
        os.mkdir(self.output)
        os.chdir(self.output)
        self.root_path = os.getcwd()

    def get_root(self):
        return '{}://{}'.format(self.scheme, self.uri)

    def download_file(self, url):

        print(green('downloading: ' + url))

        cropped_url = url.replace(self.get_root(), '')
        print(green('cropped: {}'.format(cropped_url)))

        split = cropped_url.rsplit('/', 1)

        if len(split) == 2:
            path = split[0] + '/'
            filename = split[1] or 'index.html'
            shexec('mkdir -p {}'.format(path))
        elif len(split) == 1:
            path = ''
            filename = split[0] or 'index.html'

        if path:
            os.chdir(path)

        retcode = shexec('wget -O "{}" "{}"'.format(filename, url))

        self.downloaded.add(url)

        if retcode:
            print(red('failed do download: ' + url))
            os.chdir(self.root_path)
            return None, None

        content = ''
        for e in ['utf-8', 'latin1']:
            try:
                with codecs.open(filename, encoding=e) as f:
                    content = f.read()
                break
            except:
                pass

        os.chdir(self.root_path)

        return path, content

    def download(self):

        to_download = set()
        to_download.add(self.get_root())

        errors = 0

        while to_download:

            print(pink('number of remaining files: ' + str(len(to_download))))

            url = to_download.pop()
            url = url.rsplit('#', 1)[0]
            url = url.rsplit('?', 1)[0]

            if url in self.downloaded:
                print(orange('already downloaded: ' + url))
                continue

            path, content = self.download_file(url)

            if content is None:
                errors += 1
                continue

            new_files = set()
            ignored = set()

            for match in \
                re.finditer(r'(src|href|SRC|HREF)=[\'"](.+?)[\'"]', content):

                href = match.group(2)

                if not href.startswith(self.get_root()) \
                    and (href.startswith('http://') \
                        or href.startswith('https://') \
                        or href.startswith('mailto:') \
                        or href.startswith('/')):
                    ignored.add(href)
                    continue

                new_files.add(href)

                if not href.startswith(self.get_root()):
                    href = '{}{}{}'.format(self.get_root(), path, href)

                while re.search(r'/[^/]+/\.\./', href):
                    href = re.sub(r'/[^/]+/\.\./', '/', href)

                to_download.add(href)

            if ignored:
                print(orange('ignored: ' + ' | '.join(ignored)))

            if new_files:
                print(blue('new files: ' + ' | '.join(new_files)))

        print(green('done! no. of errors: ' + str(errors)))

if __name__ == '__main__':

    parser = argparse.ArgumentParser('get site v0.3.1')
    parser.add_argument('-s', required=True, dest='url')
    parser.add_argument('-o', required=False, dest='out', default='tmpsite')

    args = parser.parse_args()

    downloader = SiteDownloader(args.url, args.out)
    downloader.download()
