import urlresolver, html5lib, ctypes, datetime, math, os, re, re, string, sys, urllib, urllib2, xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs, base64, uuid, jsunpack
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from html5lib import sanitizer
from html5lib import treebuilders
from bs4 import BeautifulSoup

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

addon = Addon('plugin.video.malabartalkies', sys.argv)
net = Net()
logo = os.path.join(addon.get_path(), 'icon.png')

currPage = 0
paginationText = ''
mode = addon.queries['mode']
play = addon.queries.get('play', None)
RootDir = addon.get_path()
dlg = xbmcgui.DialogProgress()

cwd = addon.get_path()
img_path = cwd + '/resources/img'
print "gbzygil " + img_path

if not xbmcvfs.exists(RootDir + '/thumbs'):
    xbmcvfs.mkdirs(RootDir + '/thumbs')

class youkuDecoder:
    def __init__(self):
        return

    def getFileIDMixString(self, seed):
        mixed = []
        source = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/\:._-1234567890")
        seed = float(seed)
        for i in range(len(source)):
            seed = (seed * 211 + 30031) % 65536
            index = math.floor(seed / 65536 * len(source))
            mixed.append(source[int(index)])
            source.remove(source[int(index)])
        return mixed

    def getFileId(self, fileId, seed):
        mixed = self.getFileIDMixString(seed)
        ids = fileId.split('*')
        realId = []
        for i in range(0, len(ids) - 1):
            realId.append(mixed[int(ids[i])])
        return ''.join(realId)

def selResolution(streamtypes):
    ratelist = []
    for i in range(0, len(streamtypes)):
        if streamtypes[i] == 'flv': ratelist.append([3, 'flv', i])
        if streamtypes[i] == 'mp4': ratelist.append([2, 'mp4', i])
        if streamtypes[i] == 'hd2': ratelist.append([1, 'hd2', i])
#     ratelist.sort()
#     if len(ratelist) > 1:
#         sel = 0
#         while sel < len(ratelist) - 1 and resolution > ratelist[sel][0]: sel += 1
#     else:
        sel = 0
    return streamtypes[ratelist[sel][2]], ratelist[sel][1]

def GbcYoukuResolver(media_id):
    url = 'http://v.youku.com/player/getPlayList/VideoIDS/%s' % (media_id)
    link = GetHttpData(url)
    json_response = simplejson.loads(link)
    print "GBC JSON response = " + str(json_response)
    name = "gbc"
    try:
        typeid, typename = selResolution(json_response['data'][0]['streamtypes'])
        print "GBC JSON response =typeid, typename  " + typeid + ',' + typename

        if typeid:
          seed = json_response['data'][0]['seed']
          fileId = json_response['data'][0]['streamfileids'][typeid].encode('utf-8')
          fileId = youkuDecoder().getFileId(fileId, seed)
          if typeid == 'mp4':
              type = 'mp4'
          else:
              type = 'flv'
          urls = []
          for i in range(len(json_response['data'][0]['segs'][typeid])):
              no = '%02X' % i
              k = json_response['data'][0]['segs'][typeid][i]['k'].encode('utf-8')
              urls.append('http://f.youku.com/player/getFlvPath/sid/00_00/st/%s/fileid/%s%s%s?K=%s' % (type, fileId[:8], no, fileId[10:], k))
              print "GBC append URL =" + 'http://f.youku.com/player/getFlvPath/sid/00_00/st/%s/fileid/%s%s%s?K=%s' % (type, fileId[:8], no, fileId[10:], k)

          stackurl = 'stack://' + ' , '.join(urls)
          name = '%s[%s]' % (name, typename)
          print "GbcYoukuResolver returning medial url = " + stackurl + " for media id=" + media_id
          return stackurl
#     except Exception:
#         dlg.close
#         buggalo.onExceptionRaised()
    except:
          print "GbcYoukuResolver : Error in parsing Youku jSon"

def GbcLoboVideoResolver(media_id):
    retval = ''
    url = 'http://lobovideo.com/' + media_id
    print "GbcLoboVideoResolver extracting media url from = " + url
#     net = Net()
    link = net.http_GET(url).content
    soup = BeautifulSoup(link)
    for eachItem in soup.findAll("div", { "id":"player_code" }):
        html = str(eachItem)
        r = re.findall("text/javascript'>\n.+?(eval\(function\(p,a,c,k,e,d\).+?).+?</script>", html, re.I | re.M)
        unpacked = jsunpack.unpack(html)
        txt = unpacked
        txt = txt.replace('\n', ' ').replace('\r', '')
        print "GbcLoboVideoResolver jsunpacked = " + txt
        r = re.findall(r"file\',\'(.+?)\'", txt)
        retval = r[0]
        print "GbcLoboVideoResolver returning medial url = " + retval + " for media id=" + media_id
    return retval

def GetHttpData(url):
    UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    req = urllib2.Request(url)
    req.add_header('User-Agent', UserAgent)
    try:
        response = urllib2.urlopen(req)
        httpdata = response.read()
        if response.headers.get('content-encoding', None) == 'gzip':
            httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
        charset = response.headers.getparam('charset')
        response.close()
    except:
        log("%s (%d) [%s]" % (
               sys.exc_info()[2].tb_frame.f_code.co_name,
               sys.exc_info()[2].tb_lineno,
               sys.exc_info()[1]
               ))
        return ''
    match = re.compile('<meta http-equiv=["]?[Cc]ontent-[Tt]ype["]? content="text/html;[\s]?charset=(.+?)"').findall(httpdata)
    if match:
        charset = match[0]
    else:
        match = re.compile('<meta charset="(.+?)"').findall(httpdata)
        if match:
            charset = match[0]
    if charset:
        charset = charset.lower()
        if (charset != 'utf-8') and (charset != 'utf8'):
            httpdata = httpdata.decode(charset, 'ignore').encode('utf8', 'ignore')
    return httpdata

if play:
    url = addon.queries.get('url', '')
    host = addon.queries.get('host', '')
    media_id = addon.queries.get('media_id', '')
#     addon.show_small_popup(host, url, 4000, logo)
    if host == 'youku':
#         addon.resolve_url(False)
        a = 1
    elif 'lobovideo' in url:
#         addon.resolve_url(False)
        a = 2
    else:
        stream_url = urlresolver.HostedMediaFile(url=url, host=host, media_id=media_id).resolve()
        addon.resolve_url(stream_url)

elif mode == 'resolver_settings':
    urlresolver.display_settings()

# elif mode == 'rajtamilMovies':
#     dlg.create("Malabar Talkies", "Fetching movies...")
#     dlg.update(0)
#
#     dlg.close()

elif mode == 'individualmovie_abcMal':
    url = addon.queries.get('url', False)
    movTitle = str(addon.queries.get('title', False))
    fanarturl = str(addon.queries.get('fanarturl', False))
    print 'gbc current movie url : ' + url
    print 'gbc current movie fanarturl : ' + fanarturl
    print 'gbc current movie title : ' + movTitle
    link = net.http_GET(url).content
    soup = BeautifulSoup(link)
    sources = []

    linksDiv = soup.find("div", { "class":"itemFullText" })

    # most pages have a trailer embebbed. Lets include that too
    for linksSection in linksDiv.findAll("div", { "class":"avPlayerWrapper avVideo" }):
        vidurl = str(linksSection.find('iframe')['src'])
        hosted_media = urlresolver.HostedMediaFile(vidurl)
        print 'gbc ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
        if urlresolver.HostedMediaFile(vidurl).valid_url():
            sources.append(hosted_media)
        else:
            print '    not resolvable by urlresolver!'


    links = linksDiv.find_all('a')
    for link in links:
        vidurl = link.get('href').strip()
        if 'm2pub' not in vidurl:
            hosted_media = urlresolver.HostedMediaFile(vidurl)
            print 'gbc ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
            if urlresolver.HostedMediaFile(vidurl).valid_url():
                if "nowvideo" in str(hosted_media):
                    (head, tail) = os.path.split(vidurl)
        #                 Now lets remove 'embed.php?v=' to extract the mediaID
                    tail = str(tail).replace('embed.php?v=', '')
                    print 'gbc ' + movTitle + ' NOWVIDEO source found ,head =' + head + ', tail=' + tail
                    sources.append(urlresolver.HostedMediaFile(host='nowvideo.sx', media_id=tail))
                else:
                    sources.append(hosted_media)
            else:
                print '    not resolvable by urlresolver!'


    sources = urlresolver.filter_source_list(sources)

    for s in sources:
        print "gbzygil : host is " + s.get_host() + ', mediaID=' + s.get_media_id()
        addon.add_video_item({'host': s.get_host() , 'media_id': s.get_media_id()}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)

elif mode == 'individualmovie_rajtamil':
    url = addon.queries.get('url', False)
    movTitle = str(addon.queries.get('title', False))
    fanarturl = str(addon.queries.get('fanarturl', False))
    print 'gbc current movie url : ' + url
    print 'gbc current movie fanarturl : ' + fanarturl
    print 'gbc current movie title : ' + movTitle
    link = net.http_GET(url).content

    soup = BeautifulSoup(link)
    sources = []

    links = soup.find_all('iframe')
    for link in links:
        movLink = str(link.get("src"))
        if "facebook" not in movLink:
            print 'gbc ' + movTitle + ' source found : ' + movLink
            hosted_media = urlresolver.HostedMediaFile(movLink)
            print 'gbc ' + movTitle + ' hosted_media : ' + str(hosted_media)
            if "nowvideo" in str(hosted_media):
                (head, tail) = os.path.split(movLink)
#                 Now lets remove 'embed.php?v=' to extract the mediaID
                tail = str(tail).replace('embed.php?v=', '')
                print 'gbc ' + movTitle + ' NOWVIDEO source found ,head =' + head + ', tail=' + tail
                sources.append(urlresolver.HostedMediaFile(host='nowvideo.sx', media_id=tail))

            else:
                sources.append(hosted_media)
    sources = urlresolver.filter_source_list(sources)
    for s in sources:
        print "gbzygil : host is " + s.get_host() + ', mediaID=' + s.get_media_id() + ', adding new item'

        addon.add_video_item({'host': s.get_host() , 'media_id': s.get_media_id()}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)

elif mode == 'GetMovies':
    dlg = xbmcgui.DialogProgress()
    dlg.create("Malabar Talkies", "Fetching movies...")
    dlg.update(0)
    subUrl = addon.queries.get('subUrl', False)

    # When someone selects ABC Malayalam
    if 'ABCMalayalam' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 0

        base_url = 'http://abcmalayalam.com'
        abcmalUrl = ''
        if subUrl == 'ABCMalayalam-Mal':
            abcmalUrl = base_url + '/movies?start=' + str(currPage)
        elif subUrl == 'ABCMalayalam-NonMal':
            abcmalUrl = base_url + '/non-malayalam?start=' + str(currPage)
        elif subUrl == 'ABCMalayalam-shortFilm':
            abcmalUrl = base_url + '/short-film?start=' + str(currPage)
        elif subUrl == 'ABCMalayalam-sizzling':
            abcmalUrl = base_url + '/sizzling?start=' + str(currPage)
        elif subUrl == 'ABCMalayalam-Comedy':
            abcmalUrl = base_url + '/Comedy?start=' + str(currPage)

        print "gbzygil going to open : " + abcmalUrl
        link = net.http_GET(abcmalUrl).content
        # soup = BeautifulSoup(link, 'html5lib')
        soup = BeautifulSoup(link)

        for linksSection in soup.findAll("div", { "class":"itemContainer" }):
            anchors = linksSection.findAll('a')
            print '*****************'
            anchorCnt = 0
            movUrl = base_url + anchors[0]['href']
            movName = str(anchors[0].text).strip()
            imglinks = linksSection.find_all('img')
            for imglink in imglinks:
                movThumb = imglink.get('src').strip()
                movThumb = base_url + movThumb
            # print movName + ',' + movUrl + ',' + movThumb
            names = movName
            fullLink = movUrl
    #         if movThumb:
            try :
                imgfullLink = movThumb
            except:
                print "no thumb"
                imgfullLink = ''

            addon.add_directory({'mode': 'individualmovie_abcMal', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink)

        for Paginator in soup.findAll("div", { "class":"k2Pagination" }):
            try:
                Paginator.ul.decompose()
                paginationText = 'Next Page.. ( Currently in ' + str(Paginator.text).strip() + ' )'
                if subUrl == 'ABCMalayalam-Mal':
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Mal', 'currPage': int(currPage) + 21 }, {'title': paginationText})
                elif subUrl == 'ABCMalayalam-NonMal':
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-NonMal', 'currPage': int(currPage) + 21 }, {'title': paginationText})
                elif subUrl == 'ABCMalayalam-shortFilm':
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-shortFilm', 'currPage': int(currPage) + 21 }, {'title': paginationText})
                elif subUrl == 'ABCMalayalam-sizzling':
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-sizzling', 'currPage': int(currPage) + 21 }, {'title': paginationText})
                elif subUrl == 'ABCMalayalam-Comedy':
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Comedy', 'currPage': int(currPage) + 21 }, {'title': paginationText})

            except:
                print "gbc : no pagination code found"

    elif 'olangalMovies-Recent' in subUrl:
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 0
            olangalurl = 'http://olangal.com/?start=' + str(currPage)
            print "gbc current url = " + olangalurl
            link = net.http_GET(olangalurl).content
            soup = BeautifulSoup(link, 'html5lib')

        # URL that generated this code:
        # http://txt2re.com/index-python.php3?s=Page%201%20of%20102&-1&-9&7&10&-5&11&3
            txt = link
            re1 = '(Page)'  # Word 1
            re2 = '( )'  # White Space 1
            re3 = '(\\d+)'  # Integer Number 1
            re4 = '(\\s+)'  # White Space 2
            re5 = '(of)'  # Word 2
            re6 = '(\\s+)'  # White Space 3
            re7 = '(\\d+)'  # Integer Number 2

            rg = re.compile(re1 + re2 + re3 + re4 + re5 + re6 + re7, re.IGNORECASE | re.DOTALL)
            m = rg.search(txt)
            if m:
                word1 = m.group(1)
                ws1 = m.group(2)
                int1 = m.group(3)
                ws2 = m.group(4)
                word2 = m.group(5)
                ws3 = m.group(6)
                int2 = m.group(7)
                paginationText = "( Currently in Page " + int1 + " of " + int2 + ")\n"

            for eachItem in soup.findAll("div", { "class":"item" }):
                 eachItem.ul.decompose()

                 imglinks = eachItem.find_all('img')
                 for imglink in imglinks:
                      imgfullLink = imglink.get('src').strip()
                      if imgfullLink.startswith("/"):
                       imgfullLink = 'http://olangal.com' + imgfullLink

                 links = eachItem.find_all('a')
                 for link in links:
                      names = link.contents[0].strip()
                      movUrl = link.get('href').strip()
                      fullLink = olangalurl + movUrl
                      if not "Read more" in names:
                        contextMenuItems = []

                        contextMenuItems.append(('Add to Favorites', 'XBMC.RunPlugin(%s?mode=200&name=%s&url=%s&fanarturl=%s)' % (sys.argv[0], names, fullLink, imgfullLink)))
                        addon.add_directory({'mode': 'individualmovie', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink, contextmenu_items=contextMenuItems, context_replace=True)
                        print 'gbc adding movie =' + names + ' ,url =' + fullLink + ' ,fanart = ' + imgfullLink
#             addon.add_directory({'mode': 'olangalMovies', 'currPage': int(currPage) + 24 }, {'title': 'Next Page.. ' + paginationText})
            addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent', 'currPage': int(currPage) + 24 }, {'title': 'Next Page.. ' + paginationText})


    elif 'rajtamilRecent' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        rajTamilurl = 'http://www.rajtamil.com/category/movies/page/' + str(currPage) + '/'
        link = net.http_GET(rajTamilurl).content
        soup = BeautifulSoup(link)
        # print soup.prettify()
        for eachItem in soup.findAll('li'):
            for coveritem in eachItem.findAll("div", { "class":"cover" }):
                links = coveritem.find_all('a')
                for link in links:
                    movTitle = str(link['title'])
                    movTitle = movTitle.replace('-', '')
                    movTitle = movTitle.replace('Watch', '')
                    movTitle = movTitle.replace('DVD', '')
                    movTitle = movTitle.replace('Movie', '')
                    movTitle = movTitle.replace('Online', '')
                    movTitle = movTitle.replace('Tamil Dubbed', 'Tamil Dubbed*')
                    movTitle = movTitle.strip()
                    movPage = str(link['href'])
                imgSrc = coveritem.find('img')['src']

                contextMenuItems = []

                contextMenuItems.append(('Add to Favorites', 'XBMC.RunPlugin(%s?mode=200&name=%s&url=%s&fanarturl=%s)' % (sys.argv[0], movTitle, movPage, imgSrc)))
                addon.add_directory({'mode': 'individualmovie_rajtamil', 'url': movPage, 'fanarturl': imgSrc , 'title': movTitle}, {'title': movTitle}, img=imgSrc, is_folder=True, contextmenu_items=contextMenuItems, context_replace=True)
                print 'gbc adding movie =' + movTitle + ' ,url =' + movPage + ' ,fanart = ' + imgSrc
        for Paginator in soup.findAll("div", { "class":"navigation" }):
            currPage = Paginator.find("span", { "class":"page-numbers current" })
            CurrentPage = str(currPage.contents[0].strip())

            for eachPage in Paginator.findAll("a", { "class":"page-numbers" }):
                if "Next" not in eachPage.contents[0]:
                    lastPage = eachPage.contents[0].strip()
        paginationText = "( Currently in Page " + CurrentPage + " of " + lastPage + ")\n"


        addon.add_directory({'mode': 'rajtamilMovies', 'currPage': int(CurrentPage) + 1 }, {'title': 'Next Page.. ' + paginationText})


    dlg.close()

elif mode == '200':
    with open(RootDir + "/favs.dat", 'a') as target:
        target.write(str(addon.queries.get('name', False)) + ',' + str(addon.queries.get('url', False)) + ',' + str(addon.queries.get('fanarturl', False)) + '\r\n')
    addon.show_small_popup('MalabarTalkies', str(addon.queries.get('name', False)) + ' added to favs', 4000, logo)

elif mode == 'ViewFavorites':
    try:
        for line in open(RootDir + "/favs.dat", 'r').readlines():
            names, fullLink, imgfullLink = line.split(",")
            if "rajtamil" in fullLink:
                addon.add_directory({'mode': 'individualmovie_rajtamil', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink)
            else:
                addon.add_directory({'mode': 'individualmovie', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink)
            print 'gbc adding movie =' + names + ' ,url =' + fullLink + ' ,fanart = ' + imgfullLink
    except IOError:
       addon.show_small_popup('MalabarTalkies', 'No favs yet..', 4000, logo)


elif mode == 'individualmovie':
#     dlg = xbmcgui.DialogProgress()
#     dlg.create( "Malabar Talkies", "Fetching movie sources..." )
#     dlg.update( 0 )

    url = addon.queries.get('url', False)
    movTitle = str(addon.queries.get('title', False))
    (head, tail) = os.path.split(url)
    url = 'http://olangal.com/movies/watch-malayalam-movies-online/' + tail
    fanarturl = str(addon.queries.get('fanarturl', False))
    print 'gbc current movie url : ' + url
    print 'gbc current movie fanarturl : ' + fanarturl
    print 'gbc current movie title : ' + movTitle
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    soup = BeautifulSoup(link)
    allVidSrcs = soup.findAll('a', target="_blank")

    currIdx = 0
    for vidLink in allVidSrcs:
     currIdx = currIdx + 1
#      dlg.update(int((currIdx * 100.0) / len(allVidSrcs)))
     if 'watchmoviesindia.com' not in str(vidLink) and 'tamizh.ws' not in str(vidLink) and 'malayalam_calendar.php' not in str(vidLink) :
         mediaLink = ''
         mediaHost = ''
         media_id = ''
         if 'vidto.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'vidto.me'
              print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
              addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})

         elif 'lobovideo.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'lobovideo.com'
              mediaUrl = GbcLoboVideoResolver(media_id)
              print 'gbc From vidLink = ' + str(mediaUrl) + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost

              li = xbmcgui.ListItem(movTitle + "," + mediaHost + ' (' + media_id + ')')
              li.setProperty('IsPlayable', 'true')
              xbmcplugin.addDirectoryItem(int(sys.argv[1]), mediaUrl, li)

         elif 'nowvideo.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'nowvideo.com'
              print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
              addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})

         elif 'youku.php' in str(vidLink):
              youKuswf = 'http://static.youku.com/v1.0.0389/v/swf/loader.swf?VideoIDS='
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'youku.com'
              mediaUrl = GbcYoukuResolver(media_id)
              if mediaUrl:
                  print 'gbc From vidLink = ' + mediaUrl + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost + ', movTitle=' + movTitle
                  li = xbmcgui.ListItem(movTitle + "," + mediaHost + ' (' + media_id + ')')
                  li.setProperty('IsPlayable', 'true')
                  xbmcplugin.addDirectoryItem(int(sys.argv[1]), mediaUrl, li)

         elif 'putlocker.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'putlocker'
              print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
              addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
         elif 'youtubelinks.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'youtube.com'
              print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
              addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
         elif 'veoh.php' in str(vidLink):
              (head, tail) = os.path.split(vidLink['href'])
              media_idArr = tail.split('=')
              media_id = media_idArr[1]
              mediaHost = 'veoh'
              print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
              addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
         else:
              print 'gbc other source :' + str(vidLink)
#     dlg.close

elif mode == 'GetSearchQuery':
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search Movies')
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_text = keyboard.getText()
#         dlg = xbmcgui.DialogProgress()
        dlg.create("Malabar Talkies", "Searching for " + search_text + "..")
        dlg.update(0)
        searchurl = 'http://olangal.com/component/search/?searchword=' + str(search_text) + '&searchphrase=all'
        req = urllib2.Request(searchurl)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        Searchsoup = BeautifulSoup(link, 'html5lib')
        for eachItem in Searchsoup.findAll("dt", { "class":"result-title" }):
            searchResNumber = eachItem.contents[0].strip()
            links = eachItem.find_all('a')
            for link in links:
                name = link.contents[0].strip()
                fullLink = 'http://olangal.com' + link.get('href').strip()
                print searchResNumber + ' ' + name + ' ' + fullLink
                addon.add_directory({'mode': 'individualmovie', 'url': fullLink, 'title': str(name)}, {'title': str(searchResNumber) + ' ' + str(name)})
        dlg.close

elif mode == 'olangalMalayalam':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent'}, {'title': 'Recent Movies'}, img=img_path + '/recent.PNG')

    addon.add_directory({'mode': 'GetSearchQuery'}, {'title': 'Search'}, img=img_path + '/search.PNG')
elif mode == 'abcmalayalam':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Mal'}, {'title': 'Malayalam Movies'}, img=img_path + '/malayalam.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-NonMal'}, {'title': 'Non-Malayalam Movies'}, img=img_path + '/nonmalayalam.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-shortFilm'}, {'title': 'Short Films'}, img=img_path + '/shortfilms.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-sizzling'}, {'title': 'Sizzling(18+)'}, img=img_path + '/18plus.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Comedy'}, {'title': 'Comedy'}, img=img_path + '/comedy.PNG')
elif mode == 'rajTamil':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilRecent'}, {'title': 'Recent Movies'}, img=img_path + '/rajTamil.PNG')

elif mode == 'main':
    addon.add_directory({'mode': 'olangalMalayalam'}, {'title': 'Malayalam : olangal.com'}, img=img_path + '/olangal.PNG')
    addon.add_directory({'mode': 'abcmalayalam'}, {'title': 'Malayalam : abcmalayalam.com'}, img=img_path + '/abcMal.PNG')
    addon.add_directory({'mode': 'rajTamil'}, {'title': 'Tamil : rajtamil.com'}, img=img_path + '/rajTamil.PNG')
    addon.add_directory({'mode': 'ViewFavorites'}, {'title': 'Favorites'}, img=img_path + '/favorites.PNG')
if not play:
    addon.end_of_directory()
