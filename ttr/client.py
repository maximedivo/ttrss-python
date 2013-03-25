from datetime import datetime
import requests
import json

class TTRClient(object):
    def __init__(self, url, user=None, password=None):
        self.url = url + '/api/'
        self.user = user
        self.password = password

        self._session = requests.Session()

        if self.password and self.user:
            self.login()

    def login(self):
        self._session.post(self.url, data=json.dumps({'op': 'login', 'user': self.user, 'password': self.password}))

    def logout(self):
        self._get_json({'op': 'logout'})

    def _get_json(self, post_data):
        r = self._session.post(self.url, data=json.dumps(post_data))
        return json.loads(r.content)

    def get_categories(self):
        r = self._get_json({'op': 'getCategories'})
        return [Category(cat, self) for cat in r['content']]

    def get_feeds(self, cat_id=-1, unread_only=False, limit=0, offset=0, include_nested=False):
        r = self._get_json({'op': 'getFeeds', 'cat_id': cat_id})
        return [Feed(feed, self) for feed in r['content']]

    def get_headlines(self, feed_id=0):
        r = self._get_json({'op': 'getHeadlines', 'feed_id': feed_id})
        return [Headline(hl, self) for hl in r['content']]

    def get_articles(self, article_id):
        r = self._get_json({'op': 'getArticle', 'article_id': article_id})
        return [Article(article, self) for article in r['content']]

    def share_to_published(self, title, url, content):
        r = self._get_json({'op': 'shareToPublished', 'title': title, 'url': url, 'content': content})

class RemoteObject(object):
    def __init__(self, attr, client=None):
        self._client = client
        for key,value in attr.items():
            if key == 'id':
                value = int(value)
            self.__setattr__(key, value)

    
class Category(RemoteObject):
    def feeds(self, **kwargs):
        return self._client.get_feeds(cat_id=self.id, **kwargs)

class Feed(RemoteObject):
    def __init__(self, attr, client):
        super(Feed, self).__init__(attr, client)
        try:
            self.last_updated = datetime.fromtimestamp(self.last_updated)
        except AttributeError:
            pass

    def headlines(self):
        return self._client.get_headlines(feed_id=self.id)

class Headline(RemoteObject):
    def full_article(self):
        r = self._client.get_articles(self.id)
        return r[0]

class Article(RemoteObject):
    def publish(self):
        self._client.share_to_published(self.title, self.link, self.content)
    
