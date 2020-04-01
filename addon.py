#!/usr/bin/python
# coding=utf-8

import sys,xbmc,urlparse,xbmcplugin,xbmcgui,urllib,re,xbmcaddon,urllib2,base64,threading,time,os
import requests
import resolveurl

from lib.tugastream.web import dev_http



__handle__ = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
base_url = sys.argv[0]
PARAMS = dict(urlparse.parse_qsl(sys.argv[2][1:]))
__addon__       = xbmcaddon.Addon(id='plugin.video.tuga.stream')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
addonID       = __addon__.getAddonInfo('id')
wtpath = __addon__.getAddonInfo('path')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
mensagemok = xbmcgui.Dialog().ok

__CACHE_FOLDER__ = addonUserDataFolder + "\\"
if (not os.path.isdir(__CACHE_FOLDER__)):
    os.mkdir(__CACHE_FOLDER__)

__LEGENDAS__ = __CACHE_FOLDER__ + "subtitle.srt"
__FICHEIRO_VIDEO__ = __CACHE_FOLDER__ + "video.mp4"




def makeRequest(url, headers=None,timeout=1):
        try:
            if headers is None:
                headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, lmagellan Gecko) Chrome/52.0.2743.116 Safari/537.36'}
            if '|' in url:
                url,header_in_page=url.split('|')
                header_in_page=header_in_page.split('&')
                for h in header_in_page:
                    if len(h.split('='))==2:
                        n,v=h.split('=')
                    else:
                        vals=h.split('=')
                        n=vals[0]
                        v='='.join(vals[1:])
                        #n,v=h.split('=')
                    #print(n,v)
                    headers[n]=v
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req,timeout=timeout)
            data = response.read()
            response.close()
            return data
        except:
            try:
                # Try Other Lib ??
                r = requests.get(url, headers=headers, timeout=timeout)
                return r.content()
            except:
                print("HTTP-ERROR ---> " + url)
                return None

HOST_LINK = "https://www.dropbox.com/s/lekqu0fugf7unaj/tugatvhost.txt?dl=1"
TUGA_HOST = "https://www.tugastream.club/" #base64.b64decode(makeRequest(HOST_LINK,timeout=2))


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def create_dir(name,url,title="",genre="",thumb="",icon="",fanart="",is_folder=True):
    list_item = xbmcgui.ListItem(label=name)
    list_item.setArt({'thumb': thumb,
                          'icon': icon,
                          'fanart': fanart})
    list_item.setInfo('video', {'title': title,
                                'genre': genre,
                                'mediatype': 'video'})
    xbmcplugin.addDirectoryItem(__handle__, url, list_item, is_folder)

def do_menu():
    create_dir('Filmes', build_url({'mode': 'folder', 'action': 'Filmes|/filmes'}), 'Filmes', 'Filmes')
    create_dir('Series', build_url({'mode': 'folder', 'action': 'Series|/series'}), 'Series', 'Series')
    create_dir('Pesquisar', build_url({'mode': 'folder', 'action': 'Pesquisar'}), 'Pesquisar', 'Pesquisar')

def read_file(filename):
    f = open(filename, "r")
    data = f.read()
    f.close()
    return data

def write_subtitles(subtitles):
    write_file(__LEGENDAS__, subtitles)

def write_file(filename, content):
    f = open(filename, "w")
    f.write(content)
    f.close()

def http_GET(uri,timeout):
    try:
        return requests.get(url = uri, timeout=timeout, allow_redirects=True)
    except:return requests.get(url = uri, timeout=timeout * 2, allow_redirects=True)

def check_tugastream_html(data_txt):
    _check_ = re.findall('<title>([^"]*)<\/title>', data_txt)
    if (len(_check_) > 0):
        if('TUGAstream' in _check_[0]):
            return True
    return False

def fuck_cloudfare(link):
    resolve_js = """
	function resolvecf(){

        $(VAR_ONE)

        g = String.fromCharCode;
        o = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
        e = function(s) {
          s += "==".slice(2 - (s.length & 3));
          var bm, r = "", r1, r2, i = 0;
          for (; i < s.length;) {
              bm = o.indexOf(s.charAt(i++)) << 18 | o.indexOf(s.charAt(i++)) << 12
                      | (r1 = o.indexOf(s.charAt(i++))) << 6 | (r2 = o.indexOf(s.charAt(i++)));
              r += r1 === 64 ? g(bm >> 16 & 255)
                      : r2 === 64 ? g(bm >> 16 & 255, bm >> 8 & 255)
                      : g(bm >> 16 & 255, bm >> 8 & 255, bm & 255);
          }
          return r;
        };

        $(VAR_TWO)

    }

resolvecf()
"""
    r = http_GET(link ,8)
    data = r.content
    print(data)
    _POST_LINK_ = None
    _POST_VAR_ONE_ = None
    _POST_VALUE_ONE_ = None
    _POST_VAR_JSCHLVC_ = None
    _POST_VAR_JS_NONCENSE_ = None
    post_link_res = re.findall('<form id="challenge-form" action="([^"]*)" method="POST" enctype="([^"]*)">', data)
    if (len(post_link_res) > 0):
        _POST_LINK_ = post_link_res[0][0]
        print(_POST_LINK_)
    post_data_res = re.findall('<input type="hidden" name="([^"]*)" value="([^"]*)"\/>', data)
    if (len(post_data_res) > 0):
        _POST_VAR_ONE_ = post_data_res[0][0]
        _POST_VALUE_ONE_ = post_data_res[0][1]
        print(str(post_data_res))
    post_data_jschl_vc_res = re.findall('<input type="hidden" id="jschl-vc" name="jschl_vc" value="([^"]*)"\/>', data)
    if (len(post_data_jschl_vc_res) > 0):
        _POST_VAR_JSCHLVC_ = post_data_jschl_vc_res[0]
        print(str(post_data_jschl_vc_res))
    post_data_noncense_res = re.findall('<div style="display:none;visibility:hidden;" id="([^"]*)">([^"]*)<\/div>', data)
    if (len(post_data_noncense_res) > 0):
        _POST_VAR_JS_NONCENSE_ = post_data_noncense_res[0][1]
        print(str(post_data_noncense_res))
    pass_res = re.findall('<input type="hidden" name="pass" value="([^"]*)"\/>',data)
    parts = data.split('<script type="text/javascript">')
    for part in parts:
        if ('function()' in part):
            if ('</script>' in part):
                scr = part.split('</script>')[0]
                #print("La part ---------> " + scr)
                code_parts = scr.split(';')
                _var_class_ = None
                valid_code_one = None
                _var_parts_ = ""
                for codes in code_parts:
                    _has_the_one = False
                    #print("Code_part ----> " + codes)
                    if ('setTimeout(' in codes):
                        valid_code_one = codes.split('(){')[1].split('}')[0] + '}'
                        _var_class_ = valid_code_one.split('={')[0].split('var')[1].split(' ')[2]
                        _has_the_one = True
                    if (_var_class_):
                        if (_var_class_ in codes and _has_the_one == False):
                            if (codes):
                                print("Parcel --------------------------->" + codes)
                                if ('function(p)' in codes and 'Element' in codes):
                                    #after_var = codes.split('var p =')[1]
                                    #print("Change this one ---------> " + codes.split('var p =')[0] + " - var p = " + _POST_VAR_JS_NONCENSE_ + ';\n')
                                    _var_parts_ += codes.split('var p =')[0] + " var p = " + _POST_VAR_JS_NONCENSE_ + '; \n return +(p)}(); \n'
                                    print("others -----------> " + codes.split('var p =')[1]  )
                                if ('function(p)' in codes and 'italics' in codes):
                                    print("UPS CANT DECODE THIS.................!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                else:
                                    _var_parts_ += codes + ';\n'
                print("Precious here -----------> " + valid_code_one)
                _var_parts_ = _var_parts_.replace('a.value =', 'return')
                print("Precious 22222222222222222222 here -----------> " + _var_parts_)
                resolve_js = resolve_js.replace('$(VAR_ONE)', valid_code_one)
                resolve_js = resolve_js.replace('$(VAR_TWO)', _var_parts_)
                print("Run This babe -----------> " + resolve_js)
    dat = {_POST_VAR_ONE_: _POST_VALUE_ONE_,
            'jschl_vc': _POST_VAR_JSCHLVC_,
            'pass':pass_res[0],
            'jschl_answer':'NaN'
            }
    #po = requests.post(TUGA_HOST + _POST_LINK_, data=dat)
    #print("PLZ -----> " + po.content)


def fetch_movies(url):
    r = http_GET(url,8)
    data = r.content
    _valid = check_tugastream_html(data)
    if(not _valid):
        mensagemok("Cloudfare","Cloudfare is back on")
        fuck_cloudfare(url)
    movies = data.split('<div id="archive-content"')
    for movs in movies:
        if ('article' in movs):
            mov = movs.split('<article')
            for video in mov:
                if(not 'w_item_b' in video):
                    if (not 'featured' in video):
                        _img_ = None
                        _name_ = None
                        _link_ = None
                        picture = re.findall('<img src="([^"]*)" alt="([^"]*)">', video)
                        if (len(picture) > 0):
                            _img_ = picture[0][0]
                            _name_= picture[0][1]
                        link_res = re.findall('<a href="([^"]*)">', video)
                        if(len(link_res) > 0):
                            _link_ = link_res[0]
                        if(_img_ and _name_ and _link_):
                            url = build_url({'name': _name_, 'action': 'movie|' + _link_})
                            create_dir(_name_,url,title=_name_,thumb=_img_,is_folder=False)
    fetch_next_movies_page(data)

def fetch_next_movies_page(data):
    next_page_res = data.split('<div class="pagination">')
    for np in next_page_res:
        if ('class="current"' in np):
            if ('</div>' in np):
                _nav_ = np.split('</div>')
                for nv in _nav_:
                    if ('class="current"' in nv):
                        next_res = re.findall('''<a class='arrow_pag' href="([^"]*)">''', nv)
                        if (len(next_res) > 0):
                            url = build_url({'mode': 'folder', 'action': 'Filmes|' + next_res[0]})
                            create_dir("Proxima Pagina",url,title="Proxima Pagina",is_folder=True)

def get_host_from_link(link):
    s = link
    host_list = s.split('/')[:3]
    string = ""
    for h in host_list:
        string += h + '/'
    return string

def parse_download_option(data,list,pdialog):
    down_res = data.split('<div class="links_table">')
    _file_download = None
    for down in down_res:
        if ('Download' in down):
            d = down.split('</div>')[0]
            res_sults = re.findall('<a href="([^"]*)" target="_blank">Download<\/a>', d)
            if (len(res_sults) > 0):
                pdialog.update(10,'Fetching Download File')
                r = requests.get(res_sults[0], allow_redirects=True, timeout=8)
                if ('s=' in r.url):
                    nurl = r.url.split('s=')[1]
                    _file_download = nurl
    return _file_download

def parse_servers(data,_file_download,slist,namelist):
    cont = '<iframe class="metaframe rptss" src="([^"]*)" frameborder="0" scrolling="no" allowfullscreen><\/iframe>'
    urls = re.findall(cont, data)
    if (_file_download):
        urls.append(_file_download)
    if (len(urls) > 0):
        for url in urls:
            _url_ = url
            if(not 'https:' in _url_):
                _url_ = 'https:' + _url_
            _name_ = _url_.split('//')[1].split('/')[0]
            slist.append(_name_ + '|' + _url_)
        for s in slist:
            namelist.append(s.split('|')[0])
    return slist,namelist


def mixdrop_after_resolve(browse_link,pdialog):
    resolved = False
    subtitles = None
    if ('sub=' in browse_link):
        pdialog.update(25,'Fetching Subtitles')
        subtitles = browse_link.split('sub=')[1]
        r = http_GET(subtitles, 7)
        subtitles = r.content
    pdialog.update(50,'Parsing JS...')
    try:
        # Using a resolver agains my wheel
        resolved = resolveurl.resolve(browse_link)
        print("Link Resolved ---> " + resolved)
    except:
        mensagemok("Video","Video não disponivel.")
        return 0
    if (resolved != False):
        play_item = xbmcgui.ListItem(path=resolved)
        # Mixdrop as small download subs
        if(not subtitles):
            pdialog.update(65,'Fetching Subtitles')
            subtitles = mixdrop_subs_getter(browse_link)
        if (subtitles):
            pdialog.update(75,'Adding Subtitles')
            write_file(__LEGENDAS__, subtitles)
            play_item.setSubtitles([__LEGENDAS__])
        _player_ = xbmc.Player()
        print("Starting mixdrop VPlayer --->")
        pdialog.update(95,'Enjoy')
        pdialog.close()
        _player_.play(resolved, play_item)
        check_if_video_started(_player_,resolved,__LEGENDAS__)

def feurl_parse_subs_in_link(browse_link):
    if ('caption=' in browse_link):
        _legendas_ = browse_link.split('caption=')[1]
        r = http_GET(_legendas_, 5)
        _legenda_ = r.content
        if (_legenda_):
            return _legenda_
    return None

def feurl_resolve_subtitle(data,_t_id):
    if (data["captions"]):
        _caption_id_ = data["captions"][0]["id"]
        _extension_ = data["captions"][0]["extension"]
        _data_player_ = data["player"]["poster_file"]
        _list_ = _data_player_.split('/')[:-4]
        _data_ = ""
        for sla in _list_:
            if (sla != ''):
                _data_ += '/' + sla
        sub_link = "https://feurl.com/asset" + _data_ + '/caption/' + _t_id + '/' + _caption_id_ + '.' + _extension_
        r = http_GET(sub_link, 5)
        return  r.content
    return None

def feurl_organize_quality_links(data):
    slist = []
    namelist = []
    for file_ in data["data"]:
        _p_ = file_["label"]
        _link_ = file_["file"]
        slist.append(_p_ + '|' + _link_)
    for s in slist:
        namelist.append(s.split('|')[0])
    return slist,namelist


def feurl_after_resolver(browse_link,pDialog):
    #print('feurl----> ' + browse_link)
    _legendas_ = None
    _t_url_ = browse_link.split('/')[-1]
    if ('caption=' in browse_link):
        _t_url_ = browse_link.split('#')[0].split('/')[-1]
    _legendas_ = feurl_parse_subs_in_link(browse_link)
    pDialog.update(50,'Resolving Feurl...')
    r = requests.post('https://feurl.com/api/source/' + _t_url_, timeout=8)
    import json
    data = json.loads(r.content)
    _link_ = None
    pDialog.update(60,'Parsing Response...')
    if (not _legendas_):
        _legendas_ = feurl_resolve_subtitle(data, _t_url_)
    slist,namelist = feurl_organize_quality_links(data)
    pDialog.close()
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Choose a quality', namelist)
    _link_ = slist[ret].split('|')[1]
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('URL', 'Redirecting...')
    pDialog.update(70,'Parsing selected quality...')
    try:
        r = requests.head(_link_, allow_redirects=True, timeout=8)
        resolved = r.url
        print("feurl resolved ----> " + resolved)
    except:resolved = _link_
    play_item = xbmcgui.ListItem(path= resolved)
    if (_legendas_):
        pDialog.update(80,'Fetching Subtitles')
        write_subtitles(_legendas_)
        play_item.setSubtitles([__LEGENDAS__])
    _player_ = xbmc.Player()
    print("Starting feurl VPlayer --->")
    pDialog.update(95,'Enjoy')
    _player_.play(resolved, play_item)
    check_if_video_started(_player_,resolved,__LEGENDAS__,_link_)


def openplayer_after_resolver(browse_link,pDialog):
    op_link = browse_link
    up = 33
    pDialog.update(up, 'Running OpenPlayer Bruteforce AI ...')
    # This fella needs a push couse it can fail several times
    good_resolved = None
    for i in range(5):
        up += (5 + i)
        pDialog.update(up,'Resolving Openplayer..')
        resolved,subs = openplayer_resolver(op_link)
        if (resolved and subs):
            good_resolved = resolved
            break
        elif(resolved and not subs):
            good_resolved = resolved
    if (good_resolved):
        _ALIVE_ = True
        if (_ALIVE_):
            pDialog.update(75,'Enjoy...')
            play_item = xbmcgui.ListItem(path=resolved)
            if (subs):
                f = open(addonUserDataFolder + "leg.srt", "w")
                f.write(subs)
                f.close()
                play_item.setSubtitles([addonUserDataFolder + "leg.srt"])
            pDialog.close()
            _player_ = xbmc.Player()
            _player_.play(resolved, play_item)




# Threading is the only way of not compromise the player work
def check_if_video_started(player,link,subtitles,alternative_link="",timeout=1000,retry=40):
    x = threading.Thread(target=_check_if_video_started_, args=(player, link, subtitles, alternative_link, timeout, retry,))
    x.start()
def _check_if_video_started_(player,link,subtitles,alternative_link="",timeout=1000,retry=40):
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Checking if video starts ...')
    for i in range(retry):
        pDialog.update( int((i * 100) / retry), 'A verificar ...')
        if (player.isPlayingVideo()):
            return i
        xbmc.sleep(timeout)
    pDialog.update(33, 'O lançamento falhou ...\n A lançar de novo ...')
    xbmc.sleep(2000)
    if (alternative_link != ""):
        link = alternative_link
    y = threading.Thread(target=play_movie_file, args=(link,subtitles,False,))
    y.start()
    pDialog.close()




def router(paramstring):
    if paramstring:
        if ( "Filmes|" in paramstring['action']):
            uri = paramstring['action'].split("|")[1]
            if (uri == '/filmes'):
                fetch_movies(TUGA_HOST + uri)
            else:fetch_movies(uri)
        elif ( "movie|" in paramstring['action']):
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('Servers', 'Fetching Servers')
            uri = paramstring['action'].split("|")[1]
            r = http_GET(uri,8)
            data = r.content
            slist = []
            namelist = []
            _file_download = parse_download_option(data, slist, pDialog)
            slist, namelist = parse_servers(data,_file_download,slist,namelist)
            pDialog.close()
            if (len(slist) > 0):
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Choose a Server', namelist)
                browse_link = slist[ret].split('|')[1]
                print("Selected Link ---> " + browse_link)
                pDialog = xbmcgui.DialogProgress()
                pDialog.create('URL', 'Parsing URL')
                if ('mixdrop' in get_host_from_link(browse_link)):
                    mixdrop_after_resolve(browse_link,pDialog)
                elif ('feurl' in get_host_from_link(browse_link)):
                    feurl_after_resolver(browse_link,pDialog)
                elif ('openplayer' in get_host_from_link(browse_link)):
                    openplayer_after_resolver(browse_link,pDialog)
                elif('1fichier' in get_host_from_link(browse_link)):
                    onefichier_after_resolver(browse_link,pDialog,slist)
    else:
        do_menu()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def onefichier_can_download(data):
    res_wait = re.findall('<br\/>You must wait ([^"]*) ...', data)
    if (len(res_wait) > 0):
        wait_time = res_wait[0].split('...')[0] + ' ...'
        return wait_time
    else:return True

def onefichier_subtitles_fetcher(_old_links):
    for link in _old_links:
        _host_ = link.split('|')[0]
        _link_ = link.split('|')[1]
        if ('mixdrop' in _host_):
            subtitles_one_fichier = mixdrop_subs_getter(_link_)
            if (subtitles_one_fichier):
                write_subtitles(subtitles_one_fichier)
                return __LEGENDAS__
    return False

def onefichier_downloader(resolved,pDialog,subtitles=None):
    _PLAYING_ = False
    u = urllib2.urlopen(resolved)
    file_name = __CACHE_FOLDER__ + "vid.mp4"
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    pDialog.close()
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Download')
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        _percent_ = (file_size_dl * 100. / file_size)
        _fake_percent_ = int((_percent_ * 100) / 5)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        pDialog.update(_fake_percent_, str(status)  + '\nAtenção o download é sequencial, não deve avançar.')
        if (_percent_ > 5 and _PLAYING_ == False):
            pDialog.close()
            _PLAYING_ = True
            x = threading.Thread(target=play_movie_file, args=(file_name,subtitles,True,))
            x.start()
    f.close()
    pDialog.close()

def onefichier_after_resolver(browse_link,pDialog,slist):
    if ('&' in browse_link):
        browse_link = browse_link.split('&')[0]
    print("ONEFichier FILE ---> " + browse_link)
    pDialog.update(35,'Fetching noncenses...')
    r = http_GET(browse_link, 5)
    _ns_name = None
    _ns_val = None
    _subtitles_ = None
    _res_wait_ = onefichier_can_download(r.content)
    if (_res_wait_ == True):
        res_nonsense = re.findall('<input type="hidden" name="([^"]*)" value="([^"]*)" \/>', r.content)
        if (len(res_nonsense) > 0):
            _ns_name = res_nonsense[0][0]
            _ns_val = res_nonsense[0][1]
        if (_ns_name and _ns_val):
            data = { _ns_name: _ns_val }
            pDialog.update(55,'Posting noncenses...')
            r = requests.post(browse_link, data, timeout=5)
            r_link = re.findall('<a href="([^"]*)"  style="([^"]*)" class="ok btn-general btn-orange">Click here to download the file<\/a>', r.content)
            if (len(r_link) > 0):
                if (len(r_link[0]) > 0):
                    # We got it! START ----
                    _subtitles_ = onefichier_subtitles_fetcher(slist)
                    resolved = r_link[0][0]
                    onefichier_downloader(resolved,pDialog,_subtitles_)
    else:
        pDialog.close()
        mensagemok("Lista de Espera", 'Aguarda : ' +  _res_wait_ + '\n Para poderes continuar o download')






def event_play_closed(player, deleteFile=""):
    if (player.isPlayingVideo() == True):
        while player.isPlaying():
            xbmc.sleep(1000)
    # Movie closed here
    if (deleteFile != ""):
        try:os.remove(deleteFile)
        except:print("Cound't remove file...")

def play_movie_file(file_name,subtitles=None,deleteFile=False):
    play_item = xbmcgui.ListItem(path=file_name)
    if (subtitles):
        play_item.setSubtitles([subtitles])
    _player_ = xbmc.Player()
    _player_.play(file_name, play_item)
    if (deleteFile == False): y = threading.Thread(target=event_play_closed, args=(_player_,))
    else: y = threading.Thread(target=event_play_closed, args=(_player_,file_name,))
    y.start()



def openplayer_resolver(link):
    # We are calling the Orc Army here to BRUTEFORCE
    print("Resolving ----> " + link)
    r = requests.get(url = link, timeout=8)
    print(r.content)
    parts = r.content.split('/javascript">')
    i = 0
    for part in parts:
        if ('eval(function(' in part):
            sp = part.split("|")
            fs_var = None
            tok_var = None
            sub_var = None
            subs = None
            for s in sp:
                i += 1
                #print(s)
                if (i > 360):
                    print("var ---> " + s)
                    if (len(s) == 60):
                        print("Openplayer TOK_VAR (DEBUG) ---> " + s + " -> " + str(len(s)) )
                        tok_var = s
                    if (len(s) > 70 and sub_var == None and len(s) < 125 and '\\' not in s):
                        print("Openplayer SUBS_TOK_VAR (DEBUG) ---> " + s + " -> " + str(len(s)) )
                        sub_var = s
                        print("Queryng Subs at ---> " + "https://openplayer.net/api/mysub/?url=" + sub_var + '==')
                        r =  requests.get(url = "https://openplayer.net/api/mysub/?url=" + sub_var + '==', timeout=4)
                        subs = r.content
                    if ('fs' in str(s) and len(s) == 5):
                        print("Openplayer FS_VAR (DEBUG) ---> " + s + " -> " + str(len(s)) )
                        fs_var = s
                if (fs_var and tok_var):
                    _linkp_ = 'https://' + fs_var + '.gounlimited.to/' + tok_var + '/v.mp4'
                    print("Main Link ----- > " + _linkp_)
                    return _linkp_, subs
    return None,None



def mixdrop_subs_getter(url):
    for i in range(5):
        r = makeRequest(url, timeout=5)
        if (r):
            scripts = r.split('<script>')
            for script in scripts:
                if( 'MDCore.ref =' in script):
                    _ref_var_ = None
                    _tstamp_var_ = None
                    _checksum_var_ = None
                    _token_var_ = None
                    _delivery_var_ = None
                    _language_ = 'pt'
                    _one_len_list_ = []
                    info = script.split('</script>')[0]
                    #print(info)
                    _ref_var_res_ = re.findall('MDCore.ref = "([^"]*)";', info)
                    if (len(_ref_var_res_) > 0):
                        _ref_var_ = _ref_var_res_[0]
                    print(" INFO REF_VAR --------> " + _ref_var_)
                    _logs_ = info.split('|')
                    for log in _logs_:
                        print('LOG---> ' + log)
                        if (len(log) == 1):
                            print('LOG ONE_VAR --------------> ' + log)
                            _one_len_list_.append(log)
                        if (len(log) == 2):
                            if('en' in log or 'pt' in log):
                                print('LOG _LANGUAGEEWEEEEE_ --------------> ' + log)
                                _language_ = log
                        if (len(log) == 10):
                            try:
                                if (int(log) > 1000):
                                    _tstamp_var_ = log
                                    print('LOG _VAR_TSTAMP_ --------------> ' + log)
                            except:pass
                        if (len(log) == 32):
                            _checksum_var_ = log
                            print('LOG _VAR_CHECKSUM_ --------------> ' + log)
                        if (len(log) > 11 and len(log) < 30):
                            print('LOG _VAR_TOKEN_ --------------> ' + log)
                            _token_var_ = log
                        if ('delivery' in log):
                            _delivery_var_ = log
                            print('LOG _VAR_DELIVERY_ --------------> ' + log)
                        if (_ref_var_ and  _tstamp_var_ and _language_):
                            print("POssible Link_SUBS -----> " +  "https://s-" + _delivery_var_ + ".mxdcontent.net/subs/" + _ref_var_ + "_" + _language_ + ".vtt?t" + _tstamp_var_)
                            _tmp_ = "https://s-" + _delivery_var_ + ".mxdcontent.net/subs/" + _ref_var_ + "_" + _language_ + ".vtt?t" + _tstamp_var_
                            r = makeRequest(_tmp_, timeout=5)
                            if (r):
                                print("Subtitles size -------------> " + str(len(r)))
                                return r
        return None









if __name__ == '__main__':
    router(PARAMS)
xbmcplugin.endOfDirectory(int(sys.argv[1]))