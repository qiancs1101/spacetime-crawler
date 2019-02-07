import logging
from datamodel.search.Chongshq_datamodel import ChongshqLink, OneChongshqUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

import json

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

def load_data():
    return {}
crawler_status = load_data()

@Producer(ChongshqLink)
@GetterSetter(OneChongshqUnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "Chongshq"

    def __init__(self, frame):
        self.app_id = "Chongshq"
        self.frame = frame


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneChongshqUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = ChongshqLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneChongshqUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url

            if not crawler_status.has_key(link.full_url):
                crawler_status[link.full_url] = {
                    'parent': None,
                    'visited': True,
                    'processed': 0,
                    'children': [],
                    'invalid': []
                }
            else:
                crawler_status[link.full_url]['visited'] = True
                crawler_status[crawler_status[link.full_url]['parent']]['processed'] += 1
            
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l, self.frame.get(ChongshqLink)):
                    self.frame.add(ChongshqLink(l))
                    crawler_status[l] = {
                        'parent': link.full_url,
                        'visited': False,
                        'processed': 0,
                        'children': [],
                        'invalid': []
                    }
                    crawler_status[link.full_url]['children'].append(l)
                else:
                    crawler_status[link.full_url]['invalid'].append(l)
            with open("./record.json","w") as f:
                json.dump(crawler_status, f)

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
    
def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''
    try:
        parsedPage = html.fromstring(rawDataObj.content)  # parse DOM tree
        parsedPage.make_links_absolute(rawDataObj.url)   # make some relative links to be absolute
    except:
        return outputLinks  # if web page cannot be parsed, return []
    outputLinks = parsedPage.xpath(".//a/@href")   # extract all href
    return outputLinks

def is_valid(url, frontier):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    try:
        parsed = urlparse(url)   # parse url, if cannot parse, it is invalid
    except:
        return False
    if parsed.scheme not in set(["http", "https"]):  # should contains protocol
        return False
    for link in frontier:   # ignore all the links that has been added to the frontier
        if url == link.full_url:
            return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False

