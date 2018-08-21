#!/usr/bin/env python2
"""
Logpuzzle exercise

Copyright 2010 Google Inc.
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0

Google's Python Class
http://code.google.com/edu/languages/google-python-class/

Given an apache logfile, find the puzzle urls and download the images.

Here's what a puzzle url looks like:
10.254.254.28 - - [06/Aug/2007:00:13:48 -0700] "GET /~foo/puzzle-bar-aaab.jpg HTTP/1.0" 302 528 "-" "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6" 
# noqa
# ^ Added above line because line 15 needs to stay intact to make sense
"""

import os
import re
import sys
import urllib
import argparse


def sort_urls(url):
    """Function used as key when sorted.
    Sorts by second group of matches in ()'s.
    Returns list of targeted words if match or url if no match."""
    match = re.search(r'puzzle/\w+-(\w+)-(\w+)\.\w+', url)
    return match.group(2) if match else url


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""
    underscore = filename.find('_')
    hostname = filename[underscore + 1:]
    with open(filename, 'r') as f:
        text = f.read()
        f.close()
        partial_paths = re.findall(r'[/]edu\S+\.\w+', text)
        full_paths = map(
            lambda p_path: 'http://' + hostname + p_path, partial_paths
        )
    return sorted(list(set(full_paths)), key=sort_urls)


def download_images(img_urls, dest_dir):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    with open(os.path.join(dest_dir, 'index.html'), 'w+') as f:
        f.write('<html><body>')
        index = 0
        for img_url in img_urls:
            new_name = 'img{}'.format(index)
            urllib.urlretrieve(img_url, os.path.join(dest_dir, new_name))
            f.write('<img src={}>'.format(new_name))
            index += 1
        f.write('</body></html>')
        f.close()


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--todir',  help='destination directory for downloaded images')
    parser.add_argument('logfile', help='apache logfile to extract urls from')

    return parser


def main(args):
    """Parse args, scan for urls, get images from urls"""
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    img_urls = read_urls(parsed_args.logfile)

    if parsed_args.todir:
        download_images(img_urls, parsed_args.todir)
    else:
        print('\n'.join(img_urls))


if __name__ == '__main__':
    main(sys.argv[1:])
