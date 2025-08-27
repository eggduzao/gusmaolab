
# Metadata 
SITENAME = 'Gusmao Lab'
SITESUBTITLE = 'Computational Biology • AI • Writing'
SITEURL = "" # In main
TIMEZONE = 'America/Bahia'
DEFAULT_LANG = 'en'
DEFAULT_DATE_FORMAT = '%d %B %Y' 
THEME = 'themes/Flex' 
 
# SideBar Bio
AUTHOR = 'Eduardo Gade Gusmao'
TAGLINE = 'Bioinformatician, Professor and AI/ML/DL Researcher'
SITELOGO = '/images/avatar.png'  # optional
FAVICON = '/images/favicon.ico'  # optional

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

# Static paths
STATIC_PATHS = ['images', 'extra/CV.pdf', 'extra/CNAME']
EXTRA_PATH_METADATA = {
    'extra/CV.pdf': {'path': 'CV.pdf'},
    'extra/CNAME': {'path': 'CNAME'},
}

# Site structure
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
ARTICLE_URL = 'blog/{slug}/'
ARTICLE_SAVE_AS = 'blog/{slug}/index.html'

# Blogroll
# LINKS = (
#     ("Pelican", "https://getpelican.com/"),
#     ("Python.org", "https://www.python.org/"),
#     ("Jinja2", "https://palletsprojects.com/p/jinja/"),
# )

# Social links (use your links or placeholders)
SOCIAL = (
    ('GitHub', 'https://github.com/eggduzao'),
    ('LinkedIn', 'https://www.linkedin.com/in/eduardogadegusmao/'),
    ('ResearchGate', 'https://www.researchgate.net/profile/Eduardo-Gusmao'),
    ('ORCID', 'https://orcid.org/0000-0001-7461-1443'),
    ('Instagram', 'https://instagram.com/eduardo.gade.gusmao.lab'),
    ('Google Scholar', 'https://scholar.google.com/citations?user=erHz7L8AAAAJ&hl=en'),
    ('Email', 'mailto:eduardo.gusmao@gusmaolab.org'),
    ('RSS', '/feeds/all.atom.xml'),
)

# Menu items
MAIN_MENU = True
MENUITEMS = (
    ('About', '/about.html'),
    ('Projects', '/projects.html'),
    ('Writings', '/writing.html'),
    ('Blog', '/blog.html'),
)

# Enable Flex features
USE_FOLDER_AS_CATEGORY = True
SHOW_ARTICLE_AUTHOR = True
SHOW_ARTICLE_CATEGORY = True
SHOW_ARTICLE_TAGS = True
SHOW_DATE_MODIFIED = True

# Flex-specific options
DISQUS_SITENAME = ''
GOOGLE_ANALYTICS = ''

# Default pagination
DEFAULT_PAGINATION = 10


# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
######################################

