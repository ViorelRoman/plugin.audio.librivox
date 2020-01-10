#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xbmcswift2 import Plugin, xbmcgui
import requests
import feedparser

plugin = Plugin()


class Librivox:
    books_url = 'https://librivox.org/api/feed/audiobooks/'
    authors_url = 'https://librivox.org/api/feed/authors/'

    def __init__(self, *args, **kwargs):
        pass

    def search(self, author=None, genre=None, title=None, offset=0):
        book_list = [
            {
                'label': 'Authors',
                'path': plugin.url_for('authors')
            }
        ]
        r = requests.get(
            self.books_url,
            params={'author': author, 'genre': genre, 'title': title, 'offset': offset, 'format': 'json'}
        )
        if r.status_code == 200:
            data = r.json()
            for book in data['books']:
                book = {
                    'label': '{} ({} {}) {}'.format(
                        book['title'].encode('utf-8'),
                        book['authors'][0]['first_name'].encode('utf-8'),
                        book['authors'][0]['last_name'].encode('utf-8'),
                        [int(x) for x in book['copyright_year'].split() if x.isdigit()]
                    ),
                    'label2': book['description'],
                    'icon': plugin.icon,
                    'fanart': get_plugin_fanart(),
                    'path': plugin.url_for(
                        'show_book',
                        url=book['url_rss'],
                        author=book['authors'][0]['last_name'].encode('utf-8')
                    ),
                }
                book_list.append(book)
        book_list.append(
            {
                'label': 'Next page',
                'path': plugin.url_for('book_list', author=author, offset=str(offset + 50))
            }
        )
        return book_list

    def authors(self):
        author_list = []
        r = requests.get(
            self.authors_url,
            params={'format': 'json'}
        )
        if r.status_code == 200:
            data = r.json()
            for author in data['authors']:
                item = {
                    'label': '{} {}'.format(
                        author['first_name'].encode('utf-8'),
                        author['last_name'].encode('utf-8'),
                    ),
                    'icon': plugin.icon,
                    'fanart': get_plugin_fanart(),
                    'path': plugin.url_for('author', author=author['last_name'].encode('utf-8'))
                }
                author_list.append(item)
        return author_list

    def details(self, id):
        pass

    def get_tracks(self, url, author):
        data = feedparser.parse(url)
        song_list = [
            {
                'label': 'Other books of the same author',
                'path': plugin.url_for('author', author=author)
            }
        ]
        for song in data['items']:
            item = {
                'label': song['title'],
                'path': [x['href'] for x in song['links'] if x['rel'] == 'enclosure'][0],
                'is_playable': True,
                'info': ['video', {'plot': 'Some plot', 'mediatype': 'movie'}]
            }
            song_list.append(item)
        return song_list


@plugin.route('/')
def index():
    menu = (
        {
            'label': 'All books',
            'path': plugin.url_for('book_list', offset='0')
        },
        {
            'label': 'All authors',
            'path': plugin.url_for('authors')
        },
        {
            'label': 'Search by author',
            'path': plugin.url_for('author_search')
        },
        {
            'label': 'Search by genre',
            'path': plugin.url_for('genre_search')
        },
    )
    plugin.finish(menu)


@plugin.route('/list/<offset>')
def book_list(offset='0'):
    offset = int(offset)
    librivox = Librivox()
    plugin.finish(librivox.search(offset=offset))


@plugin.route('/show_book/<url>/<author>')
def show_book(url, author):
    librivox = Librivox()
    plugin.finish(librivox.get_tracks(url, author))


@plugin.route('/authors/')
def authors():
    libribox = Librivox()
    plugin.finish(libribox.authors())


@plugin.route('/author/<author>')
def author(author):
    librivox = Librivox()
    plugin.finish(librivox.search(author=author))


@plugin.route('/author_search/')
def author_search():
    author = xbmcgui.Dialog().input(heading='Enter the last name of author')
    librivox = Librivox()
    plugin.finish(librivox.search(author=author))


@plugin.route('/genre_search/')
def genre_search():
    genre = xbmcgui.Dialog().input(heading='Enter the genre of desired books')
    librivox = Librivox()
    plugin.finish(librivox.search(genre=genre))


def get_plugin_fanart():
    return plugin.fanart if not plugin.get_setting('hide-fanart', bool) else ''
