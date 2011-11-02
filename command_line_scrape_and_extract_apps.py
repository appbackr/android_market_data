#! /usr/bin/env python
# command_line_scrape_and_extract_apps.py
import sys
reload(sys)
sys.path.append('/Users/herdrick/appbackr/appbackr_data_science/')
sys.setdefaultencoding('utf-8')
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
    max_ending_page=sys.argv[arg_pos]
    arg_pos+=1
    profiler_web_server_port=sys.argv[arg_pos]
    print 'working_dir: '+working_dir
    print 'category: ' +category
    print 'paid_or_free: ' +paid_or_free
    print 'offline_or_online: ' +offline_or_online
    print 'html_cache_path: ' +html_cache_path
    print 'resolved_urls_cache_path: ' +resolved_urls_cache_path
    print 'starting_page: ' +starting_page
    print 'max_ending_page: '+max_ending_page
    print 'scrape_timestamp_s: '+scrape_timestamp_s
    print 'profiler_web_server_port: '+profiler_web_server_port
    print

    # for memory profiling:
    #import cherrypy
    #import dowser
    #cherrypy.config.update({'server.socket_port': int(profiler_web_server_port)})
    #cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    #cherrypy.tree.mount(dowser.Root())
    #cherrypy.engine.autoreload.unsubscribe()
    ### Windows only                                                                                                                                                                                    
    ###cherrypy._console_control_handler.unsubscribe()                                                                                                                                                  
    #cherrypy.engine.start()

    print 'now starting scrape'
    import os
    os.chdir(working_dir)
    sys.path.append(working_dir)
    reload(sys)
    import datetime,time
    from common import utilities
    reload(utilities)
    from android_market_data_public import scrape_and_extract_apps
    reload(scrape_and_extract_apps)
    from android import analysis
    from android import db
    offline=offline_or_online.lower()=='offline'
    extraction_date=datetime.datetime.now()
    start_time=datetime.datetime.now()
    print 'time is: '+str(start_time)
    print 'extraction_date: '+str(extraction_date)
    print 'extraction_date converted to a timestamp: '+str(int(time.mktime(extraction_date.timetuple())*1000)) # int(time.mktime((datetime.datetime(2011,6,27,0,0,1)).timetuple())*1000)
    print
    if offline:
        print '--OFFLINE SCRAPE-- '
        print
        scrape_timestamp=int(scrape_timestamp_s)
        scrape_date=datetime.datetime.fromtimestamp(scrape_timestamp/1000)
        if not html_cache_path.endswith('/'):
            html_cache_path+='/'            
        if not resolved_urls_cache_path.endswith('/'):
            resolved_urls_cache_path+='/'
    else:  #online scape - generate paths and times for timestamps
        print '--online scrape--'
        print
        if scrape_timestamp_s=='new':
            scrape_date=extraction_date
            scrape_timestamp=(int(time.mktime(scrape_date.timetuple())*1000))
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
        print "log file: "+str(log_file)
        print "now logging to that file"
        #sys.stdout=log_file
        #sys.stderr=log_file
        print "now logging to file"
        print 'making stdout and stderr unbuffered (actually buffered only per call to write())'
        #sys.stdout=utilities.Unbuffered(sys.stdout)
        #sys.stderr =utilities.Unbuffered(sys.stderr)

        #need to call set_globals here only because the call to get_categories needs them.  it's clumsy doing this here, and later on in inhale_market_data too.     
        #set_globals(html_cache_path,resolved_urls_cache_path,offline)
        paid_or_free=paid_or_free.lower()
        print 'paid_or_free :'+paid_or_free
        if category.lower()=='all':
            cats=scrape_and_extract_apps.get_categories()
        else:  
            cats=[category]
        print 'categories count: '+str(len(cats))+'  '+str(cats)
        for cat in cats:
            scrape_and_extract_apps.inhale_market_data(category=cat,paid=(paid_or_free=='paid'), html_cache_path=html_cache_path, resolved_urls_cache_path=resolved_urls_cache_path, scrape_date=scrape_date, extraction_date=extraction_date, offline=(offline_or_online.lower()=='offline'),starting_page=int(starting_page),max_ending_page=int(max_ending_page))
        print 'finished with scrape.'
        print 'now filling in calculated values in rows'
        analysis.fill_in_calculated_values(scrape_timestamp)
        print 'finished with filling in calculated values.'
        #print 'there are now '+count+' apps with this scrape_timestamp in the db.'
        print 'now declaring this was a good scrape.'
        db.record_scrape(scrape_timestamp,paid_or_free=paid_or_free)
        print 'scrape and fill in is finished'        
    finally:
        try:
            print 'closing things out'
            #cherrypy.engine.exit()
            print 'log_file is a :'
            print type(log_file)
            print log_file
            sys.stdout=sys.__stdout__
            sys.stderr=sys.__stderr__
            if type(log_file)==file:
                print 'closing log file'
                log_file.flush()
                log_file.close()
        except:
            print 'it appears we were logging to stdout. no need to close any log file.'
    print 'finished with scrape and closed log file, if any.'
    end_time=datetime.datetime.now()
    print 'scrape time:'+str(start_time)
    print 'scrape end time:  '+str(end_time)
    print 'elapsed time:     '+str(end_time-start_time)



