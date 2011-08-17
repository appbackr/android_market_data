#! /usr/bin/env python
# scrape_and_extract_apps.py
# script to scrape
# usage from command line - obsolete:
# > ./scrape_android_market_phase_1A.py NEWS_AND_MAGAZINES PAID /Users/herdrick/shadow-dropbox/python/appbackr/cache/html_testing/ /Users/herdrick/shadow-dropbox/python/appbackr/cache/resolved_urls_testing/ ONLINE 0 1
# > ./scrape_android_market_phase_1A.py all PAID /Users/herdrick/shadow-dropbox/python/appbackr/cache/html_testing/ /Users/herdrick/shadow-dropbox/python/appbackr/cache/resolved_urls_testing/ ONLINE 0 1
# if 'all' is specified in place of a catagory (like GAME or NEWS_AND_MAGAZINES), then 'https://market.android.com/apps/GAME' will be scraped to get all the app categories from the left sidebar.  each category will be scraped.
if __name__ == "__main__":
    import sys
    arg_pos=0
    arg_pos+=1
    working_dir=sys.argv[arg_pos]
    arg_pos+=1
    category=sys.argv[arg_pos]
    arg_pos+=1
    paid_or_free=sys.argv[arg_pos].lower()
    arg_pos+=1
    offline_or_online=sys.argv[arg_pos].lower()
    arg_pos+=1
    html_cache_path=sys.argv[arg_pos]
    arg_pos+=1
    resolved_urls_cache_path=sys.argv[arg_pos]
    arg_pos+=1
    scrape_timestamp_s=sys.argv[arg_pos]
    arg_pos+=1
    starting_page=sys.argv[arg_pos]
    arg_pos+=1
    ending_page=sys.argv[arg_pos]
    print 'working_dir: '+working_dir
    print 'category: ' +category
    print 'paid_or_free: ' +paid_or_free
    print 'offline_or_online: ' +offline_or_online
    print 'html_cache_path: ' +html_cache_path
    print 'resolved_urls_cache_path: ' +resolved_urls_cache_path
    print 'scrape_timestamp_s: '+scrape_timestamp_s
    print 'starting_page: ' +starting_page
    print 'ending_page: '+ending_page 
    print
    print 'now starting scrape'
    import os
    os.chdir(working_dir)
    sys.path.append(working_dir)
    reload(sys)
    import datetime,time
    from android_market_data import utilities
    reload(utilities)
    from android_market_data import scrape_and_extract_apps
    reload(scrape_and_extract_apps)
    offline=offline_or_online.lower()=='offline'
    extraction_date=datetime.datetime.now()
    print 'extraction_date: '+str(extraction_date)
    print 'extraction_date converted to a timestamp: '+str(int(time.mktime(extraction_date.timetuple())*1000)) # int(time.mktime((datetime.datetime(2011,6,27,0,0,1)).timetuple())*1000)
    print
    if offline:
        print '--OFFLINE SCRAPE-- '
        print
        scrape_date=datetime.datetime.fromtimestamp(int(scrape_timestamp_s)/1000)
        if not html_cache_path.endswith('/'):
            html_cache_path+='/'            
        if not resolved_urls_cache_path.endswith('/'):
            resolved_urls_cache_path+='/'
    else:  #online scape - generate paths and times for timestamps
        print '--online scrape--'
        print
        if scrape_timestamp_s=='new':
            scrape_date=extraction_date
        else:
            print 'PROBLEM: this is an online scrape yet the scrape_timestamp was specified.  Bad.'
            raise Exception('PROBLEM: this is an online scrape yet the scrape_timestamp was specified.  Bad.')            
        if html_cache_path=='new':
            html_cache_path=utilities.make_new_dated_path('../cache/html_','_'+paid_or_free+'/',scrape_date)
            print "html cache in:"+html_cache_path
            os.mkdir(html_cache_path)
        else:
            print 'PROBLEM: this is an online scrape yet the cache path for html was specified.  Bad.'
            raise Exception('PROBLEM: this is an online scrape yet the cache path for html was specified.  Bad.')
        if resolved_urls_cache_path=='new':
            resolved_urls_cache_path=utilities.make_new_dated_path('../cache/resolved_urls_','_'+paid_or_free+'/',scrape_date)
            print "resolved_urls cache in:"+resolved_urls_cache_path
            os.mkdir(resolved_urls_cache_path)
        else:
            print 'PROBLEM: this is an online scrape yet the cache path for resolved urls was specified.  Bad.'
            raise Exception('PROBLEM: this is an online scrape yet the cache path for resolved urls was specified.  Bad.')
 
    print
    print 'scrape_date converted to a timestamp: '+str(int(time.mktime(scrape_date.timetuple())*1000)) # int(time.mktime((datetime.datetime(2011,6,27,0,0,1)).timetuple())*1000)
    print 'html_cache_path: ' +html_cache_path
    print 'resolved_urls_cache_path: ' +resolved_urls_cache_path
    try:
        log_path=utilities.make_new_dated_path('../cache/scrape_'+paid_or_free+'_','.log',extraction_date)
        log_file=open(log_path,'w')
        #log_file=sys.stdout
        print "log file: "+str(log_file)
        print "now logging to that file"
        sys.stdout=log_file
        sys.stderr=log_file
        print "now logging to file"

        #need to call set_globals here only because the call to get_categories needs them.  it's clumsy doing this here, and later on in inhale_market_data too.     
        #set_globals(html_cache_path,resolved_urls_cache_path,offline)
        pay_types=[]
        if paid_or_free=='all':
            print 'pay types = all'
            pay_types=['paid','free']
        else:
            print 'paid_or_free is not equal to all:'+paid_or_free
            pay_types=[paid_or_free]
        print "pay types"+str(pay_types)
        for pay_type in pay_types:
            if category.lower()=='all':
                cats=get_categories('https://market.android.com/apps/GAME',use_cache=False)
            else:  
                cats=[category]
            print 'categories.  (count: '+str(len(cats))+') '+str(cats)
            for cat in cats:
                scrape_and_extract_apps.inhale_market_data(category=cat,paid=(pay_type.lower()=='paid'), html_cache_path=html_cache_path, resolved_urls_cache_path=resolved_urls_cache_path, scrape_date=scrape_date, extraction_date=extraction_date, offline=(offline_or_online.lower()=='offline'),starting_page=int(starting_page),ending_page=int(ending_page))
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__
        print 'finished with scrape.'
    finally:
        try:
            print 'log_file is a :'
            print type(log_file)
            print log_file
            if os.path.isfile(log_file):
                log_file.close()
        except:
            print 'it appears we were logging to stdout. no need to close the log file.'
    print 'finished with scrape and closed log file, if any.'
