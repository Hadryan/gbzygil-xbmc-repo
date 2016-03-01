from tokenize import String
REMOTE_DBG = False 

# append pydev remote debugger
if REMOTE_DBG:
    # Make pydev debugger works for auto reload.
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd # with the addon script.module.pydevd, only use `import pydevd`
    # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
        sys.exit(1)

import urlresolver, os, re, sys, urllib, urllib2, xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
from xml.dom.minidom import parse
import xml.dom.minidom
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from bs4 import BeautifulSoup
from pyga.requests import Tracker, Page, Session, Visitor

import resolvers
    
#    return resolvers.resolve_url(url, filename)

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

tracker = Tracker('UA-61503824-1', 'http://github.com/gbzygil/gbzygil-xbmc-repo')
visitor = Visitor()
visitor.ip_address = xbmc.getIPAddress()
session = Session()

addon = Addon('plugin.video.malabartalkies', sys.argv)
SETTINGS_CACHE_TIMEOUT = addon.get_setting('Cache-Timeout')
#SETTINGS_CACHE_TIMEOUT = 60
SETTINGS_ENABLEADULT = addon.get_setting('EnableAdult')
ALLOW_HIT_CTR = addon.get_setting('AllowHitCtr')
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


Private_WorshipSongs_XML='https://raw.githubusercontent.com/gbzygil/gbzygil-xbmc-repo/master/Private_WorshipSongs.xml'
Private_WorshipMessages_XML='https://raw.githubusercontent.com/gbzygil/gbzygil-xbmc-repo/master/Private_WorshipMessages.xml'
Public_Shared_XML='https://raw.githubusercontent.com/gbzygil/gbzygil-xbmc-repo/master/Pubic_Shared.xml'



if not xbmcvfs.exists(RootDir + '/thumbs'):
    xbmcvfs.mkdirs(RootDir + '/thumbs')

class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    
    http_error_302 = http_error_301
    http_error_307 = http_error_301
    # just keep adding error codes to cover all the ones you want reported instead of having exceptions raised
    
def getMovList_KitMovie(KitMovie_url):
        print "================ checking cache hit : function getMovList_KitMovie was called with : " + KitMovie_url
        Dict_movlist = {}

        req = urllib2.Request(KitMovie_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        soup = BeautifulSoup(link)
        #print str(soup)
        ItemNum=0

        for row in soup.findAll("link", { "rel":"next" }):
            print "<<<<<<<<<<<<<  found pagination "
            nxtPgUrl= row.get('href')
            re1='.*?'    # Non-greedy match on filler
            re2='(\\d+)'    # Integer Number 1
            rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
            m = rg.search(nxtPgUrl)
            if  m:
                int1=m.group(1)
                print "<<<<<<<<<<<<<  found next pg " + str(int(int1)-1)
                paginationText = "( "+ str(int(int1)) +")\n"
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(int1)-1) + ',title=Next Page.. ' + paginationText})

        for row in soup.findAll("div", { "class":"col-sm-4 col-xs-6 item responsive-height" }):
            ItemNum=ItemNum+1
            img=row.find('img')['src']
            if '//' in str(img[ 0 : 0 + 2]):
        	    img=img.replace("//", "")
            print "GBC found imgUrl = " + str(img)



            currMovObj=row.find('h3')
            movTitle=currMovObj.text
            
            for currMovObj in row.findAll("a"):
                if currMovObj.has_attr('href'):                 
                    link=currMovObj.get('href')
                    Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + link + ', imgLink=' + img+', MovTitle='+movTitle})
                    break

        return Dict_movlist

def getMovList_thiruttuvcd(thiruttuvcd_url):
        print "================ checking cache hit : function getMovList_thiruttuvcd was called"
        Dict_movlist = {}

        if 'thiruttumasala' in thiruttuvcd_url:
            req = urllib2.Request(thiruttuvcd_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            base_url = 'http://www.thiruttumasala.com'
            soup = BeautifulSoup(link)
            ItemNum=0
            for eachItem in soup.findAll("div", { "class":"video_box" }):
                ItemNum=ItemNum+1
                links = eachItem.find_all('a')
                for link in links:
                    if link.has_attr('href'):
                        link = link.get('href')
                img = eachItem.find('img')['src']
                movTitle = eachItem.find('img')['alt']
                Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + base_url + link + ', imgLink=' + base_url + img+', MovTitle='+movTitle})
            try:
                CurrPage = soup.find("span", { "class":"currentpage" })
                print "<<<<<<<<<<<<<  found pagination " + CurrPage.text
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
            ItemNum=0
            for eachItem in soup.findAll("div", { "class":"postbox" }):
                ItemNum=ItemNum+1
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
                    Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + link + ', imgLink=' + img+', MovTitle='+movTitle})
#             try:
            CurrPage = soup.find("span", { "class":"pages" })
            print "<<<<<<<<<<<<<  found pagination " + CurrPage.text
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
        print "================ checking cache hit : function getMovList_rajtamil was called"

        Dict_movlist = {}
        link = net.http_GET(rajTamilurl).content
        soup = BeautifulSoup(link)
        # print soup.prettify()
        ItemNum=0
        for eachItem in soup.findAll('li'):
            for coveritem in eachItem.findAll("div", { "class":"cover"}):
                links = coveritem.find_all('a')
                for link in links:
                    ItemNum=ItemNum+1
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
                Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc+', MovTitle='+movTitle})

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
        elif 'tamil-dubbed' in rajTamilurl:
            subUrl = 'rajtamildubbed'
        else:
            subUrl = 'rajtamilRecent'

#         addon.add_directory({'mode': 'rajtamilMovies', 'currPage': int(CurrentPage) + 1 }, {'title': 'Next Page.. ' + paginationText})
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(CurrentPage) + 1) + ',title=Next Page.. ' + paginationText})
        return Dict_movlist

def getMovList_interval(interval_url):
        Dict_movlist = {}
        ItemNum=0

        print "================ checking cache hit : function getMovList_interval was called"
        print "GBZYGIL we are inside getMovList_interval WITH : "+str(addon.queries)
        subUrl=addon.queries.get('subUrl', False)
        if 'interval_featuredMovs' in subUrl:
            interval_url='http://interval.in'
            req = urllib2.Request(interval_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link=response.read()
            soup =BeautifulSoup(link,'html5lib')
            for eachCol in soup.findAll('td', {'width': 175}):
                print eachCol
                imglink = eachCol.find('img')
                #print "Column = "+eachCol.text.encode('utf8').strip()
                imgfullLink = imglink.get('src').strip()
                altTitle = imglink.get('title').strip()

                links = eachCol.find_all('a')
                for link in links:
                    if link.has_attr('href'):
                        ItemNum=ItemNum+1
                        #print eachCol.text.strip().replace(".","")+","+"http://interval.in/"+link.get('href')+","+imgfullLink
                        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + "http://interval.in/"+link.get('href') + ', imgLink=' + imgfullLink+', MovTitle='+altTitle})
            return Dict_movlist
            
        link = net.http_GET(interval_url).content
        soup =BeautifulSoup(link,'html5lib')
        table = soup.find('table')
        rows = table.findAll('tr')
        
        for tr in rows:
            cols = tr.findAll('td')
            for eachCol in cols:
                imglink = eachCol.find('img')
                print "Column = "+eachCol.text.encode('utf8').strip()
                imgfullLink = imglink.get('src').strip()
                links = eachCol.find_all('a')
                for link in links:
                    if link.has_attr('href'):
                        ItemNum=ItemNum+1
                        print eachCol.text.strip().replace(".","")+","+"http://interval.in/"+link.get('href')+","+imgfullLink
                        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + "http://interval.in/"+link.get('href') + ', imgLink=' + imgfullLink+', MovTitle='+eachCol.text.strip().replace(".","")})


        for eachItem in soup.findAll('p', {'align' : 'center'}):
            links = eachItem.find_all('a')
            for link in links:
                if link.has_attr('href'):
                    PagiUrl=link.get('href')
                    PageName=link.text
                    if 'index.php' in PagiUrl :
                        if 'next' not in PageName:
                            if 'prev' not in PageName:
                                ItemNum=ItemNum+1
                                print "Adding paginator to dict : Page "+link.text+","+"http://interval.in/"+PagiUrl
                                Dict_movlist.update({'Paginator'+str(ItemNum):'mode=GetMovies, subUrl=' + "http://interval.in/"+PagiUrl + ',Paginator currPage=' + str(ItemNum) + ',title=' + "Page "+link.text})

        return Dict_movlist
        
def getMovList_olangal(olangalurl):
            print "================ checking cache hit : function getMovList_olangal was called"
            Dict_movlist = {}
            print " current url = " + olangalurl
#            link = net.http_GET(olangalurl).content
#            soup = BeautifulSoup(link, 'html5lib')
            req = urllib2.Request(olangalurl)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()
            soup = BeautifulSoup(link)
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

            ItemNum=0
            for eachItem in soup.findAll("li", { "class":"border-radius-5 box-shadow"}):
                 ItemNum=ItemNum+1
                 imgfullLink = eachItem.find('img')['src']
                 fullLink = eachItem.find('a')['href']
                 names = eachItem.find('a')['title']
                 #.encode('ascii',errors='ignore')
                 Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + fullLink + ', imgLink=' + imgfullLink.strip()+', MovTitle='+names})
                 print " : Adding to cache dictionary :"+names+", mode=individualmovie, url=" + fullLink
#             addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent', 'currPage': int(currPage) + 1 }, {'title': 'Next Page.. ' + paginationText})
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=olangalMovies-Recent, currPage=' + str(int(currPage) + 1) + ',title=Next Page.. ' + paginationText+', Order='+str(ItemNum)})
            return Dict_movlist

def getMovList_ABCmal(abcmalUrl):
        print "================ checking cache hit : function getMovList_ABCmal was called"
        Dict_movlist = {}

        link = net.http_GET(abcmalUrl).content
        soup = BeautifulSoup(link)
        ItemNum=0
        for linksSection in soup.findAll("div", { "class":"itemContainer"}):
            ItemNum=ItemNum+1
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
            Dict_movlist.update({ItemNum:'mode=individualmovie, fullLink=' + fullLink + ', imgLink=' + imgfullLink.strip()+', MovTitle='+names})

        for Paginator in soup.findAll("div", { "class":"k2Pagination"}):
            try:
                Paginator.ul.decompose()
                paginationText = 'Next Page.. ( Currently in ' + str(Paginator.text).strip() + ' )'
                Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(int(currPage) + 21) + ', title=' + paginationText})
            except:
                print " : no pagination code found"
        return Dict_movlist

def getMovLinksForEachMov(url):

    url = addon.queries.get('url', False)

    if 'olangal.org' in url:
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        print ' current movie url : ' + url
        print ' current movie fanarturl : ' + fanarturl
        print ' current movie title : ' + movTitle

        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []
        videoclass = soup.find("div", { "class":"video-embed"})
        
        try:
            links = videoclass.find_all('a')
            for link in links:
                url = link.get('href')
                if 'pongomovies' in url:
                    link = net.http_GET(url).content
                    soup = BeautifulSoup(link)
                    for linksSection in soup.findAll("div", { "class":"tabs-catch-all" }):
                        if 'iframe' in str(linksSection.contents):
                            vidurl = str(linksSection.find('iframe')['src'])
                            hosted_media = urlresolver.HostedMediaFile(vidurl)
                            print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                            if urlresolver.HostedMediaFile(vidurl).valid_url():
                                sources.append(hosted_media)
                            else:
                                print '    not resolvable by urlresolver!'
                else:
                    hosted_media = urlresolver.HostedMediaFile(url)
                    print ' ' + movTitle + ' source found : ' + url + ', hosted_media : ' + str(hosted_media)
                    if urlresolver.HostedMediaFile(url).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
        except:
            print " : no embedded urls found using method 1"

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                url = link.get('src')
                hosted_media = urlresolver.HostedMediaFile(url)
                print ' ' + movTitle + ' source found : ' + url + ', hosted_media : ' + str(hosted_media)
                if urlresolver.HostedMediaFile(url).valid_url():
                    sources.append(hosted_media)
                else:
                    print '    not resolvable by urlresolver!'
        except:
                 print 'Nothing found using method 2!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            print "#### Adding from enum after filter : "
            print 'url = ' + s.get_url()
            print 'host = ' + s.get_host()
            print 'media_id = '+ s.get_media_id()
            if s.get_media_id():
                if s.get_host():
                    print "have proper media_id and host"
                    addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)
            else:
                vidhost = re.findall('//(.*?)/', s.get_url())[0]
                #addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'rajtamil.com' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('fanarturl', False))
            print ' current movie url : ' + url
            print ' current movie fanarturl : ' + fanarturl
            print ' current movie title : ' + movTitle
            link = net.http_GET(url).content
#            link = link.encode('utf8')

            soup = BeautifulSoup(link)
#            print soup.prettify('utf-8')
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
                                print " : Adding using method1 " + tail
                                sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=tail))

            except:
                print " : no embedded youtube urls found using method1 "

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
                            print " : Adding using method2 " + eI
                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(eI)))

            except:
                print " : no embedded youtube urls found using method2 "

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
                        print " : Adding using method3 " + tail

                        sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))
            except:
                print " : no embedded youtube urls found using method3 "

            try:
                for eachItem in soup.findAll('param', {'name': 'movie'}):
                    if eachItem.has_attr('value'):
#                         print eachItem['value']
#                         print " : Adding using method3 " + eachItem['value']
#                         sources.append(urlresolver.HostedMediaFile(url=eachItem['value']))
#                         sources.append(urlresolver.HostedMediaFile(url='http://www.youtube.com/v/Y0iJdORpTPE'))
                        httpurl1 = eachItem['value']
                        splitString = httpurl1.split("??")
                        link = splitString[0]
                        if 'youtube' in link:
                            (head, tail) = os.path.split(link)
                            tail = str(tail).replace('watch?v=', '')
                            print " : Adding using method3 " + tail

                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))

            except:
                print " : no embedded youtube urls found using method4 "

            try:
                for eachItem in soup.findAll("a"):
                    if eachItem.has_attr('href'):
                        link=eachItem.get('href')
                        if 'youtube' in link:
                            (head, tail) = os.path.split(link)
                            tail = str(tail).replace('watch?v=', '')
                            print " : Adding using method5 " + tail

                            sources.append(urlresolver.HostedMediaFile(host='youtube.com', media_id=str(tail)))

            except:
                print " : no embedded youtube urls found using method5 "
                
            try:
                videoclass = soup.find("div", { "class":"entry"})
                links = videoclass.find_all('iframe')
                for plink in links:
                    movLink = plink.get('src')
                    if 'googleplay' in movLink:
                        rlink = net.http_GET(movLink).content
                        flink = net.http_GET(movLink).get_url()
                        elink = re.findall('<source src="(.*?)"', rlink)[0] + '&stream=1'
                        opener = urllib2.build_opener(NoRedirectHandler())
                        opener.addheaders = [('Referer', flink)]
                        urllib2.install_opener(opener)
                        res = urllib2.urlopen(elink)
                        glink = res.info().getheader('location')
                        hosted_media = urlresolver.HostedMediaFile(glink)
                        print ' ' + movTitle + ' source found : ' + glink + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(glink).valid_url():
                            sources.append(hosted_media)
                        else:
                            print '    not resolvable by urlresolver!'
                    else:
                        hosted_media = urlresolver.HostedMediaFile(movLink)
                        print ' ' + movTitle + ' source found : ' + movLink + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(movLink).valid_url():
                            sources.append(hosted_media)
                        else:
                            print '    not resolvable by urlresolver!'

            except:
                print " : no embedded urls found using iframe method"

            try:
                videoclass = soup.find("div", { "class":"entry"})
                links = videoclass.find_all('a')
                for plink in links:
                    movLink = plink.get('href')
                    if 'googleplay' in movLink:
                        rlink = net.http_GET(movLink).content
                        flink = net.http_GET(movLink).get_url()
                        elink = re.findall('<source src="(.*?)"', rlink)[0] + '&stream=1'
                        opener = urllib2.build_opener(NoRedirectHandler())
                        opener.addheaders = [('Referer', flink)]
                        urllib2.install_opener(opener)
                        res = urllib2.urlopen(elink)
                        glink = res.info().getheader('location')
                        hosted_media = urlresolver.HostedMediaFile(glink)
                        print ' ' + movTitle + ' source found : ' + glink + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(glink).valid_url():
                            sources.append(hosted_media)
                        else:
                            print '    not resolvable by urlresolver!'
                    else:
                        hosted_media = urlresolver.HostedMediaFile(movLink)
                        print ' ' + movTitle + ' source found : ' + movLink + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(movLink).valid_url():
                            sources.append(hosted_media)
                        else:
                            print '    not resolvable by urlresolver!'

            except:
                print " : no embedded urls found using a method"

            for idx, s in enumerate(sources):
                print "#### Adding from enum after filter : "
                print 'url = ' + s.get_url()
                print 'host = ' + s.get_host()
                print 'media_id = '+ s.get_media_id()
                if s.get_media_id():
                    if s.get_host():
                        print "have proper media_id and host"
                        addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)
                else:
                    vidhost = re.findall('//(.*?)/', s.get_url())[0]
                    #addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                    addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)
                    
    elif 'thiruttuvcd.me' in url:
            url = addon.queries.get('url', False)
            subUrl = addon.queries.get('subUrl', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            try:
                print ' current movie url : ' + url
                print ' current movie SubUrl : ' + subUrl
                print ' current movie fanarturl : ' + fanarturl
                print ' current movie title : ' + movTitle
            except:
                print 'weird'
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()

            soup = BeautifulSoup(link)
            sources = []

            try:
                linksDiv = soup.find("div", { "class":"textsection col-lg-4 col-xs-12" })
                links = linksDiv.find_all('a')			
                for link in links:
                    vidurl = link.get('href').strip()
                    if 'dai.ly' not in vidurl:
                        hosted_media = urlresolver.HostedMediaFile(vidurl)
                        print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(vidurl).valid_url():
                            sources.append(hosted_media)
                        else:
                            print vidurl + ' is NOT resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 1!'

            try:
                links = soup.find_all('iframe')
                for link in links:
                    vidurl = link.get("data-lazy-src")
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 2!'

            sources = urlresolver.filter_source_list(sources)
            for idx, s in enumerate(sources):
                print "#### Adding from enum after filter : "
                print 'url = ' + s.get_url()
                print 'host = ' + s.get_host()
                print 'media_id = '+ s.get_media_id()
                if s.get_media_id():
                    if s.get_host():
                        print "have proper media_id and host"
                        addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)
                else:
                    vidhost = re.findall('//(.*?)/', s.get_url())[0]
					#addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                    addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'thiruttumasala' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            print ' current movie url : ' + url
            print ' current movie fanarturl : ' + fanarturl
            print ' current movie title : ' + movTitle
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            response = urllib2.urlopen(req)
            link = response.read()
            response.close()

            soup = BeautifulSoup(link)
            # print soup.prettify()
            try:
                re1='.*?'    # Non-greedy match on filler
                re2='(var)'    # Word 1
                re3='(\\s+)'    # White Space 1
                re4='(cnf)'    # Word 2
                re5='(=)'    # Any Single Character 1
                re6='(.)'    # Any Single Character 2
                re7='(http)'    # Word 3
                re8='(:)'    # Any Single Character 3
                re9='(\\/)'    # Any Single Character 4
                re10='(\\/www\\.thiruttumasala\\.com\\/media\\/nuevo\\/config\\.php)'    # Unix Path 1
                re11='(.)'    # Any Single Character 5
                re12='(key)'    # Word 4
                re13='(=)'    # Any Single Character 6
                re14='(\\d+)'    # Integer Number 1

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
            print ' current movie url : ' + url
            print ' current movie fanarturl : ' + fanarturl
            print ' current movie title : ' + movTitle
            link = net.http_GET(url).content
            soup = BeautifulSoup(link)
            sources = []

            try:
                linksDiv = soup.find("div", { "class":"itemFullText" })
                # most pages have a trailer embebbed. Lets include that too
                for linksSection in linksDiv.findAll("div", { "class":"avPlayerWrapper avVideo" }):
                    vidurl = str(linksSection.find('iframe')['src'])
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
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
                        print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(vidurl).valid_url():
                            sources.append(hosted_media)
                        else:
                            print vidurl + ' is NOT resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 2!'

            try:
                linksDiv = soup.find("div", { "class":"itemIntroText" })
                # some pages have a intro. Lets include that too
                for linksSection in linksDiv.findAll("div", { "class":"avPlayerWrapper avVideo" }):
                    vidurl = str(linksSection.find('iframe')['src'])
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 3!'

            sources = urlresolver.filter_source_list(sources)
            for idx, s in enumerate(sources):
                print "#### Adding from enum after filter : "
                print 'url = ' + s.get_url()
                print 'host = ' + s.get_host()
                print 'media_id = '+ s.get_media_id()
                if s.get_media_id():
                    if s.get_host():
                        print "have proper media_id and host"
                        addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)
                else:
                    vidhost = re.findall('//(.*?)/', s.get_url())[0]
					#addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                    addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'kitmovie.com' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            print ' current movie url : ' + url
            print ' current movie fanarturl : ' + fanarturl
            print ' current movie title : ' + movTitle
            
            link = net.http_GET(url).content
            soup = BeautifulSoup(link,'html5lib')
            sources = []
            
            for row in soup.findAll("div", { "class":"videoWrapper player" }):
                for currMovObj in row.findAll("iframe"):
                    if currMovObj.has_attr('src'):
                        vidurl=currMovObj.get('src')
                        #vidurl="http://www.youtube.com/5JTqw9sLjTs"
                        print "lets see if ["+vidurl+"] can be resolved"
                        if urlresolver.HostedMediaFile(vidurl).valid_url():
                            print 'resolvable! using isvalid_url'
                        hmf = urlresolver.HostedMediaFile(vidurl)
                        if hmf:
                            print '--------------- yay! we can resolve this one'
                        else:
                            print '--------------- sorry no resolvers available to handle this one.'
                        if 'embed' in vidurl:
                            print "********************** THIS IS A LINK WITH EMBED : " + vidurl 
                            

                        hosted_media = urlresolver.HostedMediaFile(vidurl)
                        #print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                        if urlresolver.HostedMediaFile(vidurl).valid_url():
                            sources.append(hosted_media)
                        else:
                            print '    not resolvable by urlresolver!'

                        #print "Primary url = " + currMovObj.get('src')
            for row in soup.findAll("a", { "class":"btn btn-success btn-lg btn-block  " }):
                print "Secondary url=" + row.get('href')
                vidurl=row.get('href')
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    print '    not resolvable by urlresolver!'
            sources = urlresolver.filter_source_list(sources)
            for idx, s in enumerate(sources):
                print "#### Adding from enum after filter : "
                print 'url = ' + s.get_url()
                print 'host = ' + s.get_host()
                print 'media_id = '+ s.get_media_id()
                if s.get_media_id():
                    if s.get_host():
                        print "have proper media_id and host"
                        addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                else:
                    #addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_url() + ')'}, img=fanarturl)
                    addon.add_video_item({'url': s.get_url()},{'title': movTitle},img=fanarturl,fanart=fanarturl)

    elif 'interval.in' in url:
            url = addon.queries.get('url', False)
            movTitle = str(addon.queries.get('title', False))
            fanarturl = str(addon.queries.get('img', False))
            print ' current movie url : ' + url
            print ' current movie fanarturl : ' + fanarturl
            print ' current movie title : ' + movTitle
            link = net.http_GET(url).content
            soup = BeautifulSoup(link,'html5lib')
            sources = []

            try:
                AllEmbeds=soup.findAll("embed")
                for eachEmbed in AllEmbeds:
                    vidurl=eachEmbed.get("src")
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                # most pages have a trailer embebbed. Lets include that too
                #for linksSection in linksDiv.findAll("div", { "class":"avPlayerWrapper avVideo" }):
                 #   vidurl = str(linksSection.find('iframe')['src'])
                  #  hosted_media = urlresolver.HostedMediaFile(vidurl)
                   # print ' ' + movTitle + ' source found : ' + vidurl + ', hosted_media : ' + str(hosted_media)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
            except:
                     print 'Nothing found using method 1!'

            sources = urlresolver.filter_source_list(sources)
            for idx, s in enumerate(sources):
                addon.add_video_item({'host': s.get_host() , 'media_id': s.get_media_id(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': movTitle + "," + s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)

def get_tag_value(node):
    """retrieves value of given XML node
    parameter:
    node - node object containing the tag element produced by minidom
 
    return:
    content of the tag element as string
    """
 
    xml_str = node.toxml() # flattens the element to string
 
    # cut off the base tag to get clean content:
    start = xml_str.find('>')
    if start == -1:
        return ''
    end = xml_str.rfind('<')
    if end < start:
        return ''
 
    return xml_str[start + 1:end]
print"############# MAIN MENU ##################"
print 'MODE = ' + str(addon.queries.get('mode', False))
print 'TITLE = ' + str(addon.queries.get('title', False))
print 'URL = ' + str(addon.queries.get('url', False))
print 'SUBURL = ' + str(addon.queries.get('subUrl', False))
print 'CURRPAGE = ' + str(addon.queries.get('currPage', False))
print"########################################"
CurrUrl=str(addon.queries.get('url', False))
if ALLOW_HIT_CTR == 'true':
    if CurrUrl != False:
        tracker.track_pageview(Page("/"+str(CurrUrl)), session, visitor)
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
   
    print "********* In Play with : url = "+url +", host="+host+ ", media_id="+media_id
    if url:
        stream_url = urlresolver.HostedMediaFile(url).resolve()
    else:
        stream_url = urlresolver.HostedMediaFile(host=host, media_id=media_id).resolve()

    print "** FINAL STREAM URL = " + str(stream_url)
    addon.resolve_url(stream_url)

elif mode == 'resolver_settings':
    urlresolver.display_settings()


elif mode == 'individualmovie':
    url = addon.queries.get('url', False)
    getMovLinksForEachMov(url)
#     print "@@@@@@@@@@@@@@ Dict of MovSources received :"
#     dump(ReceivedDict)

elif 'Worship' in mode:
        print "Inside WorshipSongs"
        # Open XML document using minidom parser
        if mode == 'Worship Songs':
            worshipUrl= urllib2.urlopen(Private_WorshipSongs_XML)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Worship/Songs'), session, visitor)
        elif mode == 'Worship Messages':
            worshipUrl= urllib2.urlopen(Private_WorshipMessages_XML)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Worship/Messages'), session, visitor)
        #parser.parse(toursurl)
        DOMTree = xml.dom.minidom.parse(worshipUrl)
        collection = DOMTree.documentElement
        if collection.hasAttribute("shelf"):
           print "Root element : %s" % collection.getAttribute("shelf")
        
        # Get all the movies in the collection
        movies = collection.getElementsByTagName("movie")
        
        # Print detail of each movie.
        for movie in movies:
           print "*****Movie*****"
           if movie.hasAttribute("title"):
              WorshipItem_title=unicode(movie.getAttribute("title"))
              WorshipItem_url=get_tag_value(movie.getElementsByTagName('url')[0])
              WorshipItem_img=get_tag_value(movie.getElementsByTagName('img')[0])
              print "title: %s" % WorshipItem_title
              print "url: %s" % WorshipItem_url
              print "img: %s" % WorshipItem_img
              #addon.add_video_item({'url':Worship_url, 'img':'', 'title': Worship_title}, {'title': Worship_title}, img='')
              addon.add_video_item({'url': WorshipItem_url},{'title': WorshipItem_title},img=WorshipItem_img)

              
elif mode == 'GetMovies':
    dlg = xbmcgui.DialogProgress()
    dlg.create("Malabar Talkies", "Fetching movies and caching...\nWill be faster next time")
    dlg.update(0)
    subUrl = addon.queries.get('subUrl', False)
    mode = addon.queries.get('mode', False)
    Url = addon.queries.get('Url', False)
    print "GBZYGIL we are inside GETMOVIES WITH : "+str(addon.queries)
    base_url = 'http://abcmalayalam.com'
    if 'ABCMalayalam' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 0
        if subUrl == 'ABCMalayalam-Mal':
            abcmalUrl = base_url + '/movies?start=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/ABCMalayalam/Malayalam'), session, visitor)
        elif subUrl == 'ABCMalayalam-shortFilm':
            abcmalUrl = base_url + '/short-film?start=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/ABCMalayalam/ShortFilm'), session, visitor)
        elif subUrl == 'ABCMalayalam-sizzling':
            abcmalUrl = base_url + '/sizzling?start=' + str(currPage)

        Dict_res = cache.cacheFunction(getMovList_ABCmal, abcmalUrl)
#         print "<<<<< received DICT="
#         dump(Dict_res)
        print " here's the sorted dict now"
            
        keylist = Dict_res.keys()
        keylist.sort()
        for key in keylist:
            print "%s: %s" % (key, Dict_res[key])
        MovTitle_Str=""
        for key, value in Dict_res.iteritems():
            if 'Paginator' not in value:
                SplitValues = value.split(",")
                for eachSplitVal in SplitValues:
                    if 'mode' in eachSplitVal:
                        mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                    elif 'fullLink' in eachSplitVal:
                        fullLink_Str = str(eachSplitVal.replace('fullLink=', '')).strip()
                    elif 'imgLink' in eachSplitVal:
                        IMGfullLink_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                    elif 'MovTitle' in eachSplitVal:
                        MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()
                if MovTitle_Str:
                    addon.add_directory({'mode': mode_Str, 'url': fullLink_Str , 'title': MovTitle_Str, 'img' :IMGfullLink_Str}, {'title': MovTitle_Str}, img=IMGfullLink_Str)
#                   print "<<< creating directory for " + key + "img=" + IMGfullLink_Str

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
                print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
        except:
            print "No pagination found"

    elif 'olangalMovies-Recent' in subUrl:
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Olangal'), session, visitor)
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            olangalurl = 'http://olangal.org/malayalam/page/' + str(currPage)
            Dict_res = cache.cacheFunction(getMovList_olangal, olangalurl)
            #print " lets dump the received Cach dict now"
            #dump(Dict_res)
            print " here's the sorted dict now"
            
            keylist = Dict_res.keys()
            keylist.sort()
            for key in keylist:
                print "%s: %s" % (key, Dict_res[key])
    
            for key, value in Dict_res.iteritems():
                print " : current key = "+str(key)+ ", value = "+ value
                if 'Paginator' not in value:
                    SplitValues = value.split(",")
                    mode_Str=""
                    fullLink_Str=""
                    fanarturl_Str=""
                    MovTitle_Str=""
                    for eachSplitVal in SplitValues:
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'url' in eachSplitVal:
                            fullLink_Str = str(eachSplitVal.replace('url=', '')).strip()
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                        elif 'MovTitle' in eachSplitVal:
                            MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()
                    if MovTitle_Str:
                        print " values before adding = "+mode_Str+", "+fullLink_Str+", "+fanarturl_Str+", "+MovTitle_Str
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
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
                    print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
            except:
                print "No Pagination found"

    elif ('KitMovies' in subUrl):
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 0
        currPage = int(currPage) + 1 
                                     
        if subUrl == 'KitMovies_Malayalam':
            Kitmovies_url = 'http://www.kitmovie.com/malayalam/categories/movie/page/' + str(currPage)+'/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Malayalam/Movies'), session, visitor) 
        elif subUrl == 'KitMovies_MalayalamSongs':
            Kitmovies_url = 'http://www.kitmovie.com/malayalam/categories/songs/page/' + str(currPage)+'/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Malayalam/Songs'), session, visitor)            
        elif subUrl == 'KitMovies_Tamil':
            Kitmovies_url = 'http://www.kitmovie.com/tamil/categories/movie/page/' + str(currPage)+'/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Tamil/Movies'), session, visitor)
        elif subUrl == 'KitMovies_TamilSongs':
            Kitmovies_url = 'http://www.kitmovie.com/tamil/categories/songs/page/' + str(currPage)+'/' 
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Tamil/Songs'), session, visitor)           
        elif subUrl == 'KitMovies_Hindi':
            Kitmovies_url = 'http://www.kitmovie.com/hindi/categories/movies/page/' + str(currPage)+'/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Hindi/Movies'), session, visitor)
        elif subUrl == 'KitMovies_HindiSongs':
            Kitmovies_url = 'http://www.kitmovie.com/hindi/categories/songs/page/' + str(currPage)+'/' 
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/KitMovie/Hindi/Songs'), session, visitor)           
        print " subUrl= " + subUrl + " , opening url :" + Kitmovies_url
        cache.delete("%")

        Dict_res = cache.cacheFunction(getMovList_KitMovie, Kitmovies_url)
        keylist = Dict_res.keys()
        keylist.sort()
        MovTitle_Str=""
        fanarturl_Str=""
        fullLink_Str=""
        mode_Str=""
        for key, value in Dict_res.iteritems():
            if 'Paginator' not in value:
                SplitValues = value.split(",")
                for eachSplitVal in SplitValues:
                    eachSplitVal = eachSplitVal.encode('utf8')
                    #print "inside dict loop with eachSplitVal=" + eachSplitVal
                    if 'mode' in eachSplitVal:
                        mode_Str = eachSplitVal.replace('mode=', '')
                    elif 'url' in eachSplitVal:
                        fullLink_Str = eachSplitVal.replace('url=', '')
                    elif 'imgLink' in eachSplitVal:
                        fanarturl_Str = eachSplitVal.replace('imgLink=', '')
                        #fanarturl_Str = BeautifulSoup(html_encoded_string, convertEntities=BeautifulSoup.HTML_ENTITIES)

                    elif 'MovTitle' in eachSplitVal:
                        MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()  
                if MovTitle_Str:
                    #mode_Str = mode_Str.encode('utf8')
                    fanarturl_Str = fanarturl_Str.strip()
                    print "adding : " + MovTitle_Str
                    addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str, 'img':fanarturl_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
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
                subUrl_Str=str(addon.queries.get('subUrl', False))
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
                print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
        except:
            print "No Pagination found"    
                       
    elif ('thiruttuvcd' in subUrl) & ('MP3' not in subUrl):
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            if 'thiruttuvcd_masala' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttumasala.com/videos?o=mr&page=' + str(currPage)
            elif 'thiruttuvcd_MalayalamMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/malayalam/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/ThiruttuVcd/Malayalam'), session, visitor)          
            elif 'thiruttuvcd_tamilMovs' in subUrl:
                #thiruttuvcd_url = 'http://www.thiruttuvcd.me/page/' + str(currPage) + '/'
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/tamil-movies-online/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/ThiruttuVcd/TamilMovies'), session, visitor) 
            elif 'thiruttuvcd_teluguMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/watch-telugu-movie/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/ThiruttuVcd/Telugu'), session, visitor) 
            elif 'thiruttuvcd_hindiMovs' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/hindi-movies-online/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/ThiruttuVcd/Hindi'), session, visitor) 
            elif 'thiruttuvcd_tamilSerials' in subUrl:
                thiruttuvcd_url = 'http://www.thiruttuvcd.me/tv/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/ThiruttuVcd/TamilSerials'), session, visitor) 

            print " subUrl= " + subUrl + " , opening url :" + thiruttuvcd_url
            cache.delete("%")
            Dict_res = cache.cacheFunction(getMovList_thiruttuvcd, thiruttuvcd_url)
            #print "<<<<<  thiruttuvcd received dict:"
            #dump(Dict_res)
            print " here's the sorted dict now"
            keylist = Dict_res.keys()
            keylist.sort()
            MovTitle_Str=""
            fanarturl_Str=""
            fullLink_Str=""
            mode_Str=""
            for key, value in Dict_res.iteritems():
                if 'Paginator' not in value:
                    SplitValues = value.split(",")
                    for eachSplitVal in SplitValues:
                        eachSplitVal = eachSplitVal.encode('utf8')
                        if 'mode' in eachSplitVal:
                            mode_Str = eachSplitVal.replace('mode=', '')
                        elif 'url' in eachSplitVal:
                            fullLink_Str = eachSplitVal.replace('url=', '')
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = eachSplitVal.replace('imgLink=', '')
                            #fanarturl_Str = BeautifulSoup(html_encoded_string, convertEntities=BeautifulSoup.HTML_ENTITIES)

                        elif 'MovTitle' in eachSplitVal:
                            MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()  
                    if MovTitle_Str:
                        #mode_Str = mode_Str.encode('utf8')
                        fanarturl_Str = fanarturl_Str.encode('utf8').strip()
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str, 'img':fanarturl_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
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
                    subUrl_Str=str(addon.queries.get('subUrl', False))
                    addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
                    print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
            except:
                print "No Pagination found"

    elif 'interval' in subUrl:
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1  
            if 'interval_MalayalamMovs' in subUrl:
                interval_url = 'http://interval.in/index.php?p=&searching=[Malayalam]'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Interval/Malayalam'), session, visitor)
            elif 'interval_TeluguMovs' in subUrl:
                interval_url = 'http://interval.in/index.php?p=&searching=[Telugu]'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Interval/Telugu'), session, visitor)
            elif 'interval_TamilMovs' in subUrl:
                interval_url = 'http://interval.in/index.php?p=&searching=[Tamil]' 
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Interval/Tamil'), session, visitor)              
            elif 'interval_featuredMovs' in subUrl:
                interval_url = 'http://interval.in/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Interval'), session, visitor)
            elif 'interval_NextPage' in subUrl:
                interval_url = addon.queries.get('url', False)
              
            print "opening url :" + interval_url
            Dict_res = cache.cacheFunction(getMovList_interval,interval_url)
            keylist = Dict_res.keys()
            keylist.sort()
            print "<<<<<  interval received dict:"
            #dump(Dict_res)
            MovTitle_Str=""
            fanarturl_Str=""
            fullLink_Str=""
            mode_Str=""
            PaginatorTitle_Str=""
            for key, value in Dict_res.iteritems():
                SplitValues = value.split(",")
                for eachSplitVal in SplitValues:
                    eachSplitVal = eachSplitVal.encode('utf8')
                    if 'mode' in eachSplitVal:
                        mode_Str = eachSplitVal.replace('mode=', '')
                    elif 'subUrl' in eachSplitVal:
                        PagiSubUrl_Str = eachSplitVal.replace('subUrl=', '')
                    elif 'url' in eachSplitVal:
                        fullLink_Str = eachSplitVal.replace('url=', '')
                    elif 'imgLink' in eachSplitVal:
                        fanarturl_Str = eachSplitVal.replace('imgLink=', '')
                        #fanarturl_Str = BeautifulSoup(html_encoded_string, convertEntities=BeautifulSoup.HTML_ENTITIES)
                    elif 'MovTitle' in eachSplitVal:
                        MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()  
                    elif 'title=' in eachSplitVal:
                        PaginatorTitle_Str = ">>> "+str(eachSplitVal.replace('title=', '')).strip() +" >>>"
                if 'Paginator' not in value:
                    if MovTitle_Str:
                        #mode_Str = mode_Str.encode('utf8')
                        print "Current value to add to ListView = "+fullLink_Str
                        fanarturl_Str = fanarturl_Str.encode('utf8').strip()
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str, 'img':fanarturl_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                elif 'Paginator' in value:    
                    print "GBC : make paginator with url"+ PagiSubUrl_Str
                    #addon.add_directory({'mode': 'GetMovies', 'url': PagiSubUrl_Str, 'subUrl': 'interval_MalayalamMovs' , 'title': PaginatorTitle_Str}, {'title': PaginatorTitle_Str})
                    #print "Current Pagination value to add to ListView = "+value
                    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'interval_NextPage', 'url': PagiSubUrl_Str }, {'title': PaginatorTitle_Str})

    elif 'rajtamil' in subUrl:
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            if 'rajtamilTVshowsVijayTV' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/vijay-tv-shows/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil/TVshowsVijayTV'), session, visitor)
            elif 'rajtamilTVshowsSunTV' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/sun-tv-show/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil/TVshowsSunTV'), session, visitor)
            elif 'rajtamilTVshowsZeeTamil' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/zee-tamil-tv-show/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil/TVshowsZeeTamilTV'), session, visitor)
            elif 'rajtamilTVshowsPolimer' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/polimer-tv-show-2/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil/TVshowsPolimerTV'), session, visitor)
            elif 'rajtamildubbed' in subUrl:
                rajTamilurl = 'http://www.rajtamil.com/category/tamil-dubbed/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil/TamilDubbed'), session, visitor)
            else:
                rajTamilurl = 'http://www.rajtamil.com/category/movies/page/' + str(currPage) + '/'
                if ALLOW_HIT_CTR == 'true':
                    tracker.track_pageview(Page('/Rajtamil'), session, visitor)

            print " subUrl= " + subUrl + " , opening url :" + rajTamilurl
            Dict_res = cache.cacheFunction(getMovList_rajtamil, rajTamilurl)

            #print "<<<<<  rajtamil received dict:"
            #dump(Dict_res)
            # dumpclean(Dict_res)
            print " here's the sorted dict now"
            
            keylist = Dict_res.keys()
            keylist.sort()
            #for key in keylist:
                #print "%s: %s" % (key, Dict_res[key])
            MovTitle_Str=""    
            fanarturl_Str=""
            
            for key, value in Dict_res.iteritems():
                if 'Paginator' not in value:
                    SplitValues = value.split(",")
                    try:
                        for eachSplitVal in SplitValues:
                            eachSplitVal = eachSplitVal.encode('utf8')
                            if 'mode' in eachSplitVal:
                                mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                            elif 'url' in eachSplitVal:
                                fullLink_Str = str(eachSplitVal.replace('url=', '')).strip()
                            elif 'imgLink' in eachSplitVal:
                                fanarturl_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                            elif 'MovTitle' in eachSplitVal:
                                MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()
                    
                        if MovTitle_Str:
                        #mode_Str = mode_Str.encode('utf8')
                        #fanarturl_Str = fanarturl_Str.encode('utf8')
                        #MovTitle_Str = MovTitle_Str.encode('utf8')
                            addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                    except:
                        print "No likey exception caught"                        
            try:
                PaginatorVal = Dict_res['Paginator']
                if PaginatorVal:
                    SplitValues = PaginatorVal.split(",")
                    for eachSplitVal in SplitValues:
                        eachSplitVal = eachSplitVal.encode('utf8')
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'currPage' in eachSplitVal:
                            currPage_Str = str(eachSplitVal.replace('currPage=', '')).strip()
                        elif 'subUrl' in eachSplitVal:
                            subUrl_Str = str(eachSplitVal.replace('subUrl=', '')).strip()
                        elif 'title' in eachSplitVal:
                            title_Str = str(eachSplitVal.replace('title=', '')).strip()
                    print " SETTING FOR NEXT LINK: " + mode_Str + ', ' + currPage_Str + ', ' + title_Str
                    addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
            except:
                print "No Pagination found"

    dlg.close()

elif mode == 'olangalMalayalam':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Olangal_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent'}, {'title': 'Recent Movies'})
elif mode == 'abcmalayalam':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/AbcMalayalam_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-Mal'}, {'title': 'Malayalam Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-shortFilm'}, {'title': 'Short Films'})
    if SETTINGS_ENABLEADULT == 'true':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-sizzling'}, {'title': 'Sizzling(18+)'})
elif mode == 'rajTamil':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Rajtamil_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilRecent'}, {'title': 'Recent Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamildubbed'}, {'title': 'Dubbed Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsVijayTV'}, {'title': 'TV Shows - Vijay TV'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsSunTV'}, {'title': 'TV Shows - Sun TV'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsZeeTamil'}, {'title': 'TV Shows - Zee Tamil'})

elif mode == 'thiruttuvcd':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Thiruttuvcd_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_MalayalamMovs'}, {'title': 'Malayalam Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_tamilMovs'}, {'title': 'Tamil Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_teluguMovs'}, {'title': 'Telugu Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_hindiMovs'}, {'title': 'Hindi Movies'})
    if SETTINGS_ENABLEADULT == 'true':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_masala'}, {'title': 'Thiruttu Masala'})

elif mode == 'interval':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Interval_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'interval_featuredMovs'}, {'title': ' - Featured Movies - '})        
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'interval_MalayalamMovs'}, {'title': 'Malayalam Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'interval_TamilMovs'}, {'title': 'Tamil Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'interval_TeluguMovs'}, {'title': 'Telugu Movies'})    
elif mode == 'KitMovies':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/KitMovie_Main'), session, visitor)
        #GBC add a new hitcounter
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_Malayalam'}, {'title': 'Malayalam Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_MalayalamSongs'}, {'title': 'Malayalam Music Videos'})        
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_Tamil'}, {'title': 'Tamil Movies'}) 
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_TamilSongs'}, {'title': 'Tamil Music Videos'})       
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_Hindi'}, {'title': 'Hindi Movies'})   
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'KitMovies_HindiSongs'}, {'title': 'Hindi Music Videos'})   


elif mode == 'main':
        #addon.add_directory({'mode': 'olangalMalayalam'}, {'title': 'Malayalam : olangal.org'})
        addon.add_directory({'mode': 'KitMovies'}, {'title': 'Malayalam, Tamil, Hindi : KitMovie.com'})
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent'}, {'title':'Malayalam : olangal.org'})
        addon.add_directory({'mode': 'abcmalayalam'}, {'title': 'Malayalam : abcmalayalam.com'})
        addon.add_directory({'mode': 'rajTamil'}, {'title': 'Tamil : rajtamil.com'})
        addon.add_directory({'mode': 'thiruttuvcd'}, {'title': 'Malayalam, Tamil, Telugu, Hindi : Thiruttu VCD'})
        addon.add_directory({'mode': 'Worship Songs'}, {'title': '[COLOR yellow]+ Worship Songs+[/COLOR]'})
        addon.add_directory({'mode': 'Worship Messages'}, {'title': '[COLOR yellow]+ Worship Messages+[/COLOR]'})
        addon.add_directory({'mode': 'PublicPlaylists'}, {'title': '[COLOR green]User submitted content[/COLOR]'})

#         addon.add_directory({'mode': 'ViewFavorites'}, {'title': 'Favorites'}, img=img_path + '/favorites.PNG')
#         addon.add_directory({'mode': 'ViewHistory'}, {'title': 'History'})
        if ALLOW_HIT_CTR == 'true':
            tracker.track_pageview(Page('/Main'), session, visitor)

if not play:
    addon.end_of_directory()
