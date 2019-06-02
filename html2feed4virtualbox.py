import argparse
import datetime

import xml.dom.minidom
import dateparser
import requests
from lxml import html
from rfeed import *


def createfeeditem(_news):
    link, guid = parse_link(_news)
    _item = Item(
        description=html.tostring(_news).strip().decode('utf-8'),
        link=link,
        pubDate=parse_date(_news),
        guid=guid,
        title=parse_title(_news),
    )
    return _item


def parse_title(_news):
    title = _news.xpath('./strong')
    if len(title) > 0:
        _title = title[0].tail
    else:
        _title = _news.xpath('.')[0].text
    _title = _title.split('!', 1)[0]
    return _title.strip()


def parse_link(_news):
    try:
        _link = BASELINK + "/" + _news.xpath('./a')[0].attrib['href']
        _guid = Guid(_link)
        return _link, _guid
    except:
        pass
    return None, None


def parse_date(_news):
    try:
        date = _news.xpath('./strong')[0].text
        _pubdate = dateparser.parse(date, languages=['en'], settings={})
        return _pubdate
    except:
        pass
    return None


def create_items(_items):
    items = []
    # last one is "older entries"
    for news in _items[:-1]:
        item = createfeeditem(news)
        items.append(item)

    return items


def write(args, feed):
    pretty_xml = xml.dom.minidom.parseString(feed.rss()).toprettyxml()
    if args.filename:
        f = open(args.filename, "w")
        f.write(pretty_xml)
        f.close()
    else:
        print(pretty_xml)


def main():
    parser = argparse.ArgumentParser(description='Virtualbox.org html2rss generator')
    parser.add_argument('-f', '--file', dest='filename', default=None, help='Filename to store RSS-feed into.')
    args = parser.parse_args()

    url = requests.get(BASELINK)
    tree = html.fromstring(url.text)
    news_elements = tree.xpath('//*[@id="wikipage"]/p')

    title = tree.xpath('//title')[0].text.strip()
    description = tree.xpath('//title')[0].text.strip()

    feed = Feed(
        title=title,
        link=BASELINK,
        description=description,
        language="en-US",
        lastBuildDate=datetime.datetime.now(),
        items=create_items(news_elements),
        generator="Virtualbox Feed Generator",
    )

    write(args, feed)


BASELINK = "https://www.virtualbox.org/wiki/News"

if __name__ == '__main__':
    main()
