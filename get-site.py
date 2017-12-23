#!/usr/bin/python
import os
import sys
import argparse

class SiteDownloader:

    def __init__(self, url):
        self.url = url
        self.downloaded = set([])

    def download():






if __name__ == '__main__':

    parser = argparse.ArgumentParser('get site')
    parser.add_argument('-s', required=True, dest='url')

    args = parser.parse()

    downloader = SiteDownloader(args.url)
    downloader.download()

