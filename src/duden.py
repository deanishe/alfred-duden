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
A workflow for Alfred 3+ (http://www.alfredapp.com/).

Search the definitive German dictionary at http://www.duden.de.
"""

from __future__ import print_function, unicode_literals

import htmlentitydefs
from hashlib import md5
import sys
import urllib
import re

from workflow import web, Workflow3, ICON_WARNING


UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-duden'}
# USER_AGENT = ('Mozilla/5.0 (Windows NT 5.1; rv:31.0) '
#               'Gecko/20100101 Firefox/31.0')
USER_AGENT = ('Alfred-Duden/{version} '
              '(https://github.com/deanishe/alfred-duden)')

BASE_URL = b'http://www.duden.de'
SEARCH_URL = b'{}/suchen/dudenonline/{{query}}'.format(BASE_URL)

MAX_CACHE_AGE = 86400  # 1 day
MIN_QUERY_LENGTH = 2

# Load local HTML page for parser testing
DEVMODE = False
if DEVMODE:
    MAX_CACHE_AGE = 1  # 1 second

log = None


def unescape(text):
    """Replace HTML entities with Unicode characters.

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

    return re.sub(r'&#?\w+;', fixup, text)


def flatten(elem, recursive=False):
    """Return the string contents of partial BS elem tree.

    :param elem: BeautifulSoup ``Tag`` or ``NavigableString``
    :param recursive: Whether to flatten children or entire subtree
    :returns: Flattened Unicode text contained in subtree

    """
    from bs4 import Tag

    content = []

    if recursive:
        elems = elem.descendants
    else:
        elems = elem.contents

    for e in elems:
        # If processing recursively, a NavigableString for the
        # tag text will also be encountered
        if isinstance(e, Tag) and recursive:
            continue
        if hasattr(e, 'string') and e.string is not None:
            # log.debug('[%s] : %s', e.__class__.__name__, e.string)
            content.append(e.string)

    return unescape(re.sub(r'\s+', ' ', ''.join(content))).strip()


def lookup(query):
    """Get results matching ``query`` from duden.de.

    :param query: Search term to look up
    :type query: ``unicode``
    :returns: (possibly empty) list of search results
    :rtype: ``list``

    """
    from bs4 import BeautifulSoup as BS
    results = []

    if DEVMODE:
        with open('test-after.html') as fp:
            html = fp.read()

    else:
        url = SEARCH_URL.format(query=urllib.quote(query.encode('utf-8')))
        log.debug(url)

        user_agent = USER_AGENT.format(version=wf.version)
        r = web.get(url, headers={'User-Agent': user_agent})
        # Duden.de sends 404 if there are no results
        if r.status_code == 404:
            return results
        r.raise_for_status()
        html = r.content

    # Parse results
    soup = BS(html, b'html5lib')
    elems = soup.find_all('section', {'class': 'vignette'})

    for elem in elems:
        # log.debug('elem : %s', elem.prettify())
        result = {}
        header = elem.find('h2')
        if header is None:
            continue

        link = header.find('a')
        term = flatten(link)

        log.debug('term : %r', term)

        result['term'] = term
        # result['url'] = '{}{}'.format(BASE_URL, link['href'])
        result['url'] = BASE_URL + link['href']

        log.debug('URL : %r', result['url'])

        description_elem = elem.find('p')

        log.debug('raw description : %r', description_elem)

        description = flatten(description_elem, recursive=True)

        log.debug('flattened description : %r', description)

        # Remove Worttrennung & definition links
        i = description.find('|')
        if i > -1:
            i = description.find(' ', i)
            description = description[i:].strip()
        else:
            i = description.find('Worttrennung:')
            if i > -1:
                i = description.find(' ', i + 14)
                description = description[i:].strip()

        description = description.replace('Zum vollständigen Artikel',
                                          '').strip()

        log.debug('description : %r', description)

        result['description'] = description

        # log.debug('result : {}'.format(pformat(result)))
        results.append(result)

    log.debug('{} results for `{}`'.format(len(results), query))

    return results


def main(wf):
    """Run workflow."""
    query = wf.args[0]

    log.debug('query : %r', query)

    if wf.update_available:
        wf.add_item('New version available',
                    'Action this item to update',
                    autocomplete='workflow:update',
                    icon='update-available.icns')

    if len(query) < MIN_QUERY_LENGTH:
        wf.add_item('Query too short', 'Keep typing…', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    def wrapper():
        return lookup(query)

    key = md5(query.encode('utf-8')).hexdigest()

    results = wf.cached_data(key, wrapper, max_age=MAX_CACHE_AGE)

    if not len(results):
        wf.add_item('Nothing found',
                    'Try a different query',
                    icon=ICON_WARNING)

    for d in results:
        it = wf.add_item(d['term'],
                         d['description'],
                         uid=d['url'],
                         arg=d['url'],
                         valid=True,
                         icon='icon.png')

        it.add_modifier('cmd', subtitle=d['url'])

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(
        update_settings=UPDATE_SETTINGS,
        libraries=['./lib'])
    log = wf.logger
    sys.exit(wf.run(main))
