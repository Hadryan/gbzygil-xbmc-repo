import urlresolver, os, re, sys, urllib2, xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from bs4 import BeautifulSoup
import resolvers
#    return resolvers.resolve_url(url, filename)

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

addon = Addon('plugin.video.malabartalkies', sys.argv)
SETTINGS_CACHE_TIMEOUT = addon.get_setting('Cache-Timeout')
#SETTINGS_CACHE_TIMEOUT = 60
SETTINGS_ENABLEADULT = addon.get_setting('EnableAdult')
cache = StorageServer.StorageServer("malabartalkies", SETTINGS_CACHE_TIMEOUT)
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

if not xbmcvfs.exists(RootDir + '/thumbs'):
    xbmcvfs.mkdirs(RootDir + '/thumbs')

def GetHttpData(url):
#     log("%s::url - %s" % (sys._getframe().f_code.co_name, url))
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')

    try:
        response = urllib2.urlopen(req)
        httpdata = response.read()
        if response.headers.get('content-encoding', None) == 'gzip':
            httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
        charset = response.headers.getparam('charset')
        response.close()
    except:
#         log("%s (%d) [%s]" % (
#                sys.exc_info()[2].tb_frame.f_code.co_name,
#                sys.exc_info()[2].tb_lineno,
#                sys.exc_info()[1]
#                ))
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

class youkuDecoder:
    import math
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
    if sys.version_info < (2, 7):
        import simplejson
    else:
        import json as simplejson

    url = 'http://v.youku.com/player/getPlayList/VideoIDS/%s' % (media_id)
    link = GetHttpData(url)
    json_response = simplejson.loads(link)

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

def dump(obj, nested_level=0, output=sys.stdout):
    spacing = '   '
    if type(obj) == dict:
        print >> output, '%s{' % ((nested_level) * spacing)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print >> output, '%s%s:' % ((nested_level + 1) * spacing, k.encode('utf8'))
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k.encode('utf8'), v.encode('utf8'))
        print >> output, '%s}' % (nested_level * spacing)
    elif type(obj) == list:
        print >> output, '%s[' % ((nested_level) * spacing)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s' % ((nested_level + 1) * spacing, v.encode('utf8'))
        print >> output, '%s]' % ((nested_level) * spacing)
    else:
        print >> output, '%s%s' % (nested_level * spacing, obj)

def GbcLoboVideoResolver(media_id):
    import jsunpack
    retval = ''
    url = 'http://lobovideo.com/' + media_id
    print "GbcLoboVideoResolver extracting media url from = " + url
#     net = Net()
    link = net.http_GET(url).content
    soup = BeautifulSoup(link)
    for eachItem in soup.findAll("div", { "id":"player_code"}):
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

def getMovList_thiruttuvcd(thiruttuvcd_url):
        print "================GBZYGIL checking cache hit : function getMovList_thiruttuvcd was called"
        Dict_movlist = {}

        if 'thiruttumasala' in thiruttuvcd_url:
            req = urllib2.Request(thiruttuvcd_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            base_url = 'http://www.thiruttumasala.com'
            soup = BeautifulSoup(link)
            for eachItem in soup.findAll("div", { "class":"video_box" }):
                links = eachItem.find_all('a')
                for link in links:
                    if link.has_attr('href'):
                        link = link.get('href')
                img = eachItem.find('img')['src']
                movTitle = eachItem.find('img')['alt']
                Dict_movlist.update({movTitle:'mode=individualmovie, url=' + base_url + link + ', imgLink=' + base_url + img})
            try:
                CurrPage = soup.find("span", { "class":"currentpage" })
                print "<<<<<<<<<<<<< gbzygil found pagination " + CurrPage.text
                paginationText = "( Currently in Page " + CurrPage.text + ")\n"
                Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(CurrPage.text) + 1) + ',title=Next Page.. ' + paginationText})
            except:
                print "No next page"
#         elif 'hindi-movies-online' in thiruttuvcd_url:
#             a = 1
#         elif 'http://www.thiruttuvcd.me/category/telugu/' in thiruttuvcd_url:
#             a = 1
        else:
            url = thiruttuvcd_url
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            # base_url='http://www.thiruttuvcd.me'
            soup = BeautifulSoup(link)
            # print soup.prettify()

            for eachItem in soup.findAll("div", { "class":"postbox" }):
                links = eachItem.find_all('a')
                for link in links:
                    if link.has_attr('href'):
                        link = link.get('href')
                img = eachItem.find('img')['src']
                movTitle = eachItem.find('img')['alt']
                movTitle = re.sub('Tamil', '', movTitle)
                movTitle = re.sub('Movie', '', movTitle)
                movTitle = re.sub('Watch', '', movTitle)
                movTitle = re.sub('Online', '', movTitle)

                #print 'BLAAAAAAAA' + movTitle + ',' + link + "," + img
                if ('MP3' not in movTitle) & ('Songs' not in movTitle):
                    Dict_movlist.update({movTitle:'mode=individualmovie, url=' + link + ', imgLink=' + img})
#             try:
            CurrPage = soup.find("span", { "class":"pages" })
            print "<<<<<<<<<<<<< gbzygil found pagination " + CurrPage.text
            txt = CurrPage.text
            re1 = '.*?'  # Non-greedy match on filler
            re2 = '(\\d+)'  # Integer Number 1
            rg = re.compile(re1 + re2, re.IGNORECASE | re.DOTALL)
            m = rg.search(txt)
            if m:
                int1 = m.group(1)
                CurrPage1 = int1
                print "(" + int1 + ")" + "\n"
                paginationText = "( Currently in " + txt + ")\n"
                if 'hindi-movies-online' in thiruttuvcd_url:
                    Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=thiruttuvcd_hindiMovs, currPage=' + str(int(CurrPage1) + 1) + ',title=Next Page.. ' + paginationText})
                elif 'telugu-movies'  in thiruttuvcd_url:
                    Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=thiruttuvcd_teluguMovs, currPage=' + str(int(CurrPage1) + 1) + ',title=Next Page.. ' + paginationText})
                else:
                    Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=thiruttuvcd_tamilMovs, currPage=' + str(int(CurrPage1) + 1) + ',title=Next Page.. ' + paginationText})

#             except:
#                 print "No next page"


        return Dict_movlist

def getMovList_rajtamil(rajTamilurl):
        print "================GBZYGIL checking cache hit : function getMovList_rajtamil was called"

        Dict_movlist = {}
        link = net.http_GET(rajTamilurl).content
        soup = BeautifulSoup(link)
        # print soup.prettify()
        for eachItem in soup.findAll('li'):
            for coveritem in eachItem.findAll("div", { "class":"cover"}):
                links = coveritem.find_all('a')
                for link in links:
                    # movTitle = str(link['title'])
                    movTitle = link['title']
                    movTitle = movTitle.replace('-', '')
                    movTitle = movTitle.replace('Watch', '')
                    movTitle = movTitle.replace('DVD', '')
                    movTitle = movTitle.replace('Movie', '')
                    movTitle = movTitle.replace('Online', '')
                    movTitle = movTitle.replace('Tamil Dubbed', 'Tamil Dubbed*')
                    movTitle = movTitle.strip()
                    # movPage = str(link['href'])
                    movPage = link['href']
                try:
                    imgSrc = coveritem.find('img')['src']
                except:
                    imgSrc = ''

                contextMenuItems = []

                contextMenuItems.append(('Add to Favorites', 'XBMC.RunPlugin(%s?mode=200&name=%s&url=%s&fanarturl=%s)' % (sys.argv[0], movTitle, movPage, imgSrc)))
#                 addon.add_directory({'mode': 'individualmovie_rajtamil', 'url': movPage, 'fanarturl': imgSrc , 'title': movTitle}, {'title': movTitle}, img=imgSrc, is_folder=True, contextmenu_items=contextMenuItems, context_replace=True)

                Dict_movlist.update({movTitle:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc})

#                 print 'gbc adding movie =' + movTitle + ' ,url =' + movPage + ' ,fanart = ' + imgSrc

        for Paginator in soup.findAll("div", { "class":"navigation"}):
            currPage = Paginator.find("span", { "class":"page-numbers current"})
            CurrentPage = str(currPage.contents[0].strip())

            for eachPage in Paginator.findAll("a", { "class":"page-numbers"}):
                if "Next" not in eachPage.contents[0]:
                    lastPage = eachPage.contents[0].strip()
        paginationText = "( Currently in Page " + CurrentPage + " of " + lastPage + ")\n"

        if 'vijay-tv-shows' in rajTamilurl:
            subUrl = 'rajtamilTVshowsVijayTV'
        elif 'sun-tv-show' in rajTamilurl:
            subUrl = 'rajtamilTVshowsSunTV'
        elif 'zee-tamil-tv-show' in rajTamilurl:
            subUrl = 'rajtamilTVshowsZeeTamil'
        elif 'polimer-tv-show-2' in rajTamilurl:
            subUrl = 'rajtamilTVshowsPolimer'
        else:
            subUrl = 'rajtamilRecent'

#         addon.add_directory({'mode': 'rajtamilMovies', 'currPage': int(CurrentPage) + 1 }, {'title': 'GBCNext Page.. ' + paginationText})
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(CurrentPage) + 1) + ',title=Next Page.. ' + paginationText})
        return Dict_movlist

def getMovList_olangal(olangalurl):
            print "================GBZYGIL checking cache hit : function getMovList_olangal was called"
            Dict_movlist = {}
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

            for eachItem in soup.findAll("div", { "class":"item"}):
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

#                         contextMenuItems.append(('Add to Favorites', 'XBMC.RunPlugin(%s?mode=200&name=%s&url=%s&fanarturl=%s)' % (sys.argv[0], names, fullLink, imgfullLink)))
#                         addon.add_directory({'mode': 'individualmovie', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink, contextmenu_items=contextMenuItems, context_replace=True)
                        Dict_movlist.update({names:'mode=individualmovie, url=' + fullLink + ', imgLink=' + imgfullLink.strip()})

#                         print 'gbc adding movie =' + names + ' ,url =' + fullLink + ' ,fanart = ' + imgfullLink
#             addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent', 'currPage': int(currPage) + 24 }, {'title': 'Next Page.. ' + paginationText})
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=olangalMovies-Recent, currPage=' + str(int(currPage) + 24) + ',title=Next Page.. ' + paginationText})
            return Dict_movlist

def getMovList_ABCmal(abcmalUrl):
        print "================GBZYGIL checking cache hit : function getMovList_ABCmal was called"
        Dict_movlist = {}

        link = net.http_GET(abcmalUrl).content
        soup = BeautifulSoup(link)

        for linksSection in soup.findAll("div", { "class":"itemContainer"}):
            anchors = linksSection.findAll('a')
            anchorCnt = 0
            movUrl = base_url + anchors[0]['href']
            movName = str(anchors[0].text).strip()
            imglinks = linksSection.find_all('img')
            for imglink in imglinks:
                movThumb = imglink.get('src').strip()
                movThumb = base_url + movThumb
            names = movName
            fullLink = movUrl
            try :
                imgfullLink = movThumb
            except:
                print "no thumb"
                imgfullLink = ''
            Dict_movlist.update({names:'mode=individualmovie, fullLink=' + fullLink + ', imgLink=' + imgfullLink.strip()})

        for Paginator in soup.findAll("div", { "class":"k2Pagination"}):
            try:
                Paginator.ul.decompose()
                paginationText = 'Next Page.. ( Currently in ' + str(Paginator.text).strip() + ' )'
                Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(currPage) + 21) + ', title=' + paginationText})
            except:
                print "gbc : no pagination code found"
        return Dict_movlist

def getMovLinksForEachMov(url):

#     with open(RootDir + "/history.dat", 'a') as target:
#         target.write(str(addon.queries.get('title', False)) + ',' + str(addon.queries.get('url', False)) + ',' + str(addon.queries.get('fanarturl', False)) + '\r\n')

    url = addon.queries.get('url', False)
#     if url == False:
#         url = addon.queries.get('subUrl', False)

    if 'olangal.com' in url:
        movTitle = str(addon.queries.get('title', False))
        (head, tail) = os.path.split(url)
        url = 'http://olangal.com/movies/watch-malayalam-movies-online/' + tail
        fanarturl = str(addon.queries.get('fanarturl', False))
        print 'gbc current movie url : ' + url
        print 'gbc current movie fanarturl : ' + fanarturl
        print 'gbc current movie title : ' + movTitle

        link = net.http_GET(url).content
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
                  addon.add_video_item({'host': mediaHost, 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})

#                   Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaLink})
             elif 'lobovideo.php' in str(vidLink):
                  (head, tail) = os.path.split(vidLink['href'])
                  media_idArr = tail.split('=')
                  media_id = media_idArr[1]
                  mediaHost = 'lobovideo.com'
                  mediaUrl = GbcLoboVideoResolver(media_id)
                  if mediaUrl:
                      print 'gbc From vidLink = ' + str(mediaUrl) + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
                      li = xbmcgui.ListItem(movTitle + "," + mediaHost + ' (' + media_id + ')')
                      li.setProperty('IsPlayable', 'true')
                      xbmcplugin.addDirectoryItem(int(sys.argv[1]), mediaUrl, li)
#                       Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaUrl})
             elif 'nowvideo.php' in str(vidLink):
                  (head, tail) = os.path.split(vidLink['href'])
                  media_idArr = tail.split('=')
                  media_id = media_idArr[1]
                  mediaHost = 'nowvideo.com'
                  print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
                  addon.add_video_item({'host': mediaHost, 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
#                   Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaLink})
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
#                       Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaUrl})
             elif 'putlocker.php' in str(vidLink):
                  (head, tail) = os.path.split(vidLink['href'])
                  media_idArr = tail.split('=')
                  media_id = media_idArr[1]
                  mediaHost = 'putlocker'
                  print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
                  addon.add_video_item({'host': mediaHost, 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
#                   Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaLink})
             elif 'youtubelinks.php' in str(vidLink):
                  (head, tail) = os.path.split(vidLink['href'])
                  media_idArr = tail.split('=')
                  media_id = media_idArr[1]
                  mediaHost = 'youtube.com'
                  print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
                  addon.add_video_item({'host': mediaHost, 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
#                   Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaLink})
             elif 'veoh.php' in str(vidLink):
                  (head, tail) = os.path.split(vidLink['href'])
                  media_idArr = tail.split('=')
                  media_id = media_idArr[1]
                  mediaHost = 'veoh'
                  print 'gbc From vidLink = ' + vidLink['href'] + ', adding mediaid=' + media_id + ', mediaHost=' + mediaHost
                  addon.add_video_item({'host': mediaHost, 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + mediaHost + ' (' + media_id + ')'})
#                   Dict_movSources.update({movTitle:'host=' + mediaHost + ', media_id=' + media_id + ', mediaLink=' + mediaLink})
             else:
                  print 'gbc other source :' + str(vidLink)

    elif 'rajtamil.com' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('fanarturl', False))
            print 'gbc current movie url : ' + url
            print 'gbc current movie fanarturl : ' + fanarturl
            print 'gbc current movie title : ' + movTitle
            link = net.http_GET(url).content
#             print encode('utf-8')

            soup = BeautifulSoup(link)
#             print soup.prettify('utf-8')
            sources = []


            try:
                for eachItem in soup.findAll("div", { "class":"entry" }):
#                     print eachItem
                    links = eachItem.find_all('a')
                    for link in links:
                        if link.has_attr('href'):
                            link = link.get('href')
                            if 'youtube' in link:
                                (head, tail) = os.path.split(link)
                                tail = str(tail).replace('watch?v=', '')
                                print "Gbzygil : Adding using method1 " + tail
                                sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=tail))


            except:
                print "Gbzygil : no embedded youtube urls found using method1 "

            try:
                for eachItem in soup.findAll('p'):
                    for eachItem1 in eachItem.findAll('a'):
                        if eachItem1.has_attr('onclick'):
                            eI = eachItem1['onclick']
                            splitString = eI.split(",")
                            eI = splitString[0].replace("window.open('", "")
                            eI = eI.replace("'", "")
                            splitString = eI.split("=")
                            eI = splitString[2]
                            print eI
                            print "Gbzygil : Adding using method2 " + eI
                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(eI)))

            except:
                print "Gbzygil : no embedded youtube urls found using method2 "

            try:
                re1 = '(window\\.open)'  # Fully Qualified Domain Name 1
                re2 = '.*?'  # Non-greedy match on filler
                re3 = '((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'  # HTTP URL 1

                rg = re.compile(re1 + re2 + re3, re.IGNORECASE | re.DOTALL)
                m = rg.search(str(soup))
                if m:
                    fqdn1 = m.group(1)
                    httpurl1 = m.group(2)
                    # print httpurl1
                    splitString = httpurl1.split("'")
                    link = splitString[0]
                    if 'youtube' in link:
                        (head, tail) = os.path.split(link)
                        tail = str(tail).replace('watch?v=', '')
                        print "Gbzygil : Adding using method3 " + tail

                        sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))
            except:
                print "Gbzygil : no embedded youtube urls found using method3 "

            try:
                for eachItem in soup.findAll('param', {'name': 'movie'}):
                    if eachItem.has_attr('value'):
#                         print eachItem['value']
#                         print "Gbzygil : Adding using method3 " + eachItem['value']
#                         sources.append(urlresolver.HostedMediaFile(url=eachItem['value']))
#                         sources.append(urlresolver.HostedMediaFile(url='http://www.youtube.com/v/Y0iJdORpTPE'))
                        httpurl1 = eachItem['value']
                        splitString = httpurl1.split("??")
                        link = splitString[0]
                        if 'youtube' in link:
                            (head, tail) = os.path.split(link)
                            tail = str(tail).replace('watch?v=', '')
                            print "Gbzygil : Adding using method3 " + tail

                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))

            except:
                print "Gbzygil : no embedded youtube urls found using method4 "

            try:
                for eachItem in soup.findAll("a"):
                    if eachItem.has_attr('href'):
                        link=eachItem.get('href')
                        if 'youtube' in link:
                            (head, tail) = os.path.split(link)
                            tail = str(tail).replace('watch?v=', '')
                            print "Gbzygil : Adding using method5 " + tail

                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))

            except:
                print "Gbzygil : no embedded youtube urls found using method5 "

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
                        sources.append(urlresolver.HostedMediaFile(host='nowvideo.sx', media_id=str(tail)))

                    else:
                        sources.append(hosted_media)
            # sources = urlresolver.filter_source_list(sources)

            for idx, s in enumerate(sources):
                # Dict_movSources.update({movTitle + str(idx):'host=' + s.get_host() + ' , media_id=' + s.get_media_id() + ' , title=' + movTitle + ' , img=' + fanarturl.strip()})
                if s.get_host():
                    print "gbzygil : host is " + s.get_host() + ', mediaID=' + s.get_media_id() + ', adding new item'
                    addon.add_video_item({'host': s.get_host() , 'media_id': s.get_media_id(), 'title': movTitle, 'img':fanarturl, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)

    elif 'thiruttuvcd.me' in url:
            url = addon.queries.get('url', False)
            subUrl = addon.queries.get('subUrl', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            try:
                print 'gbc current movie url : ' + url
                print 'gbc current movie SubUrl : ' + subUrl
                print 'gbc current movie fanarturl : ' + fanarturl
                print 'gbc current movie title : ' + movTitle
            except:
                print 'weird'
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()

            soup = BeautifulSoup(link)
#             try:
            links = soup.find_all('iframe')
            for link in links:
                movLink = link.get("src")
                print movLink
                if 'nowvideo' in movLink:
                    mediaHost = 'nowvideo.com'
                    print 'movLink=' + movLink
                    splitString = movLink.split("=")
                    media_id = splitString[1]
                    print "media id =" + media_id
                    stream_url = urlresolver.HostedMediaFile(host=mediaHost, media_id=media_id).resolve()
                    if stream_url:
                        addon.add_video_item({'host':mediaHost , 'media_id': media_id, 'title': movTitle, 'AddtoHist':True}, {'title': mediaHost}, img=fanarturl)
#                         li.setProperty('title', movTitle)


#                         li = xbmcgui.ListItem(movTitle + ':nowvideo', iconImage=fanarturl)
#                         li.setProperty('IsPlayable', 'true')
#                         xbmcplugin.addDirectoryItem(int(sys.argv[1]), stream_url, li)
                elif 'vodlocker' in movLink:
                    req = urllib2.Request(movLink)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()
                    re1 = '.*?'  # Non-greedy match on filler
                    re2 = '(file)'  # Word 1
                    re3 = '.*?'  # Non-greedy match on filler
                    re4 = '((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'  # HTTP URL 1

                    rg = re.compile(re1 + re2 + re3 + re4, re.IGNORECASE | re.DOTALL)
                    m = rg.search(link)
                    if m:
                        word1 = m.group(1)
                        httpurl1 = m.group(2)
                        print 'found vodlocker:' + httpurl1
                        li = xbmcgui.ListItem(movTitle + ':vodlocker', iconImage=fanarturl)
                        li.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(int(sys.argv[1]), httpurl1, li)

#                     addon.add_video_item({'host': mediaHost, 'media_id': media_id}, {'title': mediaHost})


#             except:
#                 print 'nada'

#             try:
#                 for eachItem in soup.findAll('param', {'name': 'movie'}):
#                     if eachItem.has_attr('value'):
#                         # print eachItem['value']
#                         url1 = eachItem['value']
#                         if 'video.tt' in url1:
#                             print "found video.tt link :" + url1
#                             li = xbmcgui.ListItem(movTitle, iconImage=fanarturl)
#                             li.setProperty('IsPlayable', 'true')
#                             xbmcplugin.addDirectoryItem(int(sys.argv[1]), 'http://www.video.tt/f/XX86rqtwK.swf', li)
#             except:
#                 print 'nada'

    elif 'thiruttumasala' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            print 'gbc current movie url : ' + url
            print 'gbc current movie fanarturl : ' + fanarturl
            print 'gbc current movie title : ' + movTitle
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()

            soup = BeautifulSoup(link)
            # print soup.prettify()
            try:
                re1='.*?'	# Non-greedy match on filler
                re2='(var)'	# Word 1
                re3='(\\s+)'	# White Space 1
                re4='(cnf)'	# Word 2
                re5='(=)'	# Any Single Character 1
                re6='(.)'	# Any Single Character 2
                re7='(http)'	# Word 3
                re8='(:)'	# Any Single Character 3
                re9='(\\/)'	# Any Single Character 4
                re10='(\\/www\\.thiruttumasala\\.com\\/media\\/nuevo\\/config\\.php)'	# Unix Path 1
                re11='(.)'	# Any Single Character 5
                re12='(key)'	# Word 4
                re13='(=)'	# Any Single Character 6
                re14='(\\d+)'	# Integer Number 1

                rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12+re13+re14,re.IGNORECASE|re.DOTALL)
                m = rg.search(str(soup))
                if m:
                    word1=m.group(1)
                    ws1=m.group(2)
                    word2=m.group(3)
                    c1=m.group(4)
                    c2=m.group(5)
                    word3=m.group(6)
                    c3=m.group(7)
                    c4=m.group(8)
                    unixpath1=m.group(9)
                    c5=m.group(10)
                    word4=m.group(11)
                    c6=m.group(12)
                    int1=m.group(13)
                    link= word3+c3+c4+unixpath1+c5+word4+c6+int1
                    link=link.replace('config.php', 'playlist.php')
                    print 'BLAAA found link =' + link

                    req = urllib2.Request(link)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()

                    soup = BeautifulSoup(link)
                    print 'BLAAA found file =' + soup.find('file').text
                    print 'BLAAA found img =' + soup.find('thumb').text.strip()
    #                 addon.add_video_item({'url': soup.find('file').text}, {'title': movTitle }, img=soup.find('thumb').text)
                    li = xbmcgui.ListItem(movTitle, iconImage=soup.find('thumb').text.strip())
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(int(sys.argv[1]), soup.find('file').text, li)

            except:
                print "Nothing found with method 1"

            try:
                txt = soup.find('param', {'name':'flashvars'})['value']
                re1 = '.*?'  # Non-greedy match on filler
                re2 = '((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'  # HTTP URL 1

                rg = re.compile(re1 + re2, re.IGNORECASE | re.DOTALL)
                m = rg.search(txt)
                if m:
                    httpurl1 = m.group(1)
                    # print "("+httpurl1+")"+"\n"
                    httpurl1 = httpurl1.replace('config.php', 'playlist.php')
                    req = urllib2.Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                    response = urllib2.urlopen(httpurl1)
                    link = response.read()
                    response.close()

                    soup = BeautifulSoup(link)
                    print soup.find('file').text
                    print soup.find('thumb').text.strip()
    #                 addon.add_video_item({'url': soup.find('file').text}, {'title': movTitle }, img=soup.find('thumb').text)
                    li = xbmcgui.ListItem(movTitle, iconImage=soup.find('thumb').text.strip())
                    li.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(int(sys.argv[1]), soup.find('file').text, li)
            except:
                print "Nothing found using method 2"



    elif 'abcmalayalam.com' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            print 'gbc current movie url : ' + url
            print 'gbc current movie fanarturl : ' + fanarturl
            print 'gbc current movie title : ' + movTitle
            link = net.http_GET(url).content
            soup = BeautifulSoup(link)
            sources = []

            try:
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
            except:
                     print 'Nothing found using method 1!'

            try:
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
                            print vidurl + ' is NOT resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 2!'

            sources = urlresolver.filter_source_list(sources)

            for idx, s in enumerate(sources):
#                 Dict_movSources.update({movTitle + str(idx):'host=' + s.get_host() + ' , media_id=' + s.get_media_id() + ' , title=' + movTitle + ' , img=' + fanarturl.strip()})
                addon.add_video_item({'host': s.get_host() , 'media_id': s.get_media_id(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)

#     return Dict_movSources
    #     dlg.close

print"############# MAIN MENU ##################"
print 'MODE = ' + str(addon.queries.get('mode', False))
print 'TITLE = ' + str(addon.queries.get('title', False))
print 'URL = ' + str(addon.queries.get('url', False))
print 'SUBURL = ' + str(addon.queries.get('subUrl', False))
print 'CURRPAGE = ' + str(addon.queries.get('currPage', False))
print"########################################"

if play:
    print "********* Gonna add to history and start playing"
    print str(addon.queries)
    try:
        if "True" in addon.queries.get('AddtoHist', False):
            with open(RootDir + "/history.dat", 'a') as target:
                target.write("title=" + str(addon.queries.get('title', False)) + ', host=' + str(addon.queries.get('host', False)) + ', media_id=' + str(addon.queries.get('media_id', False)) + ', img=' + str(addon.queries.get('img', False)) + '\r\n')
    except:
        print "not adding to watch history"
    url = addon.queries.get('url', '')
    host = addon.queries.get('host', '')
    media_id = addon.queries.get('media_id', '')

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


elif mode == 'individualmovie':
    url = addon.queries.get('url', False)
    getMovLinksForEachMov(url)
#     print "@@@@@@@@@@@@@@ Dict of MovSources received :"
#     dump(ReceivedDict)

elif mode == 'GetMovies':
    dlg = xbmcgui.DialogProgress()
    dlg.create("Malabar Talkies", "Fetching movies and caching...\nWill be faster next time")
    dlg.update(0)
    mode = addon.queries.get('mode', False)
    base_url = 'http://abcmalayalam.com'
    subUrl = addon.queries.get('subUrl', False)
    if 'ABCMalayalam' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 0
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

        Dict_res = cache.cacheFunction(getMovList_ABCmal, abcmalUrl)
#         print "<<<<<GBZYGIL received DICT="
#         dump(Dict_res)
        for key, value in Dict_res.iteritems():
            if 'Paginator' not in key:
                SplitValues = value.split(",")
                for eachSplitVal in SplitValues:
                    if 'mode' in eachSplitVal:
                        mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                    elif 'fullLink' in eachSplitVal:
                        fullLink_Str = str(eachSplitVal.replace('fullLink=', '')).strip()
                    elif 'imgLink' in eachSplitVal:
                        IMGfullLink_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'url': fullLink_Str , 'title': key, 'img' :IMGfullLink_Str}, {'title': key}, img=IMGfullLink_Str)
#                 print "<<<GBC creating directory for " + key + "img=" + IMGfullLink_Str

        try:
            PaginatorVal = Dict_res['Paginator']
            if PaginatorVal:
                SplitValues = PaginatorVal.split(",")
                for eachSplitVal in SplitValues:
                    if 'mode' in eachSplitVal:
                        mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                    elif 'subUrl' in eachSplitVal:
                        subUrl_Str = str(eachSplitVal.replace('subUrl=', '')).strip()
                    elif 'currPage' in eachSplitVal:
                        currPage_Str = str(eachSplitVal.replace('currPage=', '')).strip()
                    elif 'title' in eachSplitVal:
                        title_Str = str(eachSplitVal.replace('title=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
                print "gbzygil : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
        except:
            print "No pagination found"

    elif 'olangalMovies-Recent' in subUrl:
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 0
            olangalurl = 'http://olangal.com/?start=' + str(currPage)
            Dict_res = cache.cacheFunction(getMovList_olangal, olangalurl)
            for key, value in Dict_res.iteritems():
                if 'Paginator' not in key:
                    SplitValues = value.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'url' in eachSplitVal:
                            fullLink_Str = str(eachSplitVal.replace('url=', '')).strip()
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                    addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': key}, {'title': key}, img=fanarturl_Str)
            try:
                PaginatorVal = Dict_res['Paginator']
                if PaginatorVal:
                    SplitValues = PaginatorVal.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'subUrl' in eachSplitVal:
                            subUrl_Str = str(eachSplitVal.replace('subUrl=', '')).strip()
                        elif 'currPage' in eachSplitVal:
                            currPage_Str = str(eachSplitVal.replace('currPage=', '')).strip()
                        elif 'title' in eachSplitVal:
                            title_Str = str(eachSplitVal.replace('title=', '')).strip()
                    addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
                    print "gbzygil : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
            except:
                print "No Pagination found"

    elif ('thiruttuvcd' in subUrl) & ('MP3' not in subUrl):
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            if 'thiruttuvcd_masala' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttumasala.com/videos?o=lv&page=' + str(currPage)
            elif 'thiruttuvcd_tamilMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/page/' + str(currPage) + '/'
            elif 'thiruttuvcd_teluguMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/telugu/page/' + str(currPage) + '/'
            elif 'thiruttuvcd_hindiMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/hindi-movies-online/page/' + str(currPage) + '/'
            elif 'thiruttuvcd_tamilSerials' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/tv/page/' + str(currPage) + '/'

            print "GBZYGIL subUrl= " + subUrl + " , opening url :" + thiruttuvcd_url
            cache.delete("%")
            Dict_res = cache.cacheFunction(getMovList_thiruttuvcd, thiruttuvcd_url)
            print "<<<<< GBZYGIL thiruttuvcd received dict:"
            dump(Dict_res)
            for key, value in Dict_res.iteritems():
                if 'Paginator' not in key:
                    SplitValues = value.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = eachSplitVal.replace('mode=', '')
                        elif 'url' in eachSplitVal:
                            fullLink_Str = eachSplitVal.replace('url=', '')
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = eachSplitVal.replace('imgLink=', '')
                    mode_Str = mode_Str.encode('utf8')
                    fanarturl_Str = fanarturl_Str.encode('utf8').strip()
                    key = key.encode('utf8')
                    print mode_Str
                    print fanarturl_Str
                    print key
                    addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': key, 'img':fanarturl_Str}, {'title': key}, img=fanarturl_Str)
            try:
                PaginatorVal = Dict_res['Paginator']
                if PaginatorVal:
                    SplitValues = PaginatorVal.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'subUrl' in eachSplitVal:
                            subUrl_Str = str(eachSplitVal.replace('subUrl=', '')).strip()
                        elif 'currPage' in eachSplitVal:
                            currPage_Str = str(eachSplitVal.replace('currPage=', '')).strip()
                        elif 'title' in eachSplitVal:
                            title_Str = str(eachSplitVal.replace('title=', '')).strip()
                    addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
                    print "gbzygil : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
            except:
                print "No Pagination found"

#                 Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(CurrPage.text) + 1) + ',title=Next Page.. ' + paginationText})

    elif 'rajtamil' in subUrl:
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            if 'rajtamilTVshowsVijayTV' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/vijay-tv-shows/page/' + str(currPage) + '/'
            elif 'rajtamilTVshowsSunTV' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/sun-tv-show/page/' + str(currPage) + '/'
            elif 'rajtamilTVshowsZeeTamil' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/zee-tamil-tv-show/page/' + str(currPage) + '/'
            elif 'rajtamilTVshowsPolimer' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/polimer-tv-show-2/page/' + str(currPage) + '/'
            else:
                rajTamilurl = 'http://www.rajtamil.com/category/movies/page/' + str(currPage) + '/'
#             rajTamilurl = 'http://www.rajtamil.com/category/polimer-tv-show-2/'
            print "GBZYGIL subUrl= " + subUrl + " , opening url :" + rajTamilurl
            Dict_res = cache.cacheFunction(getMovList_rajtamil, rajTamilurl)

            print "<<<<< GBZYGIL rajtamil received dict:"
            dump(Dict_res)
            # dumpclean(Dict_res)
            for key, value in Dict_res.iteritems():
                if 'Paginator' not in key:
                    SplitValues = value.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'url' in eachSplitVal:
                            fullLink_Str = str(eachSplitVal.replace('url=', '')).strip()
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                    mode_Str = mode_Str.encode('utf8')
                    fanarturl_Str = fanarturl_Str.encode('utf8')
                    key = key.encode('utf8')


                    addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': key}, {'title': key}, img=fanarturl_Str)
            try:
                PaginatorVal = Dict_res['Paginator']
                if PaginatorVal:
                    SplitValues = PaginatorVal.split(",")
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'currPage' in eachSplitVal:
                            currPage_Str = str(eachSplitVal.replace('currPage=', '')).strip()
                        elif 'subUrl' in eachSplitVal:
                            subUrl_Str = str(eachSplitVal.replace('subUrl=', '')).strip()
                        elif 'title' in eachSplitVal:
                            title_Str = str(eachSplitVal.replace('title=', '')).strip()
                    print "GBZYGIL SETTING FOR NEXT LINK: " + mode_Str + ', ' + currPage_Str + ', ' + title_Str
                    addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
            except:
                print "No Pagination found"

    dlg.close()

elif mode == '200':
    with open(RootDir + "/favs.dat", 'a') as target:
        target.write(str(addon.queries.get('name', False)) + ',' + str(addon.queries.get('url', False)) + ',' + str(addon.queries.get('fanarturl', False)) + '\r\n')
    addon.show_small_popup('MalabarTalkies', str(addon.queries.get('name', False)) + ' added to favs', 4000, logo)

elif mode == 'ViewFavorites':
    print str(addon.queries)
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

#         req = urllib2.Request(searchurl)
#         req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
#         response = urllib2.urlopen(req)
#         link = response.read()
#         response.close()
        link = net.http_GET(searchurl).content
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
elif mode == 'ViewHistory':
#     addon.add_directory({'mode': 'clear_history', 'title': 'Clear History'}, {'title':'Clear History' })
#     a = 1
    try:
        for line in open(RootDir + "/history.dat", 'r').readlines():
            title, host, media_id, img = line.split(",")
#             print "-------"
#             print title
#             print host
#             print media_id
#             print img
#             print "-------"
            title = title.replace('title=', '').strip()
            host = host.replace('host=', '').strip()
            media_id = media_id.replace('media_id=', '').strip()
            img = media_id.replace('img=', '').strip()
#             print "title=" + title
#             addon.add_video_item({'host': host , 'media_id': media_id, 'img':img, 'title': title})
#             print "-------"
#             print title
#             print host
#             print media_id
#             print img
#             print "-------"
            addon.add_video_item({'host': host, 'media_id': media_id, 'AddtoHist':False}, {'title': title, 'img':img, 'AddtoHist':True})

#             addon.add_directory({'mode': 'individualmovie', 'url': fullLink, 'fanarturl': imgfullLink , 'title': names}, {'title': names}, img=imgfullLink)

    except IOError:
       addon.show_small_popup('MalabarTalkies', 'No History yet..', 4000, logo)

elif mode == 'olangalMalayalam':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent'}, {'title': 'Recent Movies'}, img=img_path + '/recent.PNG')
    addon.add_directory({'mode': 'GetSearchQuery'}, {'title': 'Search'}, img=img_path + '/search.PNG')
elif mode == 'abcmalayalam':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Mal'}, {'title': 'Malayalam Movies'}, img=img_path + '/malayalam.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-NonMal'}, {'title': 'Non-Malayalam Movies'}, img=img_path + '/nonmalayalam.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-shortFilm'}, {'title': 'Short Films'}, img=img_path + '/shortfilms.PNG')
    if SETTINGS_ENABLEADULT == 'YES':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-sizzling'}, {'title': 'Sizzling(18+)'}, img=img_path + '/18plus.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Comedy'}, {'title': 'Comedy'}, img=img_path + '/comedy.PNG')
elif mode == 'rajTamil':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilRecent'}, {'title': 'Recent Movies'}, img=img_path + '/rajTamil.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsVijayTV'}, {'title': 'TV Shows - Vijay TV'}, img=img_path + '/rajTamil.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsSunTV'}, {'title': 'TV Shows - Sun TV'}, img=img_path + '/rajTamil.PNG')
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsZeeTamil'}, {'title': 'TV Shows - Zee Tamil'}, img=img_path + '/rajTamil.PNG')
#     addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsPolimer'}, {'title': 'TV Shows - Polimer TV'}, img=img_path + '/rajTamil.PNG')

elif mode == 'thiruttuvcd':
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_tamilMovs'}, {'title': 'Tamil Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_teluguMovs'}, {'title': 'Telugu Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_hindiMovs'}, {'title': 'Hindi Movies'})
    #addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_tamilSerials'}, {'title': 'Tamil Serials'})
    if SETTINGS_ENABLEADULT:
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_masala'}, {'title': 'Thiruttu Masala'})

elif mode == 'main':
        addon.add_directory({'mode': 'olangalMalayalam'}, {'title': 'Malayalam : olangal.com'}, img=img_path + '/olangal.PNG')
        addon.add_directory({'mode': 'abcmalayalam'}, {'title': 'Malayalam : abcmalayalam.com'}, img=img_path + '/abcMal.PNG')
        addon.add_directory({'mode': 'rajTamil'}, {'title': 'Tamil : rajtamil.com'}, img=img_path + '/rajTamil.PNG')

        # TODO ThiruttuVCD
        addon.add_directory({'mode': 'thiruttuvcd'}, {'title': 'Tamil, Telugu, Hindi : Thiruttu VCD'})

#         addon.add_directory({'mode': 'ViewFavorites'}, {'title': 'Favorites'}, img=img_path + '/favorites.PNG')
#         addon.add_directory({'mode': 'ViewHistory'}, {'title': 'History'})
if not play:
    addon.end_of_directory()
