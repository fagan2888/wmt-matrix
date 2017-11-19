#!/usr/bin/env python3

"""

# MOTIVATION



# VERSION HISTORY

- version 0.1.0

# LICENSE

WMT is licensed under the Apache 2.0 License.

# CREDITS

Originally written by Matt Post.
The official version can be found at github.com/mjpost/wmt.
"""

import re
import os
import sys
import csv
import math
import gzip
import tarfile
import logging
import urllib.request
import urllib.parse
import argparse

from collections import Counter, namedtuple
from typing import List

try:
    # SIGPIPE is not available on Windows machines, throwing an exception.
    from signal import SIGPIPE

    # If SIGPIPE is available, change behaviour to default instead of ignore.
    from signal import signal, SIG_DFL
    signal(SIGPIPE, SIG_DFL)

except ImportError:
    logging.warn('Could not import signal.SIGPIPE (this is expected on Windows machines)')

VERSION = '1.1.5'

# Where to store downloaded test sets.
# Define the environment variable $SACREBLEU, or use the default of ~/.sacrebleu.
#
# Querying for a HOME environment variable can result in None (e.g., on Windows)
# in which case the os.path.join() throws a TypeError. Using expanduser() is
# a safe way to get the user's home folder.
from os.path import expanduser
USERHOME = expanduser("~")
WMT = os.environ.get('WMT', os.path.join(USERHOME, '.wmt'))

# n-gram order. Don't change this.
NGRAM_ORDER = 4

# This defines data locations.
# At the top level are test sets.
# Beneath each test set, we define the location to download the test data.
# The other keys are each language pair contained in the tarball, and the respective locations of the source and reference data within each.
# Many of these are *.sgm files, which are processed to produced plain text that can be used by this script.
# The canonical location of unpacked, processed data is $SACREBLEU/$TEST/$SOURCE-$TARGET.{$SOURCE,$TARGET}
data = {
    'wmt17': {
        'description': 'Official evaluation data.',
        'cs-en': 'http://matrix.statmt.org/matrix/systems_list/1866',
        'de-en': 'http://matrix.statmt.org/matrix/systems_list/1868',
        'en-cs': 'http://matrix.statmt.org/matrix/systems_list/1867',
        'en-de': 'http://matrix.statmt.org/matrix/systems_list/1869',
        'en-fi': 'http://matrix.statmt.org/matrix/systems_list/1871',
        'en-lv': 'http://matrix.statmt.org/matrix/systems_list/1873',
        'en-ru': 'http://matrix.statmt.org/matrix/systems_list/1875',
        'en-tr': 'http://matrix.statmt.org/matrix/systems_list/1877',
        'en-zh': 'http://matrix.statmt.org/matrix/systems_list/1879',
        'fi-en': 'http://matrix.statmt.org/matrix/systems_list/1870',
        'lv-en': 'http://matrix.statmt.org/matrix/systems_list/1872',
        'ru-en': 'http://matrix.statmt.org/matrix/systems_list/1874',
        'tr-en': 'http://matrix.statmt.org/matrix/systems_list/1876',
        'zh-en': 'http://matrix.statmt.org/matrix/systems_list/1878',
    },
}


def _read(file, encoding='utf-8'):
    """Convenience function for reading compressed or plain text files.
    :param file: The file to read.
    :param encoding: The file encoding.
    """
    if file.endswith('.gz'):
        return gzip.open(file, 'rt', encoding=encoding)
    return open(file, 'rt', encoding=encoding)


def process_to_csv(rawfile, txtfile):
    """Processes raw matrix pages to CSV files.

    :param rawfile: the input HTML file
    :param txtfile: the plaintext CSV file
    """

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(open(rawfile), 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')

    logging.info("Processing {} to {}".format(rawfile, txtfile))
    headers = [x.find(text=True) for x in rows[0].find_all('th')]
    with open(txtfile, 'w') as csvfile:
        out = csv.DictWriter(csvfile, fieldnames=headers)
        out.writeheader()

        def leaf(node):
            if node.find('p'):
                return node.find('p').find(text=True)
            else:
                return node.find(text=True)

        for row in rows[1:]:
            values = [leaf(x) for x in row.find_all('td')]
            if len(headers) == len(values):
                out.writerow(dict(zip(headers, values)))
#                print(values)


def download_matrix_page(test_set, langpair=None):
    """Downloads the specified matrix page to the system location specified by the WMT environment variable.

    :param page: the test set to download
    :return: the set of processed files
    """

    # if not data.has_key(test_set):
    #     return None

    if langpair is None:
        for langpair in data[test_set].keys():
            download_matrix_page(test_set, langpair)
    else:
        dataset = data[test_set][langpair]
        outdir = os.path.join(WMT, test_set)
        rawdir = os.path.join(outdir, 'raw')
        if not os.path.exists(rawdir):
            logging.info('Creating {}'.format(rawdir))
            os.makedirs(rawdir)

        htmlpage = os.path.join(rawdir, os.path.basename(dataset))
        if not os.path.exists(htmlpage):
            # TODO: check MD5sum
            logging.info("Downloading {} to {}".format(dataset, htmlpage))
            with urllib.request.urlopen(dataset) as f, open(htmlpage, 'wb') as out:
                out.write(f.read())

        csvfile = os.path.join(outdir, '{}.{}.csv'.format(test_set, langpair))
        if True: # not os.path.exists(csvfile):
            process_to_csv(htmlpage, csvfile)

        return [x for x in csv.DictReader(open(csvfile))]


def main():
    arg_parser = argparse.ArgumentParser(description='WMT: tools for interacting with functions of the Conference on Machine Translation')
    arg_parser.add_argument('--test-set', '-t', type=str, default=None,
                            choices=data.keys(),
                            help='the test set to use')
    arg_parser.add_argument('--language-pair', '-l', dest='langpair', default=None,
                            help='source-target language pair (2-char ISO639-1 codes)')
    arg_parser.add_argument('--download', type=str, default=None,
                            help='download a test set and quit')
    arg_parser.add_argument('--quiet', '-q', default=False, action='store_true',
                            help='suppress informative output')
    arg_parser.add_argument('--encoding', '-e', type=str, default='utf-8',
                            help='open text files with specified encoding (default: %(default)s)')
    arg_parser.add_argument('-V', '--version', action='version',
                            version='%(prog)s {}'.format(VERSION))
    args = arg_parser.parse_args()

    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format='WMT: %(message)s')

    if args.download:
        download_matrix_page(args.download, args.langpair)
        sys.exit(0)

    if args.test_set is not None and args.test_set not in data:
        logging.error('The available test sets are: ')
        for ts in sorted(data.keys(), reverse=True):
            logging.error('  {}: {}'.format(ts, data[ts].get('description', '')))
        sys.exit(1)

    if args.test_set and (args.langpair is None or args.langpair not in data[args.test_set]):
        if args.langpair is None:
            logging.error('I need a language pair (-l).')
        elif args.langpair not in data[args.test_set]:
            logging.error('No such language pair "%s"', args.langpair)
        logging.error('Available language pairs for test set "{}": {}'.format(args.test_set, ', '.join(filter(lambda x: '-' in x, data[args.test_set].keys()))))
        sys.exit(1)

    if args.test_set:
        download_matrix_page(args.test_set, args.langpair)


if __name__ == '__main__':
    main()
