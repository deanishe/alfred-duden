#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-03
#

"""
"""

from __future__ import print_function, unicode_literals

import sys
import urllib
import re
import htmlentitydefs
from hashlib import md5


from workflow import web, Workflow, ICON_WARNING
from bs4 import BeautifulSoup as BS


# USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
USER_AGENT = 'curl/7.2'

BASE_URL = b'http://www.duden.de'
SEARCH_URL = b'{}/suchen/dudenonline/{{query}}'.format(BASE_URL)

MAX_CACHE_AGE = 3600  # 1 hour
MIN_QUERY_LENGTH = 2
log = None


def unescape(text):
    """Replace HTML entities with Unicode characters

    From: http://effbot.org/zone/re-sub.htm#unescape-html
    """

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)


def flatten(elem):
    """Return the string contents of partial BS elem tree

    :param elem: BeautifulSoup ``Tag`` or ``NavigableText``
    :returns: Flattened Unicode text contained in subtree

    """

    content = []

    for e in elem.contents:
        if hasattr(e, 'string'):
            content.append(e.string.strip())

    return unescape(re.sub(r'\s+', ' ', ' '.join(content)))


def lookup(query):
    """Get results matching ``query`` from duden.de

    :param query: Search term to look up
    :type query: ``unicode``
    :returns: (possibly empty) list of search results
    :rtype: ``list``

    """

    results = []

    url = SEARCH_URL.format(query=urllib.quote(query.encode('utf-8')))
    log.debug(url)

    r = web.get(url, headers={'User-Agent': USER_AGENT})
    # Duden sends 404 if there are no results
    if r.status_code == 404:
        return results
    r.raise_for_status()

    # Parse results
    soup = BS(r.content, b'html5lib')
    # elems = soup.fetch('section', 'wide')
    # log.debug(soup.prettify())
    elems = soup.find_all('section', {'class': 'wide'})
    # elems = soup.select('section.wide')

    for elem in elems:
        log.debug('elem : %s', elem.prettify())
        result = {}
        header = elem.find('h2')
        if header is None:
            continue

        link = header.find('a')

        result['term'] = flatten(link)
        result['url'] = '{}{}'.format(BASE_URL, link['href'])

        description_elem = elem.find('p')

        log.debug('description : %r', description_elem)

        description = flatten(description_elem)

        # Remove Worttrennung
        i = description.find('|')
        if i > -1:
            i = description.find(' ', i)
            description = description[i:].strip()

        result['description'] = description

        # log.debug('result : {}'.format(pformat(result)))
        results.append(result)

    log.debug('{} results for `{}`'.format(len(results), query))

    return results


def main(wf):
    query = wf.args[0]
    if len(query) < MIN_QUERY_LENGTH:
        wf.add_item('Query too short', 'Keep typing…', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    def wrapper():
        return lookup(query)

    key = md5(query.encode('utf-8')).hexdigest()

    results = wf.cached_data(key, wrapper, max_age=MAX_CACHE_AGE)

    if not len(results):
        wf.add_item('Nothing found', 'Try a different query', icon=ICON_WARNING)

    for d in results:
        wf.add_item(d['term'], d['description'], uid=d['url'], arg=d['url'],
                    valid=True, icon='icon.png')

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
