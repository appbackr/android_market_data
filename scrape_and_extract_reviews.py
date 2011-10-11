#scrape_and_extract_reviews
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
sys.path.append('/Users/herdrick/appbackr/appbackr_data_science/')
print sys.path

import httplib,urllib,urllib2,re,json,datetime, os,time, BeautifulSoup, functools, sys, traceback
from common import utilities
reload(utilities)
from android import db   # only needed for db.get_all_unique_packages()  and db.persist_reviews()
reload(db)

global downloaded_urls
global ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_JSON
global ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_RESOLVED_URLS
global OFFLINE
global NO_CACHE

def set_globals(json_text_cache_path, resolved_urls_cache_path,offline, no_cache ):
    global ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_JSON
    ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_JSON=json_text_cache_path
    global ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_RESOLVED_URLS
    ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_RESOLVED_URLS=resolved_urls_cache_path
    global downloaded_urls
    downloaded_urls=[]
    global OFFLINE
    OFFLINE=offline
    global NO_CACHE
    NO_CACHE=no_cache

def got_url(url):
    if url in downloaded_urls:
        print 'url has been gotten, but no cache hit  this is not normal.  '+url  
    downloaded_urls.append(url)

# caching here is based entirely on the host, path, and querystring.  keying on params also, i.e. post data, would be doable, but i don't need it now. 
def post(connection_maker, host, path,querystring, params,accept="text/html"):
    download_from_web=True   #not OFFLINE
    read_from_cache=False
    write_to_cache=False
    params_s=urllib.urlencode(params)
    url=querystring
    cleaned_url=utilities._clean_for_path_improved(url)
    #cleaned_url_minus_goog_redirect_prefix=re.compile(r'^http-www.google.comurlq').sub('',cleaned_url)  # if link is a Google redirect link, remove the Google prefix part.  note that the '&usg=' part remains.
    if read_from_cache or write_to_cache:
        json_text_cache_path=ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_JSON+cleaned_url
        resolved_url_cache_path=ANDROID_MARKET_REVIEWS_SCRAPE_CACHE_FOR_RESOLVED_URLS+cleaned_url
    if read_from_cache and os.path.isfile(resolved_url_cache_path) and os.path.isfile(json_text_cache_path):
        print 'cache hit!  this value was cached on this run: ' + str(url in downloaded_urls) + '    '+url
        print 'getting file from '+ json_text_cache_path
        json_text=open(json_text_cache_path).read()
        resolved_url=open(resolved_url_cache_path).read()
    else:
        if not download_from_web:
            raise Exception('Cached file not present', 'We are doing an offline, cache-only processing job. If there is no file here it probably just means in the original scrape this post 404\'ed or something.')
        #print 'cache miss  '+url
        conn=connection_maker(host)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                  "Accept": accept}
        conn.request('POST',path+'?'+querystring,params_s,headers)
        response = conn.getresponse()
        if response.status!=200:
            print response.status
            print response.reason
        json_text = response.read()
        conn.close()
        #resolved_url = response.geturl()
        resolved_url=url  # is this good enough to put as the content of our resolved_urls cache ?
        #print 'resolved_url='+resolved_url
        # the call to got_url is after urlopen() and f.read() so that it won't be called if there is a 404 or other error on reading.  
        got_url(url)
        if write_to_cache:
            json_cache=open(json_text_cache_path,'w')
            json_cache.write(json_text)
            resolved_url_cache=open(resolved_url_cache_path,'w')
            resolved_url_cache.write(resolved_url)
    return json_text


def get_reviews_json(country_code,language_code,unique_package,page=0,reviewType=0,reviewSortOrder=0):
    params = {'xhr':1}
    reviews_s=post(httplib.HTTPSConnection, "market.android.com", '/getreviews','id='+unique_package+'&reviewType='+str(reviewType)+'&reviewSortOrder='+str(reviewSortOrder)+'&pageNum='+str(page)+'&hl='+language_code+'&gl='+country_code,params,accept="text/plain")
    #print reviews_s
    regex=re.compile('.*?("htmlContent".*)',re.DOTALL) 
    m=regex.match(reviews_s)
    json_text='{'+m.group(1)  #matching on "htmlContent" and then adding a { to make this is json object is odd, but it's much less brittle than the usual alternative. 
    return json.loads(json_text)

def extract_reviews(reviews_html,country_code,language_code):
    try:
        soup = BeautifulSoup.BeautifulSoup(reviews_html,fromEncoding="utf-8")
        #print str(soup)
        reviews=soup.findAll('div',attrs={'class':'doc-review'})
        reviews[0]
    except Exception as e:
        print 'exception in extract_reviews(). (plural!)  ' +str(e)  + " e args="+str(e.args)
        print 'review_html= '+str(reviews_html)
        return []
    return map(lambda review: extract_review(review, country_code, language_code), reviews)

def extract_review(review_soup,country_code,language_code):
    try:
        #r_t=review_soup.find('div',attrs={'class':"ratings goog-inline-block", 'title':re.compile(':\s+[0-9.,]+?\s')})   #this works for English and German
        r_t=review_soup.find('div',attrs={'class':"ratings goog-inline-block"})  
        #r_t=review_soup.find('div',title=re.compile('Rating: .*? stars'))
        #print 'r_t'
        #print r_t
        #print "r_t['title']"
        #print r_t['title']
        #m=re.match('.*?:\s+([0-9.,]+?)\s',r_t['title'])    #this works for English and German
        m=re.match('.*?([0-9.,]{2,3}).*?',r_t['title'])
        #print 'm'
        #print m 
        rating_s=m.group(1)
        rating=rating_s.replace(',','.')
        #print 'rating'
        #print rating
        foo=BeautifulSoup.BeautifulSoup(review_soup.find('span',attrs={'class':'doc-review-date'}).contents[0], convertEntities=BeautifulSoup.BeautifulSoup.HTML_ENTITIES,fromEncoding="utf-8").text
        #print 'foo'
        #print foo

        # the next three lines work for English:
        m2=re.match('.*?([A-Z]\w+ \d+, \d+)', foo)  
        dt=datetime.datetime.strptime(str(m2.group(1)), '%B %d, %Y')
        review_timestamp=int(time.mktime(dt.timetuple())) * 1000
        review_date_string=foo  #leaving silly 'foo' name in place because of above archived code block below "the next three lines work for English"
        
        # there is only a <p> tag when the review prose is long.  Otherwise the summary is the only way to get the prose.
        if review_soup.p and review_soup.p.text!='':
            prose=review_soup.p.text
        else:
            prose=review_soup.h4.text
        try:
            reviewer=re.sub('^by\s*','', review_soup.find(True,attrs={'class':'doc-review-author'}).text)
        except Exception as e:
            print 'could not parse reviewer!'
            reviewer='<could not parse reviewer>'
    except Exception as e:
        print 'exception in extract_review().  ' +str(e)  + " e args="+str(e.args)+'   review_soup= '+str(review_soup)
        traceback.print_exc()        
        return None
    return {'rating':rating,'review_timestamp':review_timestamp,'review_date_string':review_date_string,'prose':prose,'reviewer':reviewer}

def get_reviews(country_code,language_code,scrape_timestamp,unique_package):
    print 'app: '+unique_package
    try:
        count=None
        all_reviews=[]
        i=0
        while count>0 or count is None:
            all_json=get_reviews_json(country_code,language_code,unique_package,i)
            json=all_json['htmlContent']
            reviews=extract_reviews(json,country_code,language_code)
            #print 'len(reviews)'+str(len(reviews))
            map(lambda review: review.update({'unique_package':unique_package,'country_code':country_code,'language_code':language_code,'scrape_timestamp':scrape_timestamp}), reviews) # wanted to just do a normal dict key-value assignment but that's not allowed in a lambda... lame.
            all_reviews+=reviews
            i+=1
            count=len(reviews)
    except Exception as e:
        print 'exception in get_reviews().   ' +str(e)  + " e args="+str(e.args)+'   unique_package= '+str(unique_package)+' .   returning whatever reviews we got before the exception.'        
        traceback.print_exc()
    return all_reviews

#ANALYTICS:
def inhale_reviews(country_code,language_code,unique_package_l,json_text_cache_path, resolved_urls_cache_path, now, offline=False, no_cache=False,database='archive'):
    set_globals(json_text_cache_path,resolved_urls_cache_path,offline,no_cache)
    scrape_timestamp=int(time.mktime(now.timetuple()) * 1000)
    print 'scrape_timestamp:' + str(scrape_timestamp)
    print 'json cache dir: '+json_text_cache_path
    print 'resolved_urls_cache dir: '+resolved_urls_cache_path
    #return map(lambda app_reviews: app_reviews['unique_package']=  map(get_reviews, unique_package_l))

    

    for unique_package in unique_package_l:
        reviews=get_reviews(country_code,language_code,scrape_timestamp,unique_package)
        if reviews:
            print 'scrape_timestamp of this scrape/processing: '+str(scrape_timestamp)
            print 'count of reviews to be loaded into database: '+str(len(reviews))
            db.persist_reviews(reviews, database)
        else:
            print 'found a None reviews.  unique_package='+str(unique_package) 
    print 'inhale reviews finished.'


# this functionality could be in inhale_reviews but I leave it here for symmetry with the scrape_and_extract_apps script, so that an opportunity for shared code here might pop out more visibily.  lol.
# how i'm currently using this:
#>>> import android_reviews
#>>> android_reviews.scrape_and_process_reviews('us','en')


#from android_market_data_public import scrape_and_extract_reviews
#from android import db
#from android import analysis
#scrape_timestamp=scrape_and_extract_reviews.scrape_and_process_reviews('us','en',no_cache=True,database='archive')
###scrape_timestamp=1316476792000L
#scrapes_that_need_v3=db.get_unique_scrape_timestamps_from_db_without_appbackr_score_v3(latest_timestamp=scrape_timestamp)
#scrapes_that_need_v3.reverse()
#print scrapes_that_need_v3
#map(lambda s: analysis.calculate_and_update_in_db_appbackr_score_v3_all(s,skip_if_already_in_db=True) , scrapes_that_need_v3)

#here's what's running on ec2-107-20-106-112.compute-1.amazonaws.com   on October 3:
#from android_market_data import scrape_and_extract_reviews
#from appbackr_android_market_data import db
#from appbackr_android_market_data import analysis
#while 1==1:
#      scrape_timestamp=scrape_and_extract_reviews.scrape_and_process_reviews('us','en',no_cache=True)
#      scrapes_that_need_v3=db.get_unique_scrape_timestamps_from_db_without_appbackr_score_v3(latest_timestamp=scrape_timestamp)
#      scrapes_that_need_v3.reverse()
#      print scrapes_that_need_v3
#      map(lambda s: analysis.calculate_and_update_in_db_appbackr_score_v3_all(s,skip_if_already_in_db=True) , scrapes_that_need_v3)
def scrape_and_process_reviews(country_code,language_code,unique_package_l=None, json_cache_path='new',resolved_urls_cache_path='new',now=None, no_cache=False,database='archive'):
    try:
        if not unique_package_l:
            print 'getting all unique_package values from db'
            unique_package_l=db.get_all_unique_packages('production')
        print 'unique_package_l count: '+str(len(unique_package_l))
        if not now:
            now=datetime.datetime.now()
        if not no_cache:
            if json_cache_path=='new':
                json_cache_path=utilities.make_new_dated_path('../cache/reviews/json_','/',now)
                print "json cache in:"+json_cache_path
                os.mkdir(json_cache_path)
            else:
                if not json_cache_path.endswith('/'):
                    json_cache_path+='/'
            if resolved_urls_cache_path=='new':
                resolved_urls_cache_path=utilities.make_new_dated_path('../cache/reviews/resolved_urls_','/',now)
                print "resolved_urls cache in:"+resolved_urls_cache_path
                os.mkdir(resolved_urls_cache_path)
            else:
                if not resolved_urls_cache_path.endswith('/'):
                    resolved_urls_cache_path+='/'
        print 'now:' + str(now)
        timestamp=int(time.mktime(now.timetuple()) * 1000)
        print 'timestamp:' + str(timestamp)
        print 'json cache dir: '+json_cache_path
        print 'resolved_urls_cache dir: '+resolved_urls_cache_path
        log_path=utilities.make_new_dated_path('../../cache/reviews/scrape_and_process_reviews_','.log',now)
        #log_file=open(log_path,'w')
        #print "log file: "+str(log_file)
        #print "now logging to that file"
        #sys.stdout=log_file
        #sys.stderr=log_file
        #print "now logging to file"
        #print "sys.stdout: "+str(sys.stdout)
        print 'timestamp:' + str(timestamp)
        #print 'json cache dir: '+json_cache_path
        #print 'resolved_urls_cache dir: '+resolved_urls_cache_path
        inhale_reviews(country_code,language_code,unique_package_l, json_cache_path, resolved_urls_cache_path,now,no_cache=no_cache,database=database)
        print 'done with inhale_reviews'
    except Exception as e:
        print 'exception broken out to top level of scrape_and_process_reviews'
        traceback.print_exc()
    print 'switching output back to stdout and stderr'
    #sys.stdout=sys.__stdout__
    #sys.stderr=sys.__stderr__
    #try:
     #   print 'log_file is a :'
     #   print type(log_file)
     #   print log_file
     #   if type(log_file)==file:
     #       print 'closing log file'
     #       log_file.close()
     #   else:
     #       print 'no file used in logging.'
    #except:
     #   print 'it appears we were logging to stdout. no need to close any log file.'
    print 'done with scrape'
    return timestamp


