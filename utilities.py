import unicodedata, re, os.path, urlparse, sys
sys.setdefaultencoding('utf-8')
# utilities

# very shaky, needs refactor.  Consider making FP.
def merge_dicts_add_values(d1,d2):
    #result_dict={}
    for k in d2.keys():
        if d1.has_key(k): 
            d1[k]=d1[k] + d2[k]
        else:
            d1[k]=d2[k]

def dicts_column(dicts,key):
    column=[]
    for d in dicts:
        column+=[d[key]]
    return column

#currently broken, only because I removed the import of numpy.  Just import numpy (ha!) and enjoy.  
def column_mean(dicts,key):
    vals=dicts_column(dicts,key)
    vals_floats=map(lambda x: float(x), vals)
    return numpy.mean(vals_floats)

#    Flatten one level of nesting
def flatten_1(l):
    return [item for sublist in l for item in sublist]

def url_param(u,name):
    return urlparse.parse_qs(urlparse.urlparse(u).query)[name][0]

def make_url_absolute(base,relative):
    return base+relative

def normalize(value, maximum):
    normalized=value*1.0/maximum  # 1.0 to force value to float
    if normalized>1:
        raise Exception ('wtf - a normalized value is > 1.   original value was: '+str(value)+'        maximum='+maximum)
    return normalized

def duplicates(l):
    duplicates = set()
    found = set()
    for item in l:
        if item in found:
            duplicates.add(item)
        else:
            found.add(item)
    return duplicates

#rename map_dict_values
def map_all_dict_values(f,d):
    for k in d.keys():
        d[k]=f(d[k])

def foreach_dict_value(f,d):
    for k in d.keys():
        f(d[k])

def grep_dict(pattern,d):
    hits=[]
    p=re.compile('.*'+pattern+'.*')
    for k in d.keys():
        if p.match(str(d[k])):
            hits.append(d[k])
    return hits

#def defaultdict_from_dict(d,default_factory):
#    dd=collections.defaultdict(default_factory)
#    for k in d.keys():
#        dd[k]=d[k]
#    return dd

# just ensures that there is some value for 'keys'
def ensure_values_for_keys(d,keys):
    for k in keys:
        if not d.has_key(k):
            d[k]=''


# how I found the bad chars:  map(lambda d: grep_dict('\t',d), paid_528_ranked)    and   map(lambda d: grep_dict('\n',d), paid_528_ranked)
# how I fixed them: map(lambda d: values_to_strings_and_cleaned('\t',' ',d), paid_528_ranked)   and  map(lambda d: values_to_strings_and_cleaned('\n','',d), paid_528_ranked)
#cleans out instances of pattern from all values in dict d
def values_to_strings_and_cleaned(pattern,replacement,d):
    for k in d.keys():
        d[k]=re.sub(pattern,replacement,str(d[k]))

def dict_list_to_dict_of_dicts(dicts,field_to_make_key):
    dict_of_dicts={}
    for d in dicts:
        new_key=d[field_to_make_key]
        dict_of_dicts[new_key]=d
    return dict_of_dicts    

def dict_of_dicts_to_dict_list(dicts_d):
    dict_l=[]
    for k in dicts_d.keys():
        dict_l+=[dicts_d[k]]
    return dict_l    

#not finished
def list_list_to_dict_of_dicts(lists,index_to_use_for_key):
    dict_of_dicts={}
    for l in lists:
        key=l[index_to_use_for_key]
        dict_of_dicts[key]=l
    return dict_of_dicts    


# Filesystem utils
#greps one file.   does nothing if path is a dir
#doesn't do regex yet
def grep(string, path, return_string_match, return_file=False, stop_after_one_match=False):
    if os.path.isfile(path):
        f=open(path)
        lines=f.readlines()
        for i in range(len(lines)):
            line=lines[i]
            if string in line:
                if return_file:
                    print(path)
                if return_string_match:
                    #sys.stdout.write (line)
                    map(sys.stdout.write, lines[i:i+3])
                if stop_after_one_match:
                    break
        f.close()

# calls fn on every file or dir or whatever in path, recursively to depth max_depth
def recur_over_dirs(fn,path,max_depth):
    #print 'path='+path
    fn(path)
    if os.path.isdir(path) and max_depth>=0:
        #'/Users/herdrick/shadow-dropbox/python/envs/cache'
        ls_relative=commands.getoutput('ls '+path).splitlines()
        ls_absolute=map(lambda f: os.path.abspath(os.path.join(path, f)), ls_relative)
        #top_level_files=filter  (os.path.isfile, ls_top_level_absolute)
        #dirs=filter (os.path.isdir, ls_absolute)
        map(lambda p: recur_over_dirs(fn,p,max_depth-1), ls_absolute)  #filter(lambda p: p!='.', ls_absolute))



# for new code, use _clean_for_path_improved, below.  this function must be kept here, and used, to remain compatible with the older HTML caches.  Ouch.  
_clean_for_path_remove_regex = re.compile(r'[^\s\w.:-]')
_clean_for_path_hyphenate_regex = re.compile(r'[\s\:-]+')  # there is a bug here.  I meant for the hyphen to be literally interpreted.  Instead it's making some kind of wacky range here, like 'colon thru... whatever'.  I'm not even sure what all it's doing here.  
def _clean_for_path(txt): 
    if not isinstance(txt, unicode):
        txt = unicode(txt)
    txt = unicodedata.normalize('NFKD', txt)
    txt = txt.encode('ascii', 'ignore')
    txt = unicode(_clean_for_path_remove_regex.sub('', txt).strip().lower())
    return _clean_for_path_hyphenate_regex.sub('-', txt)

#kills all but word characters.  
def _clean_for_path_improved(txt):
    txt=re.compile(r'\W').sub('', txt).strip().lower()
    if not isinstance(txt, unicode):
        txt = unicode(txt)
    txt = unicodedata.normalize('NFKD', txt)
    txt = txt.encode('ascii', 'ignore')
    return txt

#if it's April 10, 2011 at 8:58am and 41 seconds and there's already a dir_base_2011_4_10/, then see if dir_base_2011_4_10_8/ exists.  If that already exists, then try dir_base_2011_4_10_8_58/.  If that already exists, then try dir_base_2011_4_10_8_58_41.  If that doesn't work, then just append a random string.  Now, that latter option isn't great, because it's certainly not going to be consistent across the two dir paths used for cacheing, the one for HTML and the other for urls, but this is anticipated to be rare.
def make_new_dated_path(base_path,suffix,now,hours=False,minutes=False,seconds=False, random_string=False):
    now_s=str(now.year)+'_'+str(now.month)+'_'+str(now.day)
    if hours:
        now_s+='_'+str(now.hour)
    if minutes:
        now_s+='_'+str(now.minute)
    if seconds:
        now_s+='_'+str(now.second)
    if random_string:
        now_s+='_'+_clean_for_path_improved(os.urandom(40))
    path=base_path+now_s+suffix
    if os.path.exists(path):
        print 'that path exists'
        if random_string:
            raise 'Somehow we cannot make a unique path.  Weird.'+'  Last path tried is '+path
        return make_new_dated_path(base_path,suffix,now,hours=True,minutes=hours,seconds=minutes,random_string=seconds) # amusing how this works, no?  If hours was *previously* True, then we need to specify minutes this time.  If minutes was *previously* True, then we need to specify seconds this time.  if seconds was previously true, then we need to add in a random string.
    else:
        return path

#end filesystem utils

# Crappy / weird / one-off functions:

def dict_of_empties(d):
    try:
        for key in d.keys():
            if len(d[key]) > 0:
                return False
        return True
    except Exception as e:
        print e
