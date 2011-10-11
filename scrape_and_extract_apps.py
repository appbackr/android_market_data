#! /usr/bin/env python
# scrape_and_extract_apps
import sys
sys.path.append('../')
from common import utilities
reload(utilities)


import urllib2, BeautifulSoup, re, urlparse,  datetime, traceback, time, os

ANDROID_MARKET_SCRAPE_CACHE_FOR_HTML='../cache/dummy_html/' 
ANDROID_MARKET_SCRAPE_CACHE_FOR_RESOLVED_URLS='../cache/dummy_resolved_urls/' 
download_from_web=True
read_from_cache=False
write_to_cache=False
downloaded_urls=[]

CATEGORY_L=[u'GAME', u'ARCADE', u'BRAIN', u'CARDS', u'CASUAL', u'GAME_WALLPAPER', u'RACING', u'SPORTS_GAMES', u'GAME_WIDGETS', u'APPLICATION', u'BOOKS_AND_REFERENCE', u'BUSINESS', u'COMICS', u'COMMUNICATION', u'EDUCATION', u'ENTERTAINMENT', u'FINANCE', u'HEALTH_AND_FITNESS', u'LIBRARIES_AND_DEMO', u'LIFESTYLE', u'APP_WALLPAPER', u'MEDIA_AND_VIDEO', u'MEDICAL', u'MUSIC_AND_AUDIO', u'NEWS_AND_MAGAZINES', u'PERSONALIZATION', u'PHOTOGRAPHY', u'PRODUCTIVITY', u'SHOPPING', u'SOCIAL', u'SPORTS', u'TOOLS', u'TRANSPORTATION', u'TRAVEL_AND_LOCAL', u'WEATHER', u'APP_WIDGETS']

def get_categories_old(u):  
    print 'get_categories: ' + u
    print 'BeautifulSoup.__version__ ' + BeautifulSoup.__version__
    page, _ = get(u)
    soup = BeautifulSoup.BeautifulSoup(page, fromEncoding='utf-8')
    rez=soup.findAll(attrs={"class":"top-nav-sub-item"})  #main-menu-sub-item-last
    categories=[]
    for r in rez:
        cat_url=(r.findAll('a'))[0]['href']
        m=re.match("/apps/(.*)", cat_url)
        if m:
            cat=m.group(1)
            categories+=[cat]
    return categories

def get_categories():
    return CATEGORY_L

# caches results, returns cached values
# returns 2-tuple of the html behind this url (after any redirection) and whatever this url ultimately redirected to (if there was no redirection, then this is just the original url of course)
def get(url):
    global download_from_web, read_from_cache, write_to_cache, downloaded_urls
    cleaned_url=utilities._clean_for_path(url)
    cleaned_url_minus_goog_redirect_prefix=re.compile(r'^http-www.google.comurlq').sub('',cleaned_url)  # if link is a Google redirect link, remove the Google prefix part.  note that the '&usg=' part remains.
    if read_from_cache or write_to_cache:
        html_cache_path=ANDROID_MARKET_SCRAPE_CACHE_FOR_HTML+cleaned_url_minus_goog_redirect_prefix
        resolved_url_cache_path=ANDROID_MARKET_SCRAPE_CACHE_FOR_RESOLVED_URLS+cleaned_url_minus_goog_redirect_prefix
    if read_from_cache and os.path.isfile(resolved_url_cache_path) and os.path.isfile(html_cache_path):
        print 'cache hit - ' + (' previously cached.' if not (url in downloaded_urls) else '') + '    '+url+'  file: '+cleaned_url_minus_goog_redirect_prefix
        html=open(html_cache_path).read()
        resolved_url=open(resolved_url_cache_path).read()
    else:
        if not download_from_web:
            raise Exception('Cached file not present', 'We are doing an offline, cache-only processing job. If there is no file here it probably just means in the original scrape this request 404\'ed or something.  Expected file in '+html_cache_path+'    and '+ resolved_url_cache_path)
        if read_from_cache:
            print 'cache miss    '+url
        f = urllib2.urlopen(url,timeout=10)
        html=f.read()
        resolved_url = f.geturl()
        # the call to got_url is after urlopen() and f.read() so that it won't be called if there is a 404 or other error on reading.  
        # print "hello philipp!"
        # print html
        got_url(url)
        if write_to_cache:
            html_cache=open(html_cache_path,'w')
            html_cache.write(html)
            resolved_url_cache=open(resolved_url_cache_path,'w')
            resolved_url_cache.write(resolved_url)
    return (html,resolved_url)

#todo: should put the summary processing thing in here     maybe... but then it would all have to work at once...?  well, just for one page, that's a good thing.
#todo:  really should put the recursive 'try again' thing here into get() instead, except with the default being attempts_remaining=0.  the thing about that is that 
#then you'd throw the exception when you've run out of attempts, which I'd then have to catch and ignore here.  but honestly, it would be really valuable in 
#other places in the code
def scrape_top(url, attempts_remaining=2, seconds_between_attempts=5): 
    print 'scrape top ' + url
    rez=[]
    try:
        page, _ = get(url)
        soup = BeautifulSoup.BeautifulSoup(page, fromEncoding='utf-8')
        rez=soup.findAll(attrs={"class":"snippet snippet-medium"})
    except Exception as e:
        print 'Exception when getting page of summaries.  url='+url
        print e
        print e.args
        if attempts_remaining>0:
            print 'waiting '+str(seconds_between_attempts)+' seconds to try again. there are '+str(attempts_remaining)+' attempts remaining (including this next one.)'
            time.sleep(seconds_between_attempts)
            print 'trying again. '
            rez=scrape_top(url,attempts_remaining=attempts_remaining-1,seconds_between_attempts=seconds_between_attempts) #kinda weird recursion.  setting the return value but not actually returning.  hmm.
    return rez

def got_url(url):
    if url in downloaded_urls:
        print 'url has been gotten, but no cache hit  this is not normal.  '+url  
    downloaded_urls.append(url)

def _get_detail_url(summary):
    soup = BeautifulSoup.BeautifulSoup(str(summary), fromEncoding='utf-8')
    rez=soup.find(attrs={"class":"thumbnail"})
    return rez['href']

def get_detail_url_absolute(summary):
    return "http://market.android.com"+_get_detail_url(summary)
    
def get_standard_metadatum(parent_tag,heading_text):
    heading_tag=parent_tag.find((lambda tag: tag.string == heading_text))
    value_tag = heading_tag.nextSibling
    return value_tag

def get_itemprop_soup(soup,itemprop_name,recur=False):
    return soup.find(None,itemprop=itemprop_name,recursive=recur)

#does not recur!  only one layer deep.
def get_itemprop_soup_l(soup,recur=False):
    return soup.findAll(None,itemprop=re.compile('.+'),recursive=recur)

def get_itemprop_content(soup,itemprop_name,recur=False):
    return get_itemprop_soup(soup,itemprop_name,recur)['content']

def scrape_detail(url):   
    app={} 
    app['email_contacts']=[]
    app['logos']=[]
    page, resolved_url = get(url)
    soup = BeautifulSoup.BeautifulSoup(page, fromEncoding='utf-8')

    app_info_list_entity=soup.find(None,itemtype="http://schema.org/MobileSoftwareApplication")

    application_name=get_itemprop_content(app_info_list_entity,'name')
    app['application_name']=application_name

    image=get_itemprop_content(app_info_list_entity,'image')
    app['logos'].append(image)

    content_rating=get_itemprop_soup(app_info_list_entity,'contentRating', True)
    app['content_rating']=content_rating.text

    size=get_itemprop_soup(app_info_list_entity,'fileSize',True)
    app['install_size']=size.text

    version=get_itemprop_soup(app_info_list_entity,'softwareVersion',True)
    app['version']=version.text

    author=get_itemprop_soup(app_info_list_entity,'author',True)
    
    author_name=get_itemprop_content(author,'name',True) 
    app['developer_name']=author_name
    
    developer_page_url=get_itemprop_content(author,'url',True)
    app['developer_page_url']='http://market.android.com'+developer_page_url

    rating=get_itemprop_content(app_info_list_entity,'ratingValue',True) 
    app['rating']= rating
    try:
        rating_count=get_itemprop_soup(app_info_list_entity,'ratingCount',True) 
        app['rating_count']= rating_count.text
    except:
        app['rating_count']=0

    price=get_itemprop_soup(app_info_list_entity,'price',True) 
    app['price']= price.text

    updated=get_itemprop_soup(app_info_list_entity,'datePublished',True) 
    app['application_updated']= updated.text

    # for a lot of these values, get_standard_metadatum is still useful!  :)
    requires_android=get_standard_metadatum(app_info_list_entity,'Requires Android:').string   
    app['requires_android']= requires_android
 
    category_tag = get_standard_metadatum(app_info_list_entity,'Category:')
    category_a=category_tag.find('a')  
    app['category']=category_a.string

    app['description']=soup.find('div',attrs={"id":"doc-original-text"}).text
    emails_in_description=get_emails(app['description'])
    app['email_contacts']+=emails_in_description

    # screenshots
    ss_section=soup.find('div',attrs={"class": re.compile(".*doc-screenshot-section.*")})
    try:
        img_l=ss_section.findAll('img')
        img_src_l=map(lambda img: img['src'], img_l)
        app['screenshots']=img_src_l
    except:
        app['screenshots']=[]
    # logos
    logos_section=soup.find('div',attrs={"class":"doc-banner-icon"})
    try:
        img_l=logos_section.findAll('img')
        img_src_l=map(lambda img: img['src'], img_l)
        app['logos']=img_src_l
    except:
        app['logos']=[]

    downloads_soup=get_itemprop_soup(soup,'numDownloads', True) 
    num_downloads=downloads_soup
    app['installs']=num_downloads.contents[0].string
    
    chart=downloads_soup.find(None, attrs={'class':'normalized-daily-installs-chart'})    
    try:
        chart_img_src=chart.find('img')['src']
        app['normalized_daily_installs_chart']=chart_img_src
    except:
        pass
    return app

def get_emails(txt):
    email_re='[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,4}'
    return re.findall(email_re, txt,re.IGNORECASE)

def get_emails_in_page(url):
    html, _ = get(url)
    #print _
    emails=get_emails(html)
    return list(set(emails))

def get_links_to_contact_page(url):
    html,redirected_url = get(url)
    contact_links_soup = BeautifulSoup.BeautifulSoup(html, fromEncoding='utf-8')
    tags=contact_links_soup.findAll('a', href=re.compile('contact',re.IGNORECASE))
    contact_links_with_desired_hrefs=[urlparse.urljoin(redirected_url,anchor['href']) for anchor in tags]

    contact_text_links_soup = BeautifulSoup.BeautifulSoup(html, fromEncoding='utf-8')
    tags=contact_links_soup.findAll('a', text=re.compile('contact',re.IGNORECASE))
    contact_links_with_desired_anchor_text=[urlparse.urljoin(redirected_url,anchor_text.parent['href']) for anchor_text in tags]
    return list(set(contact_links_with_desired_hrefs+contact_links_with_desired_anchor_text))

def get_twitter_handles(url):
    html,_ = get(url)
    twitter_handle_re='(^|\s)(@[A-Z0-9]+)'
    handles=re.findall(twitter_handle_re, html,re.IGNORECASE)
    if handles:
        handles=map(lambda x: x[1],handles)
        handles=filter(lambda x: x not in ['@import','@param','@page'],handles)
    #twitter_link_re='(http://twitter.com/[A-Z0-9]+)'  
    return list(set(handles))

def get_dev_homesite_url(dev_page_url):
    #<a href="/developer?pub=Glu+Mobile" class="doc-header-link">Glu Mobile</a>
    html,_ =get(dev_page_url)
    soup = BeautifulSoup.BeautifulSoup(html, fromEncoding="utf-8")
    #<a href="http://www.google.com/url?q=http://www.glu.com/&amp;usg=AFQjCNHZ-ipDlTho6lCB5-SdepXgLSDmjw" target="_blank">Visit Website for Glu Mobile</a>

    rez=soup.find("a",href=re.compile("^http://www.google.com/url\?q"))
    #print "rez="+str(rez)
    return rez["href"]

#if this were Clojure I'd make a macro like 'with-try-catch(print-to-output)' that would wrap its body in the try: except: block below which includes the statement  print "error in getting contact links from the developer's site: "+u except it would just print the values of args-to-output in the exception block. args-to-output would of course be a list of symbols.    oh wait, maybe better would be one that takes a list of such body blocks.  anyway.  the below is fine for now.  I can make a Python function maybe that does what i want here with this: http://pypi.python.org/pypi/SymbolType 
def scrape_dev_homesite(u,allowable_recursion_depth=1):
    #print "scrape_dev_homesite for " + u
    app={}
    if re.compile('.*twitter.com.*',re.IGNORECASE).match(u):
        return {'twitter_contacts': [u]} # if the resolved_dev_homesite_u is a "twitter.com" profile, just use that url as the lone contact
    if re.compile('mailto:.*',re.IGNORECASE).match(u):
        return {'email_contacts': [u]} # if the resolved_dev_homesite_u is a "mailto" link, just use that url as the lone contact
    if re.compile('.*facebook.com.*',re.IGNORECASE).match(u):
        return {'contact links': [u]} 
    try:
        app['email_contacts']=get_emails_in_page(u)
    except Exception as e:
        print "error in getting emails from the developer's site: "+u
        print e
    try:
        app['contact links']=get_links_to_contact_page(u)
    except Exception as e:
        print "error in getting contact links from the developer's site: "+u
        print e
    try:
        app['twitter_contacts'] = get_twitter_handles(u)
    except Exception as e:
        print "error in getting twitters from the developer's site: "+u
        print e
    if allowable_recursion_depth>0 and app.has_key('contact links'):
        for contact_link in app['contact links']:
             app_from_contact_page=scrape_dev_homesite(contact_link,allowable_recursion_depth=allowable_recursion_depth-1)
             utilities.merge_dicts_add_values(app,app_from_contact_page)
    return app

#normally the use of the cache is in the OFFLINE global variable
def extract_app(detail_u):
    app={}
    app['unique_package']=get_unique_package(detail_u)
    try:
        utilities.merge_dicts_add_values(app,scrape_detail(detail_u))
    except Exception as e:
        print >> sys.stderr ,"! ERROR IN GETTING DATA FROM THE APPLICATION'S DETAIL PAGE ON THE MARKET SITE: %s" % detail_u
        print >> sys.stderr, e
        traceback.print_exc()
        app['developer_page_url']=detail_u
    #print "app"
    #print app   # at this point there may be nothing on this dict except 'developer_page_url' (if this errored out above)
    dev_page_u=app['developer_page_url']
    try:
        dev_homesite_u = get_dev_homesite_url(dev_page_u)
        #print "dev_homesite_u=  "+dev_homesite_u
        resolved_dev_homesite_u=get(dev_homesite_u)[1]
        app['developer_homepage_url']=resolved_dev_homesite_u
        homesite_data=scrape_dev_homesite(resolved_dev_homesite_u)
        utilities.merge_dicts_add_values(app,homesite_data)
    except Exception as e:
        print "exception part 2 on "+ dev_page_u + " .  This may **or may not!** be the url that is having a problem.  It could be that the dev homepage is the problem." #it's possible that dev_homesite_u won't be defined yet, tho unlikely.  so i need to print this instead.    todo:  note that this continues on and returns app, which will have a few values.  it might be worth looking to see . but if this broke when trying to get the dev_homesite_u, then that page won't be cached, thus a second run will probably get the page successfully, assuming it's an temporary server issue (or a connectivity issue on our side)
        print e
        print e.args
        print "those are the e details"
    return app

def get_unique_package(detail_u):
    return utilities.url_param(detail_u,'id')

def extract_and_populate_app(detail_u,scrape_timestamp,extraction_timestamp,category_scraped):
    app=extract_app(detail_u)
    app['scrape_timestamp']=scrape_timestamp 
    app['extraction_timestamp']=extraction_timestamp 
    app['category_scraped']=category_scraped
    #app['paid']=is_paid
    return app


def scrape_category_top_ranked(category_scraped,is_paid,scrape_timestamp,extraction_timestamp,starting_page,max_ending_page):
    scraped_app_l=[]
    count=None
    i=starting_page
    while i<max_ending_page and (count>0 or count is None):
        print "page #"+str(i)
        print len(scraped_app_l)
        start_time=datetime.datetime.now()
        summaries=scrape_top('https://market.android.com/details?id=apps_topselling_'+ ('paid' if is_paid else 'free') +'&cat='+category_scraped+'&start='+str(i*24)+'&num=24')
        print "and now summaries:"
        for summary in summaries:
            detail_u=get_detail_url_absolute(summary)
            app=extract_and_populate_app(detail_u,scrape_timestamp,extraction_timestamp,category_scraped)
            scraped_app_l.append(app)
        i+=1
        count=len(summaries)
        end_time=datetime.datetime.now()
        print 'elapsed time for page of data:     '+str(end_time-start_time)
    return scraped_app_l

# this scrapes, ranks, and inserts into the database
# note that category can also be a subcategory / subgenre.  In fact I'm not positive that the Android market has any sort of hierarchical idea of categories. That may just be tacked onto the web UI.
# example: inhale_market_data('GAME',True,'/Users/herdrick/Dropbox/python/appbackr/cache/html_new/','/Users/herdrick/Dropbox/python/appbackr/cache/resolved_urls_new/')
# example: inhale_market_data('PUZZLE',False,'/Users/herdrick/Dropbox/python/appbackr/cache/html_new/','/Users/herdrick/Dropbox/python/appbackr/cache/resolved_urls_new/')
def inhale_market_data(category,paid,html_cache_path, resolved_urls_cache_path, scrape_date, extraction_date, offline=False,starting_page=0,max_ending_page=sys.maxint):
    start_time=datetime.datetime.now()
    print 'scrape start time:'+str(start_time)
    if offline:
        _download_from_web=False
        _read_from_cache=True
        _write_to_cache=False
    else:
        _download_from_web=True
        _read_from_cache=True
        _write_to_cache=True
    initialize_globals(html_cache_path,resolved_urls_cache_path,_download_from_web=_download_from_web,_read_from_cache=_read_from_cache,_write_to_cache=_write_to_cache)
    scrape_timestamp=int(time.mktime(scrape_date.timetuple()) * 1000)  
    extraction_timestamp=int(time.mktime(extraction_date.timetuple()) * 1000)
    if not offline and (scrape_date != extraction_date):
            raise Exception('this is supposed to be an online scrape yet the extraction date is different from the scrape date.  wtf.')
    print 'scrape_date:' + str(scrape_date)
    print 'scrape_timestamp:' + str(scrape_timestamp)
    print 'extraction_date:' + str(extraction_date)
    print 'extraction_timestamp:' + str(extraction_timestamp)

    print 'html cache dir: '+html_cache_path
    print 'resolved_urls_cache dir: '+resolved_urls_cache_path
    app_l=scrape_category_top_ranked(category,paid,scrape_timestamp,extraction_timestamp,starting_page,max_ending_page) 
    # assign Android Market ranks,  we got them in order; use that order.
    for n in range(len(app_l)):
        app_l[n]['market_rank']=n
    
    # do something with the list of apps here.  for example, persist them.
    from android import db
    reload(db)
    db.persist_apps(app_l)
    print '<here is where apps would be persisted>' # comment this out if you are persisting your apps here
    
    if len(app_l)>0:
        print 'scrape timestamp: '+str(app_l[0]['scrape_timestamp'])
        print 'count of applications extracted  '+str(len(app_l))
    else:
        print 'ERROR (or unexpected):   Results count is zero!'
    end_time=datetime.datetime.now()
    print 'category scrape time:'+str(start_time)
    print 'category scrape end time:  '+str(end_time)
    print 'elapsed time:     '+str(end_time-start_time)

def initialize_globals(_html_cache_path, _resolved_urls_cache_path, _download_from_web, _read_from_cache, _write_to_cache ):
    global ANDROID_MARKET_SCRAPE_CACHE_FOR_HTML, ANDROID_MARKET_SCRAPE_CACHE_FOR_RESOLVED_URLS, downloaded_urls, download_from_web, read_from_cache, write_to_cache
    ANDROID_MARKET_SCRAPE_CACHE_FOR_HTML=_html_cache_path
    ANDROID_MARKET_SCRAPE_CACHE_FOR_RESOLVED_URLS=_resolved_urls_cache_path
    download_from_web=_download_from_web
    read_from_cache=_read_from_cache
    write_to_cache=_write_to_cache
    downloaded_urls=[]



