
# Metadata
AUTHOR = 'Eduardo Gade Gusmao'
SITENAME = 'Gusmao Lab'
SITEURL = ""
TIMEZONE = 'America/Bahia'
DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%d %B %Y'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Content organization
PATH = "content"
ARTICLE_PATHS = ["blog"]
PAGE_PATHS = ["pages"]
STATIC_PATHS = ["extra/CV.pdf"]

# Site structure
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
ARTICLE_URL = 'blog/{slug}/'
ARTICLE_SAVE_AS = 'blog/{slug}/index.html'

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ('LinkedIn', 'https://www.linkedin.com/in/gusmao/'),
    ('GitHub', 'https://github.com/eggduzao'),
)

# Social widget
SOCIAL = (
    ('Email', 'mailto:contact@gusmaolab.org'),
    ('RSS', '/feeds/all.atom.xml'),
)

# Default pagination
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
