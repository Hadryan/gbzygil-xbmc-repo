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
SETTINGS_ENABLEADULT = addon.get_setting('EnableAdult')
ALLOW_HIT_CTR = addon.get_setting('AllowHitCtr')
cache = StorageServer.StorageServer("malabartalkies", SETTINGS_CACHE_TIMEOUT)
net = Net()
logo = os.path.join(addon.get_path(), 'icon.png')
currPage = 0
search_text = ''
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

def GetSearchQuery(sitename):
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search ' + sitename)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_text = keyboard.getText()
    
    return search_text

def getMovList_thiruttuvcd(thiruttuvcd_url):
    #print "================ checking cache hit : function getMovList_thiruttuvcd was called"
    Dict_movlist = {}

    if 'thiruttumasala' in thiruttuvcd_url:
        url = thiruttuvcd_url
        subUrl = 'thiruttuvcd_masala'
        link = net.http_GET(url).content
        base_url = 'http://www.thiruttumasala.com'
        soup = BeautifulSoup(link)
        ItemNum=0
        for eachItem in soup.findAll('div', { 'class':'video_box' }):
            ItemNum=ItemNum+1
            links = eachItem.find_all('a')
            for link in links:
                if link.has_attr('href'):
                    link = link.get('href')
            img = eachItem.find('img')['src']
            movTitle = eachItem.find('img')['alt']
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + base_url + link + ', imgLink=' + base_url + img+', MovTitle='+movTitle})

        Paginator = soup.find('div', { 'class':'pagination'})
        currPage = Paginator.find('span', { 'class':'currentpage'})
        CurrentPage = int(currPage.string)

        for eachPage in Paginator.findAll('a'):
            if ('Next' not in eachPage.contents[0]) and ('Prev' not in eachPage.contents[0]):
                lastPage = int(eachPage.string)
                
        if (CurrentPage < lastPage):
            paginationText = '(Currently in Page ' + str(CurrentPage) + ' of ' + str(lastPage) + ')\n'
        else:
            paginationText = ''
            
        if paginationText:
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText})

    elif '/private/' in thiruttuvcd_url:
        url = thiruttuvcd_url
        subUrl = 'thiruttuvcd_adult'
        link = net.http_GET(url).content
        soup = BeautifulSoup(link,'html.parser')
        ItemNum = 0
        Items = soup.find_all(class_='boxentry')
        for eachItem in Items:
            ItemNum = ItemNum+1
            movPage = eachItem.find('a')['href']
            imgSrc = eachItem.find('img')['src']
            movTitle = (eachItem.find('a')['title']).encode('utf8')
            movTitle = movTitle.replace('Hot', '')
            movTitle = movTitle.replace('Movies', '')
            movTitle = movTitle.replace('Movie', '')
            movTitle = movTitle.replace('Glamour', '')
            movTitle = movTitle.replace('Romantic', '')
            movTitle = movTitle.replace('Sex', '')
            movTitle = movTitle.replace('Full', '')
            movTitle = movTitle.replace('Adults', '')
            movTitle = movTitle.replace('hot', '')
            movTitle = movTitle.replace('Hindi', '')
            movTitle = movTitle.replace('Bollywood', '')
            movTitle = movTitle.replace('movie', '')
            movTitle = movTitle.replace('Tamil', '')
            movTitle = movTitle.replace('full', '')
            movTitle = movTitle.replace('Watch', '')
            movTitle = movTitle.replace('Online', '')
            movTitle = movTitle.replace('online', '')
            movTitle = movTitle.replace('Telugu', '')
            movTitle = movTitle.replace('Malayalam', '')
            movTitle = movTitle.replace('Length', '')
            movTitle = movTitle.replace('Masala', '')
            movTitle = movTitle.replace('18+', '')
            movTitle = movTitle.strip()
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8')})

        CurrentPage = int(re.findall("class='current'>(.*?)<", link)[0])
        lastPage = int(re.findall("class='pages'>.*?of (.*?)<", link)[0])

        if (CurrentPage < lastPage):
            paginationText = '(Currently in Page ' + str(CurrentPage) + ' of ' + str(lastPage) + ')\n'
        else:
            paginationText = ''
            
        if paginationText:
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText})

    else:
        url = thiruttuvcd_url
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        ItemNum=0
        for eachItem in soup.findAll('div', { 'class':'postbox' }):
            ItemNum=ItemNum+1
            links = eachItem.find_all('a')
            for link in links:
                if link.has_attr('href'):
                    link = link.get('href')
            img = eachItem.find('img')['src']
            movTitle = eachItem.find('img')['alt']
            movTitle = movTitle.replace('Full', '')
            movTitle = movTitle.replace('For Free', '')
            movTitle = movTitle.replace('Tamil', '')
            movTitle = movTitle.replace('Hindi', '')
            movTitle = movTitle.replace('Malayalam', '')
            movTitle = movTitle.replace('Telugu', '')
            movTitle = movTitle.replace('Movie', '')
            movTitle = movTitle.replace('Watch', '')
            movTitle = movTitle.replace('watch', '')
            movTitle = movTitle.replace('Online', '')
            movTitle = movTitle.replace('online', '')
            movTitle = movTitle.replace('Download', '')
            movTitle = movTitle.replace('download', '')
            movTitle = movTitle.strip()
            if ('MP3' not in movTitle) & ('Songs' not in movTitle):
                Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + link + ', imgLink=' + img+', MovTitle='+movTitle})

        paginationText = ''
        CurrPage = soup.find('span', { 'class':'pages' })
        if CurrPage:
            txt = CurrPage.text
            re1 = '.*?'  # Non-greedy match on filler
            re2 = '(\\d+)'  # Integer Number 1
            rg = re.compile(re1 + re2, re.IGNORECASE | re.DOTALL)
            m = rg.search(txt)
            if m:
                int1 = m.group(1)
                CurrentPage = int(int1)
                paginationText = "(Currently in " + txt + ")\n"

        if 'tamil-movies' in thiruttuvcd_url:
            subUrl = 'thiruttuvcd_tamilMovs'
        elif 'malayalam/' in thiruttuvcd_url:
            subUrl = 'thiruttuvcd_MalayalamMovs'
        elif 'telugu-movie' in thiruttuvcd_url:
            subUrl = 'thiruttuvcd_teluguMovs'
        elif 'hindi-movies' in thiruttuvcd_url:
            subUrl = 'thiruttuvcd_hindiMovs'
        elif '/?s=' in thiruttuvcd_url:
            subUrl = 'thiruttuvcd_search'
            
        if paginationText:
            Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})            
        
    return Dict_movlist

def getMovList_rajtamil(rajTamilurl):

    Dict_movlist = {}
    link = net.http_GET(rajTamilurl).content
    soup = BeautifulSoup(link)
    ItemNum=0
    for eachItem in soup.findAll('li'):
        for coveritem in eachItem.findAll("div", { "class":"post-thumb"}):
            links = coveritem.find_all('a')
            for link in links:
                ItemNum=ItemNum+1
                movTitle = link['title'].encode('utf8')
                movTitle = movTitle.replace('-', '')
                movTitle = movTitle.replace('|', '')
                movTitle = movTitle.replace('Watch', '')
                movTitle = movTitle.replace('DVD', '')
                movTitle = movTitle.replace('HD', '')
                movTitle = movTitle.replace('Movie', '')
                movTitle = movTitle.replace('movie', '')
                movTitle = movTitle.replace('tamil', '')
                movTitle = movTitle.replace('Tamil', '')
                movTitle = movTitle.replace('Online', '')
                movTitle = movTitle.replace('Dubbed', '')
                movTitle = movTitle.replace('Super', '')
                movTitle = movTitle.replace('Hilarious', '')
                movTitle = movTitle.replace('Ultimate', '')
                movTitle = movTitle.replace('Best', '')
                movTitle = movTitle.replace('Classy ', '')
                movTitle = movTitle.replace('comedy ', '')
                movTitle = movTitle.replace('Comedy', '')
                movTitle = movTitle.replace('Video', '')
                movTitle = movTitle.replace('Scenes', '')
                movTitle = movTitle.replace('Scene', '')
                movTitle = movTitle.replace('Songs', '')
                movTitle = movTitle.replace('songs', '')
                movTitle = movTitle.replace('online', '')
                movTitle = movTitle.strip()
                movPage = link['href']
            try:
                imgSrc = coveritem.find('img')['src']
            except:
                imgSrc = ''

            contextMenuItems = []
            contextMenuItems.append(('Add to Favorites', 'XBMC.RunPlugin(%s?mode=200&name=%s&url=%s&fanarturl=%s)' % (sys.argv[0], movTitle.decode('utf8'), movPage, imgSrc)))
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8')})

    Paginator = soup.find("div", { "class":"navigation"})
    paginationText=''
    currPage = Paginator.find("span", { "class":"page-numbers current"})
    if currPage:
        CurrentPage = int(currPage.string)

        for eachPage in Paginator.findAll("a", { "class":"page-numbers"}):
            if "Next" not in eachPage.contents[0] and "Prev" not in eachPage.contents[0]:
                lastPage = int(eachPage.string)
                
        if (CurrentPage < lastPage):
            paginationText = "( Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"

        
    if 'comedy' in rajTamilurl:
        subUrl = 'rajtamilcomedy'
    elif 'songs' in rajTamilurl:
        subUrl = 'rajtamilsongs'
    elif 'tamil-dubbed' in rajTamilurl:
        subUrl = 'rajtamildubbed'
    elif 'vijay-tv-shows' in rajTamilurl:
        subUrl = 'rajtamilTVshowsVijayTV'
    elif 'sun-tv-show' in rajTamilurl:
        subUrl = 'rajtamilTVshowsSunTV'
    elif '/?s=' in rajTamilurl:
        subUrl = 'rajtamilsearch'
    else:
        subUrl = 'rajtamilRecent'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_mersal(mersalurl):
    Dict_movlist = {}
    req = urllib2.Request(mersalurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link,'html.parser')
    #xbmc.log(msg='========== soup: ' + (soup.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
    lsoup = soup.find('div', { 'id':'wrapper' })
    ItemNum = 0
    Items = soup.findAll(class_='col-sm-6 col-md-4 col-lg-4')
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        ItemNum = ItemNum+1
        movTitle = eachItem.find('img')['title']
        movPage = 'http://mersalaayitten.com' + eachItem.find('a')['href']
        try:
            imgSrc = eachItem.find('img')['data-original']
        except:
            imgSrc = eachItem.find('img')['src']
        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc+', MovTitle='+movTitle})

    Paginator = soup.find("ul", { "class":"pagination pagination-lg"})
    paginationText = ''
    try:
        currPage = Paginator.find("li", { "class":"active"})
    except:
        currPage = ''
    if currPage:
        CurrentPage = int(currPage.span.string)

        for eachPage in Paginator.findAll("li", { "class":"hidden-xs"}):
            lastPage = int(eachPage.a.string)

        if (CurrentPage < lastPage):
            paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"

    if 'c=1' in mersalurl:
        subUrl = 'mersal_Tamil'
    elif 'c=2' in mersalurl:
        subUrl = 'mersal_Hindi'
    elif 'c=3' in mersalurl:
        subUrl = 'mersal_Telugu'
    elif 'c=4' in mersalurl:
        subUrl = 'mersal_Malayalam'
    elif 'c=5' in mersalurl:
        subUrl = 'mersal_Animation'
    elif 'c=6' in mersalurl:
        subUrl = 'mersal_Dubbed'
    elif 'search_query=' in mersalurl:
        subUrl = 'mersal_search'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_ftube(ftubeurl):
    Dict_movlist = {}
    req = urllib2.Request(ftubeurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link)
    #xbmc.log(msg='========== soup: ' + (soup.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
    lsoup = soup.find(id="archive")
    ItemNum = 0
    hyph = u'\u2013'.encode('utf8')
    Items = lsoup.findAll(class_='cover')
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        ItemNum = ItemNum+1
        movTitle = (eachItem.find('a')['title']).encode('utf8')
        movTitle = movTitle.replace(hyph, '')
        movTitle = movTitle.replace('Watch', '')
        movTitle = movTitle.replace('Tamil', '')
        movTitle = movTitle.replace('Telugu', '')
        movTitle = movTitle.replace('Hindi', '')
        movTitle = movTitle.replace('Movie', '')
        movTitle = movTitle.replace('Online', '')
        movTitle = movTitle.replace('Full', '')
        movTitle = movTitle.replace('Punjabi', '')
        movTitle = movTitle.replace('DVDSCR', '')
        movTitle = movTitle.replace('VDSCR', '')
        movTitle = movTitle.replace('Dubbed', '')
        movTitle = movTitle.replace('DVD', '')
        movTitle = movTitle.replace('*Bluray*', '')
        movTitle = movTitle.replace('*BluRay*', '')
        movTitle = movTitle.strip()
        movPage = eachItem.find('a')['href']
        imgSrc = eachItem.find('img')['src']
        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8')})

    Paginator = soup.find(class_='navigation')
    paginationText=''
    currPage = Paginator.find('span', { 'class':'page-numbers current'})
    if currPage:
        CurrentPage = int(currPage.string)

        for eachPage in Paginator.findAll('a'):
            if "Next" not in eachPage.contents[0] and "Prev" not in eachPage.contents[0]:
                lastPage = int(eachPage.string)

        if (CurrentPage < lastPage):
            paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"

    if '-tamil-' in ftubeurl:
        subUrl = 'ftube_Tamil'
    elif '-telugu-' in ftubeurl:
        subUrl = 'ftube_Telugu'
    elif '-punjabi-' in ftubeurl:
        subUrl = 'ftube_Punjabi'
    elif 'dubbed' in ftubeurl:
        subUrl = 'ftube_Dubbed'
    elif 'hindi' in ftubeurl:
        subUrl = 'ftube_Hindi'
    elif '/?s=' in ftubeurl:
        subUrl = 'ftube_search'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_tamilgun(tamilgunurl):
    #xbmc.log(msg='================ checking cache hit : function getMovList_tamilgun was called with : ' + tamilgunurl, level=xbmc.LOGNOTICE)

    Dict_movlist = {}

    req = urllib2.Request(tamilgunurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link,'html5lib')
    lsoup = soup.find(class_='col-sm-8')
    ItemNum = 0
    Items = lsoup.findAll(class_='col-sm-4 col-xs-6 item')
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        ItemNum = ItemNum+1
        movTitle = eachItem.h3.a.string
        movPage = eachItem.find('a')['href']
        imgSrc = eachItem.find('img')['src']
        movTitle = movTitle.replace('Full', '')
        movTitle = movTitle.replace('full', '')
        movTitle = movTitle.replace('-', '')
        movTitle = movTitle.replace('Comedy', '')
        movTitle = movTitle.replace('comedy', '')
        movTitle = movTitle.replace('Scenes', '')
        movTitle = movTitle.replace('scenes', '')
        movTitle = movTitle.replace('Movie', '')
        movTitle = movTitle.replace('Best', '')
        movTitle = movTitle.replace('Tamil ', '')
        movTitle = movTitle.replace('Collection', '')
        movTitle = movTitle.strip()
        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc+', MovTitle='+movTitle})

    Paginator = lsoup.find("ul", { "class":"pagination"})
    currPage = Paginator.find("li", { "class":"active"})
    CurrentPage = int(currPage.a.string)
    lastPage = CurrentPage
    lPage = Paginator.find("li", { "class":"last"})
    if lPage:
        laPage = lPage.find('a')['href']
        lastPage = re.findall('page/(\\d*)', laPage)[0]
    
    if (CurrentPage < lastPage):
        paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"
    else:
        paginationText = ""

    if 'new-movies' in tamilgunurl:
        subUrl = 'tamilgunnew'
    elif 'dubbed-movies' in tamilgunurl:
        subUrl = 'tamilgundubbed'
    elif 'hd-movies' in tamilgunurl:
        subUrl = 'tamilgunhd'
    elif 'hd-comedys' in tamilgunurl:
        subUrl = 'tamilguncomedy'
    elif 'trailers' in tamilgunurl:
        subUrl = 'tamilguntrailer'
    elif '/?s=' in tamilgunurl:
        subUrl = 'tamilgunsearch'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_flinks(flinksurl):
    #xbmc.log(msg='================ checking cache hit : function getMovList_flinks was called with : ' + flinksurl, level=xbmc.LOGNOTICE)

    Dict_movlist = {}

    req = urllib2.Request(flinksurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link,'html5lib')
    lsoup = soup.find(id="content_box")
    hyph = u'\u2013'.encode('utf8')
    ItemNum = 0
    Items = lsoup.findAll(class_='post excerpt')
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        asoup = eachItem.find(class_='post-content image-caption-format-1')
        movPage = eachItem.find('a')['href']
        imgSrc = eachItem.find('img')['src']
        movTitle = (eachItem.find('a')['title']).encode('utf8')
        movTitle = movTitle.replace(hyph, '')
        movTitle = movTitle.replace('Watch', '')
        movTitle = movTitle.replace('Tamil', '')
        movTitle = movTitle.replace('Malayalam', '')
        movTitle = movTitle.replace('Telugu', '')
        movTitle = movTitle.replace('Hindi', '')
        movTitle = movTitle.replace('Kannada', '')
        movTitle = movTitle.replace('Hollywood', '')
        movTitle = movTitle.replace('Movie', '')
        movTitle = movTitle.replace('Short ', '')
        movTitle = movTitle.replace('Online', '')
        movTitle = movTitle.replace('Biography', '')
        movTitle = movTitle.replace('Documentary', '')
        movTitle = movTitle.replace('Full', '')
        movTitle = movTitle.replace('Free', '')
        movTitle = movTitle.replace('Bengali', '')
        movTitle = movTitle.replace('Bhojpuri', '')
        movTitle = movTitle.replace('Gujarati', '')
        movTitle = movTitle.replace('Marathi', '')
        movTitle = movTitle.replace('Nepali', '')
        movTitle = movTitle.replace('Oriya', '')
        movTitle = movTitle.replace('Punjabi', '')
        movTitle = movTitle.replace('Panjabi', '')
        movTitle = movTitle.replace('Rajasthani', '')
        movTitle = movTitle.replace('Urdu', '')
        movTitle = movTitle.strip()
        #xbmc.log(msg='==========Title: ' + movTitle + '\n========== Item Genre: ' + (asoup.text).encode('utf-8'), level=xbmc.LOGNOTICE)
        try:
            Rating = asoup.text
        except:
            Rating = ''
        if ('Adult' not in Rating):
            ItemNum = ItemNum+1
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8') })
        elif SETTINGS_ENABLEADULT == 'true':
            ItemNum = ItemNum+1
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8') })

    Paginator = lsoup.find("div", { "class":"pagination"})
    paginationText = ''
    try:
        currPage = Paginator.find("li", { "class":"current"})
    except:
        currPage = ''
            
    if currPage:
        CurrentPage = int(currPage.span.string)
        for eachPage in Paginator.findAll("a", { "class":"inactive"}):
            if 'Last' in eachPage.text:
                laPage = eachPage.get('href')
                lastPage = re.findall('page/(\\d*)', laPage)[0]
            elif ('Next' not in eachPage.text) and ('Pre' not in eachPage.text):
                lastPage = int(eachPage.text)
        
        if (CurrentPage < lastPage):
            paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"

    if 'tamil' in flinksurl:
        subUrl = 'flinkstamil'
    elif 'malayalam' in flinksurl:
        subUrl = 'flinksmalayalam'
    elif 'telugu' in flinksurl:
        subUrl = 'flinkstelugu'
    elif 'adult-hindi' in flinksurl:
        subUrl = 'flinkshindisc'
    elif 'hindi' in flinksurl:
        subUrl = 'flinkshindi'
    elif 'kannada' in flinksurl:
        subUrl = 'flinkskannada'
    elif 'adult' in flinksurl:
        subUrl = 'flinksadult'
    elif 'animation' in flinksurl:
        subUrl = 'flinksani'
    elif 'hollywood' in flinksurl:
        subUrl = 'flinksholly'
    elif 'bengali' in flinksurl:
        subUrl = 'flinksben'
    elif 'bhojpuri' in flinksurl:
        subUrl = 'flinksbhoj'
    elif 'biography' in flinksurl:
        subUrl = 'flinksbio'
    elif 'documentary' in flinksurl:
        subUrl = 'flinksdocu'
    elif 'gujarati' in flinksurl:
        subUrl = 'flinksguj'
    elif 'marathi' in flinksurl:
        subUrl = 'flinksmar'
    elif 'nepali' in flinksurl:
        subUrl = 'flinksnep'
    elif 'oriya' in flinksurl:
        subUrl = 'flinksori'
    elif 'punjabi' in flinksurl:
        subUrl = 'flinkspun'
    elif 'rajasthani' in flinksurl:
        subUrl = 'flinksraj'
    elif 'urdu' in flinksurl:
        subUrl = 'flinksurdu'
    elif '/?s=' in flinksurl:
        subUrl = 'flinkssearch'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_hlinks(hlinksurl):
    #xbmc.log(msg='================ checking cache hit : function getMovList_flinks was called with : ' + flinksurl, level=xbmc.LOGNOTICE)

    Dict_movlist = {}

    req = urllib2.Request(hlinksurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link,'html5lib')
    lsoup = soup.find(class_='nag cf')
    ItemNum = 0
    hyph = u'\u2013'.encode('utf8')
    Items = lsoup.find_all(lambda tag: tag.has_attr('id'))
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        movsec = eachItem.find(class_='thumb')
        movdet = eachItem.find(class_='entry-summary')
        movPage = movsec.find('a')['href']
        imgSrc = movsec.find('img')['src']
        movTitle = (movsec.find('a')['title']).encode('utf8')
        movTitle = movTitle.replace(hyph, '')
        movTitle = movTitle.replace('(In Hindi)', '')
        movTitle = movTitle.replace('Documentary', '')
        movTitle = movTitle.replace('Hot Hindi Movie', '')
        movTitle = movTitle.strip()
        if ('Adult' not in movdet.text) and ('adult' not in hlinksurl):
            ItemNum = ItemNum+1
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8') })
        elif (SETTINGS_ENABLEADULT == 'true'):
            ItemNum = ItemNum+1
            Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8') })

    Paginator = soup.find(class_='wp-pagenavi')
    paginationText = ''
    try:
        currPage = Paginator.find('span', { 'class':'current'})
    except:
        currPage = ''
            
    if currPage:    
        CurrentPage = int(currPage.string)
        lasPage = Paginator.find('span', { 'class':'pages'})
        lastPage = int(re.findall('of (.*)', lasPage.string)[0])
        
        if (CurrentPage < lastPage):
            paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"


    if 'hindi-movies' in hlinksurl:
        subUrl = 'hlinkshindi'
    elif 'dubbed-movies' in hlinksurl:
        subUrl = 'hlinksdub'
    elif 'adult' in hlinksurl:
        subUrl = 'hlinksadult'
    elif 'documentaries' in hlinksurl:
        subUrl = 'hlinksdocu'
    elif '/?s=' in hlinksurl:
        subUrl = 'hlinkssearch'
        
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText + ',search_text=' + search_text})

    return Dict_movlist

def getMovList_olangal(olangalurl):
    #print "================ checking cache hit : function getMovList_olangal was called"
    Dict_movlist = {}
#            link = net.http_GET(olangalurl).content
#            soup = BeautifulSoup(link, 'html5lib')
    req = urllib2.Request(olangalurl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    soup = BeautifulSoup(link)

    for Paginator in soup.findAll("div", { "class":"paginado"}):
        currPage = Paginator.find("a", { "class":"current"})
        CurrentPage = str(currPage.contents[0].strip())

        for eachPage in Paginator.findAll("a", { "class":"page larger"}):
            if "Next" not in eachPage.contents[0]:
                lastPage = eachPage.contents[0].strip()

    if (CurrentPage < lastPage):
        paginationText = "( Currently in Page " + CurrentPage + " of " + lastPage + ")\n"
    else:
        paginationText = ""
        
    ItemNum=0
    isoup = soup.find("div", { "class":"item_1 items"})
    for eachItem in isoup.findAll("div", { "class":"item"}):
         ItemNum=ItemNum+1
         imgfullLink = eachItem.find('img')['src']
         fullLink = eachItem.find('a')['href']
         names = eachItem.find('img')['alt'].encode('utf8')
         #.encode('ascii',errors='ignore') Without this fails on olangal page 4 "Love 24x7" with utf char in title
         Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + fullLink + ', imgLink=' + imgfullLink.strip()+', MovTitle='+names.decode('utf8')})
         #print " : Adding to cache dictionary :"+names+", mode=individualmovie, url=" + fullLink
#             addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent', 'currPage': int(currPage) + 1 }, {'title': 'Next Page.. ' + paginationText})
    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=olangalMovies-Recent, currPage=' + str(int(CurrentPage) + 1) + ',title=Next Page.. ' + paginationText+', Order='+str(ItemNum)})
    return Dict_movlist

def getMovList_ABCmal(abcmalUrl):
    Dict_movlist = {}

    link = net.http_GET(abcmalUrl).content
    soup = BeautifulSoup(link)
    ItemNum=0
    for linksSection in soup.findAll(class_='itemContainer'):
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
            #print "no thumb"
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

def getMovList_ABCalt(abcaltUrl):
    Dict_movlist = {}

    req = urllib2.Request(abcaltUrl)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    soup = BeautifulSoup(link)
    lsoup = soup.find(class_='nag cf')
    ItemNum = 0
    Items = soup.find_all(class_='imgbox fpthumb shadow10d')
    #xbmc.log(msg='========== Items: ' + str(Items), level=xbmc.LOGNOTICE)
    for eachItem in Items:
        movPage = eachItem.find('a')['href']
        imgSrc = eachItem.find('img')['src']
        movTitle = (eachItem.find('img')['alt']).encode('utf8')
        movTitle = movTitle.replace('Malayalam', '')
        movTitle = movTitle.replace('Tamil', '')
        movTitle = movTitle.replace('MALAYALAM', '')
        movTitle = movTitle.replace('Movies', '')
        movTitle = movTitle.replace('Movie', '')
        movTitle = movTitle.replace('movie', '')
        movTitle = movTitle.replace('Film', '')
        movTitle = movTitle.replace('film', '')
        movTitle = movTitle.replace('New', '')
        movTitle = movTitle.replace('MOVIE', '')
        movTitle = movTitle.replace('Full', '')
        movTitle = movTitle.replace('FULL', '')
        movTitle = movTitle.replace('Length', '')
        movTitle = movTitle.replace('Glamour', '')
        movTitle = movTitle.replace('Masala', '')
        movTitle = movTitle.replace('Latest', '')
        movTitle = movTitle.replace('Romantic', '')
        movTitle = movTitle.replace('Releases', '')
        movTitle = movTitle.replace('HD', '')
        movTitle = movTitle.replace('Hot', '')
        movTitle = movTitle.replace('|', '')
        movTitle = movTitle.replace('.', '')
        movTitle = movTitle.strip()
        ItemNum = ItemNum+1
        Dict_movlist.update({ItemNum:'mode=individualmovie, url=' + movPage + ', imgLink=' + imgSrc + ', MovTitle=' + movTitle.decode('utf8') })

    Paginator = soup.find(class_='srizon-pagination hidden-phone visible-desktop')
    currPage = Paginator.find('span', { 'class':'current'})
    CurrentPage = int(currPage.string)
    
    for eachPage in Paginator.findAll('a'):
        if "Next" not in eachPage.contents[0] and "Prev" not in eachPage.contents[0]:
            lastPage = int(eachPage.string)    

    if (CurrentPage < lastPage):
        paginationText = "(Currently in Page " + str(CurrentPage) + " of " + str(lastPage) + ")\n"
    else:
        paginationText = ""

    if 'sizzling' in abcaltUrl:
        subUrl = 'ABCalt-sizzling'
    elif 'comedy' in abcaltUrl:
        subUrl = 'ABCalt-comedy'

    if paginationText:
        Dict_movlist.update({'Paginator':'mode=GetMovies, subUrl=' + subUrl + ', currPage=' + str(CurrentPage + 1) + ',title=Next Page.. ' + paginationText})
        
    return Dict_movlist

def getMovLinksForEachMov(url):

    url = addon.queries.get('url', False)
    if 'olangal.pro' in url:
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []
        videoclass = soup.find("div", { "class":"entry-content"})
        
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
                            if urlresolver.HostedMediaFile(vidurl).valid_url():
                                sources.append(hosted_media)
                            else:
                                print '    not resolvable by urlresolver!'
                else:
                    hosted_media = urlresolver.HostedMediaFile(url)
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
                if urlresolver.HostedMediaFile(url).valid_url():
                    sources.append(hosted_media)
                else:
                    print '    not resolvable by urlresolver!'
        except:
                 print 'Nothing found using method 2!'

        try:
            links = soup.find_all(class_='movieplay')
            for link in links:
                if 'hqq.tv' not in str(link):
                    url = link.find('iframe')['src']
                    hosted_media = urlresolver.HostedMediaFile(url)
                    if urlresolver.HostedMediaFile(url).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
        except:
                 print 'Nothing found using method 3!'
                
        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'mersalaayitten' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('img', False))
        movid = re.findall('video/([\\d]*)',url)[0]
        xmlurl = 'http://mersalaayitten.com/media/nuevo/econfig.php?key=' + movid
        req = urllib2.Request(xmlurl)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', 'http://mersalaayitten.com/media/nuevo/player.swf')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        soup = BeautifulSoup(link)

        try:
            movfile = soup.html5.text
            thumb = soup.thumb.text
            #xbmc.log(msg='========== Items: ' + srtfile + '\n' + movfile + '\n' + thumb, level=xbmc.LOGNOTICE)
            li = xbmcgui.ListItem(movTitle, iconImage=thumb)
            li.setArt({ 'fanart': thumb })
            li.setProperty('IsPlayable', 'true')
            try:
                srtfile = soup.captions.text
                li.setSubtitles(['special://temp/mersal.srt', srtfile])
            except:
                print "No Subtitles"
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), movfile, li)

        except:
            print "Nothing found"

    elif 'rajtamil.com' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        videoclass = soup.find(class_='entry-content')
        #xbmc.log(msg='========== Videoclass: ' + (videoclass.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
        sources = []
            
        try:
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
                    if urlresolver.HostedMediaFile(glink).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)
                else:
                    hosted_media = urlresolver.HostedMediaFile(movLink)
                    if urlresolver.HostedMediaFile(movLink).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print "no embedded urls found using iframe method"

        try:
            links = videoclass.find_all('a')
            #xbmc.log(msg = '============== links: ' + str(links), level = xbmc.LOGNOTICE)
            for alink in links:
                movLink = alink.get('href')
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
                    if urlresolver.HostedMediaFile(glink).valid_url():
                        sources.append(hosted_media)
                    else:
                        print '    not resolvable by urlresolver!'
                elif 'rajtamil' not in movLink:
                    hosted_media = urlresolver.HostedMediaFile(movLink)
                    if urlresolver.HostedMediaFile(movLink).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print "no embedded urls found using a method"
            
        try:
            links = videoclass.find_all('embed')
            for elink in links:
                movLink = elink.get('src')
                hosted_media = urlresolver.HostedMediaFile(movLink)
                if urlresolver.HostedMediaFile(movLink).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print "no embedded urls found using embed method"

        try:           
            movLink = re.findall("[\d\D]+window.open\('([^']*)", str(videoclass))[0]
            hosted_media = urlresolver.HostedMediaFile(movLink)
            if urlresolver.HostedMediaFile(movLink).valid_url():
                sources.append(hosted_media)
            else:
                xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)
        except:
            print "no embedded urls found using a method"

            
        for idx, s in enumerate(sources):
            if s.get_media_id():
                if s.get_host():
                    addon.add_video_item({'url':s.get_url(), 'img':fanarturl, 'title': movTitle, 'AddtoHist':True}, {'title': s.get_host() + ' (' + s.get_media_id() + ')'}, img=fanarturl)
            else:
                vidhost = re.findall('//(.*?)/', s.get_url())[0]
                vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
                addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'cinebix.com' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []
        
        try:
            links = soup.find_all('iframe')
            for plink in links:
                movLink = plink.get('src')
                hosted_media = urlresolver.HostedMediaFile(movLink)
                if urlresolver.HostedMediaFile(movLink).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print " : no embedded urls found using wrapper method"
            
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'youtube.com' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        sources = []

        try:
            hosted_media = urlresolver.HostedMediaFile(url)
            if urlresolver.HostedMediaFile(url).valid_url():
                sources.append(hosted_media)
            else:
                xbmc.log(msg = url + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print " : no embedded urls found using wrapper method"
            
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)     
            
    elif 'tamilgun.com' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []
        
        try:
            videoclass = soup.find("div", { "class":"videoWrapper player"})
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
                    if urlresolver.HostedMediaFile(glink).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg = glink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)
                else:
                    hosted_media = urlresolver.HostedMediaFile(movLink)
                    if urlresolver.HostedMediaFile(movLink).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

        except:
            print " : no embedded urls found using wrapper method"

        try:
            videoclass = soup.find("div", { "class":"post-entry" })
            plinks = videoclass.find_all('p')
            for plink in plinks:
                try:
                    movLink = plink.iframe.get('src')
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
                        if urlresolver.HostedMediaFile(glink).valid_url():
                            sources.append(hosted_media)
                        else:
                            xbmc.log(msg = glink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)
                    else:
                        hosted_media = urlresolver.HostedMediaFile(movLink)
                        if urlresolver.HostedMediaFile(movLink).valid_url():
                            sources.append(hosted_media)
                        else:
                            xbmc.log(msg = movLink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

                except:
                    print " : no embedded urls found using postentry method"

        except:
            print " : no embedded urls found using post entry iframe method"

        try:
            videoclass = soup.find("div", { "class":"post-entry" })
            plinks = videoclass.find_all('p')
            for plink in plinks:
                try:
                    movLink = plink.a.get('href')
                    if 'tamildbox' in movLink:
                        dlink = net.http_GET(movLink).content
                        dsoup = BeautifulSoup(dlink)
                        
                        dclass = dsoup.find("div", { "id":"player-embed" })
                        if 'unescape' in str(dclass):
                            etext = re.findall("unescape.'[^']*", str(dclass))[0]
                            etext = urllib.unquote(etext)
                            dclass = BeautifulSoup(etext)
                        glink = dclass.iframe.get('src')
                        hosted_media = urlresolver.HostedMediaFile(glink)
                        if urlresolver.HostedMediaFile(glink).valid_url():
                            sources.append(hosted_media)
                        else:
                            xbmc.log(msg = glink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)
                        
                        dclass = dsoup.find(class_='item-content')
                        glink = dclass.p.iframe.get('src')
                        hosted_media = urlresolver.HostedMediaFile(glink)
                        if urlresolver.HostedMediaFile(glink).valid_url():
                            sources.append(hosted_media)
                        else:
                            xbmc.log(msg = glink + ' not resolvable by urlresolver!', level = xbmc.LOGNOTICE)

                except:
                    print " : no embedded urls found using postentry method"
                            
        except:
            print " : no embedded urls found using post entry a method"

        try:
            jlink = re.findall('sources:.*file":"([^"]*)', link)[0]
            elink = jlink.replace('\\/', '/')
            if ('tamilgun' in elink) or ('m3u8' in elink):
                li = xbmcgui.ListItem('tamilgun.com', iconImage=fanarturl)
                li.setArt({ 'fanart': fanarturl })
                li.setProperty('IsPlayable', 'true')
                elink += '|Referer=http://tamilgun.com'
                xbmcplugin.addDirectoryItem(int(sys.argv[1]), elink, li)
            else:
                print '    not resolvable by urlresolver!'

        except:
            print " : no embedded urls found using embed method"
            
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'filmlinks4u.to' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        lsoup = soup.find(class_='post-single-content box mark-links')
        #xbmc.log(msg='========== Lsoup: ' + (lsoup.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
        sources = []
        itemdetails = lsoup.findAll('p')
        #xbmc.log(msg='========== Itemdet: ' + str(itemdetails), level=xbmc.LOGNOTICE)
        cleanmov = True
        for eachdetail in itemdetails:
            if 'Adult' in str(eachdetail):
                cleanmov = False
        #xbmc.log(msg='==========cleanmov: ' + str(cleanmov) + ' adult setting:' + SETTINGS_ENABLEADULT, level=xbmc.LOGNOTICE)
        
        try:
            ilink = lsoup.find("iframe")
            vidurl = ilink.get('src')
            if cleanmov:
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
            elif SETTINGS_ENABLEADULT == 'true':
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)

        except:
            print " : no embedded urls found using iframe method"
        
        try:
            blink = re.findall("ajaxurl = '(.*?)'", link)[0]
            postid = re.findall("'post_id':'(.*?)'", link)[0]
            values = {'action' : 'create_player_box',
                      'post_id' : postid }
            header = {'Referer' : 'http://www.filmlinks4u.to/',
                      'X-Requested-With' : 'XMLHttpRequest'}
            playbox = net.http_POST(blink, values, header).content
            psoup = BeautifulSoup(playbox)
            #xbmc.log(msg='========== Psoup: ' + (psoup.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
            tsoup = psoup.find(class_='tabs')
            tabs = tsoup.findAll('div')
            #xbmc.log(msg='========== Tabs: ' + str(tabs), level=xbmc.LOGNOTICE)
            for eachtab in tabs:
                vidurl = re.findall('data-href="(.*?)"', str(eachtab))[0]
                if cleanmov:
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                elif SETTINGS_ENABLEADULT == 'true':
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)

        except:
            print " : no embedded urls found using player_box method"
            
        try:
            links = lsoup.findAll(class_='external')
            #xbmc.log(msg='========== Items: ' + str(links), level=xbmc.LOGNOTICE)
            for plink in links:
                url = re.findall('href="(.*?)"', str(plink))[0]
                #xbmc.log(msg='========== Item: ' + str(url), level=xbmc.LOGNOTICE)
                if ('cineview' in url) or ('bollyheaven' in url) or ('videolinkz' in url):
                    clink = net.http_GET(url).content
                    csoup = BeautifulSoup(clink)
                    try:
                        for linksSection in csoup.findAll('iframe'):
                            vidurl = linksSection.get('src')
                            if ('desihome.co' not in vidurl) and ('cineview' not in vidurl) and ('bollyheaven' not in vidurl) and ('videolinkz' not in vidurl):
                                if cleanmov:
                                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                                        sources.append(hosted_media)
                                    else:
                                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                                elif SETTINGS_ENABLEADULT == 'true':
                                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                                        sources.append(hosted_media)
                                    else:
                                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                    except:
                        print " : no iframe urls found using cineview method"
                    try:
                        for linksSection in csoup.findAll('embed'):
                            vidurl = linksSection.get('src')
                            if ('desihome.co' not in vidurl) and ('cineview' not in vidurl) and ('bollyheaven' not in vidurl) and ('videolinkz' not in vidurl):
                                if cleanmov:
                                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                                        sources.append(hosted_media)
                                    else:
                                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                                elif SETTINGS_ENABLEADULT == 'true':
                                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                                        sources.append(hosted_media)
                                    else:
                                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                    except:
                        print " : no embed urls found using cineview method"
                        
                else:
                    if ('imdb.com' not in url) and ('mgid.com' not in url) and ('desihome' not in url):
                        if cleanmov:
                            hosted_media = urlresolver.HostedMediaFile(url)
                            if urlresolver.HostedMediaFile(url).valid_url():
                                sources.append(hosted_media)
                            else:
                                xbmc.log(msg='========> src: ' + url + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                        elif SETTINGS_ENABLEADULT == 'true':
                            hosted_media = urlresolver.HostedMediaFile(url)
                            if urlresolver.HostedMediaFile(url).valid_url():
                                sources.append(hosted_media)
                            else:
                                xbmc.log(msg='========> src: ' + url + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                
        except:
            print " : no embedded urls found using cineview method"
            
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'hindilinks4u.to' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []

        try:
            linksDiv = soup.find(class_='screen fluid-width-video-wrapper')
            try:
                vidurl = str(linksDiv.find('iframe')['src'])
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
            except:
                     print 'Nothing found using method 1!'
            try:
                vidtab = (re.findall('prepend\( "(.*?)" \)', str(linksDiv))[0]).replace('\\', '')
                vsoup = BeautifulSoup(vidtab)
                #xbmc.log(msg='==== vsoup: \n' + (vsoup.prettify().encode('utf-8')), level=xbmc.LOGNOTICE)
                vtabs = vsoup.find_all('span')
                #vtabs = vsoup.find_all(lambda tag: tag.name == 'span' and 'src' in tag.attrs)
                #xbmc.log(msg='==== vtabs: \n' + str(vtabs), level=xbmc.LOGNOTICE)
                for vtab in vtabs:
                    vidurl = vtab['data-href']
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
            except:
                     print 'Nothing found using method 1!'
        except:
                 print 'Nothing found using method 1!'

        try:
            linksDiv = soup.find(class_='entry-content rich-content')
            links = linksDiv.find_all('a')
            for link in links:
                vidurl = link.get('href').strip()
                if 'filmshowonline.net/media/' in vidurl:
                    clink = net.http_GET(vidurl).content
                    eurl = re.findall("url: '([^']*)[\d\D]*nonce :", clink)[0]
                    enonce = re.findall("nonce : '([^']*)", clink)[0]
                    evid = re.findall("nonce : [\d\D]*?link_id: ([\d]*)", clink)[0]
                    values = {'echo' : 'true',
                              'nonce' : enonce,
                              'width' : '848',
                              'height' : '480',
                              'link_id' : evid }
                    emurl = net.http_POST(eurl, values).content
                    strurl = (re.findall('(http[^"]*)', emurl)[0]).replace('\\', '')
                    hosted_media = urlresolver.HostedMediaFile(strurl)
                    if urlresolver.HostedMediaFile(strurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + strurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)

                elif 'filmshowonline.net/videos/' in vidurl:
                    clink = net.http_GET(vidurl).content
                    csoup = BeautifulSoup(clink)
                    strurl = csoup.find('iframe')['src']
                    hosted_media = urlresolver.HostedMediaFile(strurl)
                    if urlresolver.HostedMediaFile(strurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + strurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                        
                else:
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
        except:
                 print 'Nothing found using method 2!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'firsttube.co' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('fanarturl', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []

        try:
            linksDiv = soup.find(class_='entry')
            links = linksDiv.find_all('a')
            for link in links:
                vidurl = re.findall('(?:http://adf\.ly/\d+/)?(.*)', (link.get('href').strip()))[0]
                if 'playtube.' in vidurl:
                    clink = net.http_GET(vidurl).content
                    csoup = BeautifulSoup(clink)
                    strurl = csoup.find('iframe')['src']
                    if 'docs.google.com' in strurl:
                        glink = net.http_GET(strurl).content
                        strurl = (re.findall('"fmt_stream_map.*?(http[^|]*)', glink)[0]).replace('\\u0026', '&').replace('\\u003d', '=')
                        li = xbmcgui.ListItem('docs.google.com', iconImage=fanarturl)
                        li.setArt({ 'fanart': fanarturl })
                        li.setProperty('IsPlayable', 'true')
                        xbmcplugin.addDirectoryItem(int(sys.argv[1]), strurl, li)                        
                    else:
                        hosted_media = urlresolver.HostedMediaFile(strurl)
                        if urlresolver.HostedMediaFile(strurl).valid_url():
                            sources.append(hosted_media)
                        else:
                            xbmc.log(msg='========> src: ' + strurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
                        
                elif 'firsttube.co' not in vidurl:
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg='========> src: ' + vidurl + ' not resolvable by urlresolver!', level=xbmc.LOGNOTICE)
        except:
                 print 'Nothing found using method entry!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'thiruttuvcd.me' in url:
        url = addon.queries.get('url', False)
        subUrl = addon.queries.get('subUrl', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('img', False))
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
                if ('magnet' not in vidurl) and ('thiruttuvcd' not in vidurl):
                    hosted_media = urlresolver.HostedMediaFile(vidurl)
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        xbmc.log(msg=vidurl + ' is NOT resolvable by urlresolver!', level=xbmc.LOGNOTICE)
        except:
                 print 'Nothing found using method 1!'

        try:
            links = soup.find_all('iframe')
            for link in links:
                vidurl = link.get("data-lazy-src")
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg=vidurl + ' is NOT resolvable by urlresolver!', level=xbmc.LOGNOTICE)
        except:
                 print 'Nothing found using method 2!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            #xbmc.log(msg='========== vidhost: ' + s.get_url(), level=xbmc.LOGNOTICE)
            vidhost = s.get_url()
            vidhost = re.findall('//(.*?)/', vidhost)[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'thiruttuvcds' in url:
        url = addon.queries.get('url', False)
        subUrl = addon.queries.get('subUrl', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('img', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link,'html.parser')
        sources = []

        try:
            linksDiv = soup.find("div", { "class":"videosection" })
            links = linksDiv.find_all('iframe')			
            for link in links:
                vidurl = link.get('src').strip()
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    xbmc.log(msg=vidurl + ' is NOT resolvable by urlresolver!', level=xbmc.LOGNOTICE)
        except:
                 print 'Nothing found using youtube method!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)

    elif 'thiruttumasala' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('img', False))
        #print ' current movie url : ' + url
        #print ' current movie fanarturl : ' + fanarturl
        #print ' current movie title : ' + movTitle
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()

        soup = BeautifulSoup(link)
        #print soup.prettify()
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
                #print 'BLAAA found link =' + link

                req = urllib2.Request(link)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(req)
                link = response.read()
                response.close()

                soup = BeautifulSoup(link)

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
                # #print "("+httpurl1+")"+"\n"
                httpurl1 = httpurl1.replace('config.php', 'playlist.php')
                req = urllib2.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
                response = urllib2.urlopen(httpurl1)
                link = response.read()
                response.close()

                soup = BeautifulSoup(link)
                li = xbmcgui.ListItem(movTitle, iconImage=soup.find('thumb').text.strip())
                li.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(int(sys.argv[1]), soup.find('file').text, li)
        except:
            print "Nothing found using method 2"

    elif 'abcmalayalam.com' in url:
        url = addon.queries.get('url', False)
        movTitle = str(addon.queries.get('title', False))
        fanarturl = str(addon.queries.get('img', False))
        link = net.http_GET(url).content
        soup = BeautifulSoup(link)
        sources = []

        try:
            linksDiv = soup.find(class_='itemFullText')
            # most pages have a trailer embebbed. Lets include that too
            for linksSection in linksDiv.findAll(class_='avPlayerWrapper avVideo'):
                vidurl = str(linksSection.find('iframe')['src'])
                hosted_media = urlresolver.HostedMediaFile(vidurl)
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
                    if urlresolver.HostedMediaFile(vidurl).valid_url():
                        sources.append(hosted_media)
                    else:
                        print vidurl + ' is NOT resolvable by urlresolver!'
        except:
                 print 'Nothing found using method 2!'

        try:
            linksDiv = soup.find(class_='itemIntroText')
            # some pages have a intro. Lets include that too
            for linksSection in linksDiv.findAll(class_='avPlayerWrapper avVideo'):
                vidurl = str(linksSection.find('iframe')['src'])
                hosted_media = urlresolver.HostedMediaFile(vidurl)
                if urlresolver.HostedMediaFile(vidurl).valid_url():
                    sources.append(hosted_media)
                else:
                    print '    not resolvable by urlresolver!'
        except:
                 print 'Nothing found using method 3!'

        sources = urlresolver.filter_source_list(sources)
        for idx, s in enumerate(sources):
            vidhost = re.findall('//(.*?)/', s.get_url())[0]
            vidhost = re.findall('(?:.*\.|)(.*\..+)', vidhost)[0]
            addon.add_video_item({'url': s.get_url()},{'title': vidhost},img=fanarturl,fanart=fanarturl)
                
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

CurrUrl=str(addon.queries.get('url', False))
if ALLOW_HIT_CTR == 'true':
    if CurrUrl != False:
        tracker.track_pageview(Page("/"+str(CurrUrl)), session, visitor)
if play:

    try:
        if "True" in addon.queries.get('AddtoHist', False):
            with open(RootDir + "/history.dat", 'a') as target:
                target.write("title=" + str(addon.queries.get('title', False)) + ', host=' + str(addon.queries.get('host', False)) + ', media_id=' + str(addon.queries.get('media_id', False)) + ', img=' + str(addon.queries.get('img', False)) + '\r\n')
    except:
        print "not adding to watch history"
    url = addon.queries.get('url', '')
    host = addon.queries.get('host', '')
    media_id = addon.queries.get('media_id', '')
   
    if url:
        stream_url = urlresolver.HostedMediaFile(url).resolve()
    else:
        stream_url = urlresolver.HostedMediaFile(host=host, media_id=media_id).resolve()

    addon.resolve_url(stream_url)

elif mode == 'resolver_settings':
    urlresolver.display_settings()


elif mode == 'individualmovie':
    url = addon.queries.get('url', False)
    getMovLinksForEachMov(url)


elif 'Worship' in mode:

        if mode == 'Worship Songs':
            worshipUrl= urllib2.urlopen(Private_WorshipSongs_XML)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Worship/Songs'), session, visitor)
        elif mode == 'Worship Messages':
            worshipUrl= urllib2.urlopen(Private_WorshipMessages_XML)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Worship/Messages'), session, visitor)

        DOMTree = xml.dom.minidom.parse(worshipUrl)
        collection = DOMTree.documentElement
        if collection.hasAttribute("shelf"):
           print "Root element : %s" % collection.getAttribute("shelf")
        
        # Get all the movies in the collection
        movies = collection.getElementsByTagName("movie")

        for movie in movies:

           if movie.hasAttribute("title"):
              WorshipItem_title=unicode(movie.getAttribute("title"))
              WorshipItem_url=get_tag_value(movie.getElementsByTagName('url')[0])
              WorshipItem_img=get_tag_value(movie.getElementsByTagName('img')[0])
              addon.add_video_item({'url': WorshipItem_url},{'title': WorshipItem_title},img=WorshipItem_img)

              
elif mode == 'GetMovies':
    dlg = xbmcgui.DialogProgress()
    dlg.create("Malabar Talkies", "Fetching movies and caching...\nWill be faster next time")
    dlg.update(0)
    subUrl = addon.queries.get('subUrl', False)
    mode = addon.queries.get('mode', False)
    Url = addon.queries.get('Url', False)

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

        Dict_res = cache.cacheFunction(getMovList_ABCmal, abcmalUrl)
            
        keylist = Dict_res.keys()
        keylist.sort()
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
#                   #print "<<< creating directory for " + key + "img=" + IMGfullLink_Str

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
                #print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
        except:
            print "No pagination found"

    if 'ABCalt' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        if subUrl == 'ABCalt-sizzling':
            abcaltUrl = base_url +  '/sizzling?jut1=' + str(currPage)
        elif subUrl == 'ABCalt-comedy':
            abcaltUrl = base_url + '/comedy?jut1=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/ABCMalayalam/Comedy'), session, visitor)

        Dict_res = cache.cacheFunction(getMovList_ABCalt, abcaltUrl)
            
        keylist = Dict_res.keys()
        keylist.sort()
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
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                #print " SETTING FOR NEXT LINK: " + mode_Str + ', ' + currPage_Str + ', ' + title_Str
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str }, {'title': title_Str})
        except:
            print "No Pagination found"

    elif 'olangalMovies-Recent' in subUrl:
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Olangal'), session, visitor)
            currPage = addon.queries.get('currPage', False)
            if not currPage:
                currPage = 1
            olangalurl = 'http://olangal.pro/page/' + str(currPage)
            Dict_res = cache.cacheFunction(getMovList_olangal, olangalurl)
            
            keylist = Dict_res.keys()
            keylist.sort()
    
            for key, value in Dict_res.iteritems():
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
                            MovTitle_Str = str(eachSplitVal.encode('utf8').replace('MovTitle=', '')).strip()
                    if MovTitle_Str:
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
                    #print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
            except:
                print "No Pagination found"

    elif ('thiruttuvcd' in subUrl) and ('MP3' not in subUrl):
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''

        if 'thiruttuvcd_masala' in subUrl:
            thiruttuvcd_url = 'http://www.thiruttumasala.com/videos?o=mr&page=' + str(currPage)
        elif 'thiruttuvcd_MalayalamMovs' in subUrl:
            thiruttuvcd_url = 'http://www.thiruttuvcd.me/category/malayalam/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/ThiruttuVcd/Malayalam'), session, visitor)          
        elif 'thiruttuvcd_adult' in subUrl:
            thiruttuvcd_url = 'http://thiruttuvcds.com/private/page/' + str(currPage) + '/'
        elif 'thiruttuvcd_tamilMovs' in subUrl:
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
        elif 'thiruttuvcd_search' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('ThiruttuVCD')
                search_text = search_text.replace(' ', '+')
            thiruttuvcd_url = 'http://www.thiruttuvcd.me/page/' + str(currPage) + '/?s=' + search_text

        cache.delete("%")
        Dict_res = cache.cacheFunction(getMovList_thiruttuvcd, thiruttuvcd_url)
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

                    elif 'MovTitle' in eachSplitVal:
                        MovTitle_Str = str(eachSplitVal.replace('MovTitle=', '')).strip()  
                if MovTitle_Str:
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})                #print " : adding NEW next page, mode=" + mode_Str + ', subUrl=' + subUrl_Str + ', currPage=' + currPage_Str + ',title=' + title_Str
        except:
            print "No Pagination found"

    elif 'rajtamil' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''
            
        if 'rajtamildubbed' in subUrl:
            rajTamilurl = 'http://www.rajtamil.com/category/tamil-dubbed/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil/TamilDubbed'), session, visitor)
        elif 'rajtamilcomedy' in subUrl:
            rajTamilurl = 'http://www.rajtamil.com/category/comedy/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil/TamilComedy'), session, visitor)
        elif 'rajtamilsongs' in subUrl:
            rajTamilurl = 'http://www.rajtamil.com/category/download-songs/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil/TamilSongs'), session, visitor)
        elif 'rajtamilTVshowsVijayTV' in subUrl:
            rajTamilurl = 'http://www.rajtamil.com/category/vijay-tv-shows/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil/TVshowsVijayTV'), session, visitor)
        elif 'rajtamilTVshowsSunTV' in subUrl:
            rajTamilurl = 'http://www.rajtamil.com/category/sun-tv-show/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil/TVshowsSunTV'), session, visitor)
        elif 'rajtamilsearch' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('RajTamil')
                search_text = search_text.replace(' ', '+')
            rajTamilurl = 'http://www.rajtamil.com/page/' + str(currPage) + '/?s=' + search_text
        else:
            rajTamilurl = 'http://www.rajtamil.com/category/movies/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Rajtamil'), session, visitor)

        Dict_res = cache.cacheFunction(getMovList_rajtamil, rajTamilurl)
       
        keylist = Dict_res.keys()
        keylist.sort()
        
        for key, value in Dict_res.iteritems():
            if 'Paginator' not in value:
                SplitValues = value.split(",")
                mode_Str=""
                fullLink_Str=""
                fanarturl_Str=""
                MovTitle_Str=""                    
                try:
                    for eachSplitVal in SplitValues:
                        #eachSplitVal = eachSplitVal.encode('utf8')
                        if 'mode' in eachSplitVal:
                            mode_Str = str(eachSplitVal.replace('mode=', '')).strip()
                        elif 'url' in eachSplitVal:
                            fullLink_Str = str(eachSplitVal.replace('url=', '')).strip()
                        elif 'imgLink' in eachSplitVal:
                            fanarturl_Str = str(eachSplitVal.replace('imgLink=', '')).strip()
                        elif 'MovTitle' in eachSplitVal:
                            MovTitle_Str = str(eachSplitVal.encode('utf8').replace('MovTitle=', '')).strip()
                
                    if MovTitle_Str:
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})

        except:
            print "No Pagination found"

    elif 'tamilgun' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''

        if 'tamilgunnew' in subUrl:
            tamilgunurl = 'http://tamilgun.com/categories/new-movies/page/' + str(currPage) + '/?order=latest'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/TamilGun/NewMovies'), session, visitor)
        elif 'tamilgundubbed' in subUrl:
            tamilgunurl = 'http://tamilgun.com/categories/dubbed-movies/page/' + str(currPage) + '/?order=latest'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/TamilGun/TamilDubbed'), session, visitor)
        elif 'tamilgunhd' in subUrl:
            tamilgunurl = 'http://tamilgun.com/categories/hd-movies/page/' + str(currPage) + '/?order=latest'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/TamilGun/HDMovies'), session, visitor)
        elif 'tamilguncomedy' in subUrl:
            tamilgunurl = 'http://tamilgun.com/categories/hd-comedys/page/' + str(currPage) + '/?order=latest'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/TamilGun/Comedy'), session, visitor)
        elif 'tamilguntrailer' in subUrl:
            tamilgunurl = 'http://tamilgun.com/categories/trailers/page/' + str(currPage) + '/?order=latest'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/TamilGun/Trailers'), session, visitor)
        elif 'tamilgunsearch' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('TamilGun')
                search_text = search_text.replace(' ', '+')
            tamilgunurl = 'http://tamilgun.com/page/' + str(currPage) + '/?s=' + search_text

        Dict_res = cache.cacheFunction(getMovList_tamilgun, tamilgunurl)

        keylist = Dict_res.keys()
        keylist.sort()
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
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})
        except:
            print "No Pagination found"

    elif 'flinks' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''

        if 'flinkstamil' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/tamil/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Tamil'), session, visitor)
        elif 'flinksmalayalam' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/malayalam/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Malayalam'), session, visitor)
        elif 'flinkstelugu' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/telugu/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Telugu'), session, visitor)
        elif 'flinkshindisc' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/adult-hindi-short-films/page/' + str(currPage) + '?orderby=date'
        elif 'flinkshindi' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/hindi/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Hindi'), session, visitor)
        elif 'flinkskannada' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/kannada/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Kannada'), session, visitor)
        elif 'flinksadult' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/adult/page/' + str(currPage) + '?orderby=date'
        elif 'flinksani' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/animation/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Animation'), session, visitor)
        elif 'flinksholly' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/hollywood/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Hollywood'), session, visitor)
        elif 'flinksben' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/bengali/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Bengali'), session, visitor)
        elif 'flinksbhoj' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/bhojpuri/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Bhojpuri'), session, visitor)
        elif 'flinksbio' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/biography/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Biography'), session, visitor)
        elif 'flinksdocu' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/documentary/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Documentary'), session, visitor)
        elif 'flinksguj' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/gujarati/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Gujarati'), session, visitor)
        elif 'flinksmar' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/marathi/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Marathi'), session, visitor)
        elif 'flinksnep' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/others/nepali/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Nepali'), session, visitor)
        elif 'flinksori' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/others/oriya/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Oriya'), session, visitor)
        elif 'flinkspun' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/punjabi/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Punjabi'), session, visitor)
        elif 'flinksraj' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/others/rajasthani/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Rajasthani'), session, visitor)
        elif 'flinksurdu' in subUrl:
            flinksurl = 'http://www.filmlinks4u.to/category/others/urdu/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FilmLinks4U/Urdu'), session, visitor)
        elif 'flinkssearch' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('FilmLinks4U')
                search_text = search_text.replace(' ', '+')
            flinksurl = 'http://www.filmlinks4u.to/page/' + str(currPage) + '/?s=' + search_text
            
        Dict_res = cache.cacheFunction(getMovList_flinks, flinksurl)

        keylist = Dict_res.keys()
        keylist.sort()
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
                            MovTitle_Str = str(eachSplitVal.encode('utf8').replace('MovTitle=', '')).strip()
                
                    if MovTitle_Str:
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})

        except:
            print "No Pagination found"

    elif 'hlinks' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''
            
        if 'hlinkshindi' in subUrl:
            hlinksurl = 'http://www.hindilinks4u.to/category/hindi-movies/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/HindiLinks4U/Hindi'), session, visitor)
        elif 'hlinksdub' in subUrl:
            hlinksurl = 'http://www.hindilinks4u.to/category/dubbed-movies/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/HindiLinks4U/Dubbed'), session, visitor)
        elif 'hlinksadult' in subUrl:
            hlinksurl = 'http://www.hindilinks4u.to/category/adult/page/' + str(currPage) + '?orderby=date'
        elif 'hlinksdocu' in subUrl:
            hlinksurl = 'http://www.hindilinks4u.to/category/documentaries/page/' + str(currPage) + '?orderby=date'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/HindiLinks4U/Documentary'), session, visitor)
        elif 'hlinkssearch' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('HindiLinks4U')
                search_text = search_text.replace(' ', '+')
            hlinksurl = 'http://www.hindilinks4u.to/page/' + str(currPage) + '/?s=' + search_text
            
        Dict_res = cache.cacheFunction(getMovList_hlinks, hlinksurl)

        keylist = Dict_res.keys()
        keylist.sort()
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
                            MovTitle_Str = str(eachSplitVal.encode('utf8').replace('MovTitle=', '')).strip()
                
                    if MovTitle_Str:
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})
        except:
            print "No Pagination found"

    elif 'mersal' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''
            
        if 'mersal_Tamil' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=1&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Tamil'), session, visitor)
        elif 'mersal_Telugu' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=3&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Telugu'), session, visitor)
        elif 'mersal_Hindi' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=2&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Hindi'), session, visitor)
        elif 'mersal_Malayalam' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=4&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Malayalam'), session, visitor)
        elif 'mersal_Dubbed' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=6&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Dubbed'), session, visitor)
        elif 'mersal_Animation' in subUrl:
            mersalurl = 'http://mersalaayitten.com/videos?c=5&o=mr&page=' + str(currPage)
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/Mersal/Animation'), session, visitor)
        elif 'mersal_search' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('Mersalaayitten')
                search_text = search_text.replace(' ', '+')
            mersalurl = 'http://mersalaayitten.com/search?search_type=videos&search_query=' + search_text + '&page=' + str(currPage)

        Dict_res = cache.cacheFunction(getMovList_mersal, mersalurl)

        keylist = Dict_res.keys()
        keylist.sort()
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
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})

        except:
            print "No Pagination found"

    elif 'ftube' in subUrl:
        currPage = addon.queries.get('currPage', False)
        if not currPage:
            currPage = 1
        search_text = addon.queries.get('search_text', False)
        if not search_text:
            search_text = ''
            
        if 'ftube_Tamil' in subUrl:
            ftubeurl = 'http://firsttube.co/category/latest-tamil-movie/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FirstTube/Tamil'), session, visitor)
        elif 'ftube_Telugu' in subUrl:
            ftubeurl = 'http://firsttube.co/category/latest-telugu-movie/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FirstTube/Telugu'), session, visitor)
        elif 'ftube_Hindi' in subUrl:
            ftubeurl = 'http://firsttube.co/category/hindi-latest-movie/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FirstTube/Hindi'), session, visitor)
        elif 'ftube_Dubbed' in subUrl:
            ftubeurl = 'http://firsttube.co/category/hindi-dubbed/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FirstTube/Dubbed'), session, visitor)
        elif 'ftube_Punjabi' in subUrl:
            ftubeurl = 'http://firsttube.co/category/latest-punjabi-movie/page/' + str(currPage) + '/'
            if ALLOW_HIT_CTR == 'true':
                tracker.track_pageview(Page('/FirstTube/Punjabi'), session, visitor)
        elif 'ftube_search' in subUrl:
            if currPage == 1:
                search_text = GetSearchQuery('FirstTube')
                search_text = search_text.replace(' ', '+')
            ftubeurl = 'http://firsttube.co/page/' + str(currPage) + '/?s=' + search_text
            
        Dict_res = cache.cacheFunction(getMovList_ftube, ftubeurl)

        keylist = Dict_res.keys()
        keylist.sort()
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
                        addon.add_directory({'mode': mode_Str, 'url': fullLink_Str, 'fanarturl': fanarturl_Str , 'title': MovTitle_Str}, {'title': MovTitle_Str}, img=fanarturl_Str)
                except:
                    print "No likely exception caught"                        
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
                    elif 'search_text' in eachSplitVal:
                        search_Str = str(eachSplitVal.replace('search_text=', '')).strip()
                addon.add_directory({'mode': mode_Str, 'subUrl': subUrl_Str, 'currPage': currPage_Str, 'search_text': search_Str }, {'title': title_Str})

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
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCMalayalam-shortFilm'}, {'title': 'Malayalam Short Films'})
    #addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCalt-comedy'}, {'title': 'Malayalam Comedy'})
    #if SETTINGS_ENABLEADULT == 'true':
    #    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ABCalt-sizzling'}, {'title': 'Sizzling (18+)'})

elif mode == 'rajTamil':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Rajtamil_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilRecent'}, {'title': 'Tamil Recent Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamildubbed'}, {'title': 'Tamil Dubbed Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilcomedy'}, {'title': 'Tamil Movie Comedy Scenes'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilsongs'}, {'title': 'Tamil Movie Songs'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsSunTV'}, {'title': 'TV Shows - Sun TV'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilTVshowsVijayTV'}, {'title': 'TV Shows - Vijay TV'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'rajtamilsearch'}, {'title': 'Search'})

elif mode == 'tamilgun':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/TamilGun_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilgunnew'}, {'title': 'Tamil New Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilgunhd'}, {'title': 'Tamil HD Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilgundubbed'}, {'title': 'Tamil Dubbed Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilguncomedy'}, {'title': 'Tamil Movie Comedy Scenes'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilguntrailer'}, {'title': 'Tamil Movie Trailers'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'tamilgunsearch'}, {'title': 'Search'})

elif mode == 'flinks':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/FilmLinks4U'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkstamil'}, {'title': 'Tamil Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksmalayalam'}, {'title': 'Malayalam Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkstelugu'}, {'title': 'Telugu Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkshindi'}, {'title': 'Hindi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkskannada'}, {'title': 'Kannada Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksani'}, {'title': 'Animation Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksholly'}, {'title': 'Hollywood Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksbio'}, {'title': 'Biography Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksdocu'}, {'title': 'Documentary Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksben'}, {'title': 'Bengali Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksbhoj'}, {'title': 'Bhojpuri Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksguj'}, {'title': 'Gujarati Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksmar'}, {'title': 'Marathi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksnep'}, {'title': 'Nepali Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksori'}, {'title': 'Oriya Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkspun'}, {'title': 'Punjabi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksraj'}, {'title': 'Rajasthani Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksurdu'}, {'title': 'Urdu Movies'})
    if SETTINGS_ENABLEADULT == 'true':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinksadult'}, {'title': 'Adult Movies'})
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkshindisc'}, {'title': 'Hindi Softcore'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'flinkssearch'}, {'title': 'Search'})

elif mode == 'hlinks':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/HindiLinks4U'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'hlinkshindi'}, {'title': 'Hindi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'hlinksdub'}, {'title': 'Dubbed Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'hlinksdocu'}, {'title': 'Documentary Movies'})
    if SETTINGS_ENABLEADULT == 'true':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'hlinksadult'}, {'title': 'Adult Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'hlinkssearch'}, {'title': 'Search'})

elif mode == 'thiruttuvcd':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Thiruttuvcd_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_MalayalamMovs'}, {'title': 'Malayalam Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_tamilMovs'}, {'title': 'Tamil Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_teluguMovs'}, {'title': 'Telugu Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_hindiMovs'}, {'title': 'Hindi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_search'}, {'title': 'Search'})
    if SETTINGS_ENABLEADULT == 'true':
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_adult'}, {'title': 'Adult Movies'})
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'thiruttuvcd_masala'}, {'title': 'Thiruttu Masala'})

elif mode == 'mersal':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Mersal_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Tamil'}, {'title': 'Tamil Movies'})        
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Telugu'}, {'title': 'Telugu Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Hindi'}, {'title': 'Hindi Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Malayalam'}, {'title': 'Malayalam Movies'})  
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Dubbed'}, {'title': 'Dubbed Movies'})    
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_Animation'}, {'title': 'Animation Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'mersal_search'}, {'title': 'Search'})

elif mode == 'ftube':
    if ALLOW_HIT_CTR == 'true':
        tracker.track_pageview(Page('/Mersal_Main'), session, visitor)
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_Tamil'}, {'title': 'Tamil Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_Telugu'}, {'title': 'Telugu Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_Hindi'}, {'title': 'Hindi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_Dubbed'}, {'title': 'Hindi Dubbed Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_Punjabi'}, {'title': 'Punjabi Movies'})
    addon.add_directory({'mode': 'GetMovies', 'subUrl': 'ftube_search'}, {'title': 'Search'})

elif mode == 'main':
        addon.add_directory({'mode': 'abcmalayalam'}, {'title': 'ABCMalayalam : Malayalam'})
        addon.add_directory({'mode': 'flinks'}, {'title': 'FilmLinks4U : Various'})
        addon.add_directory({'mode': 'ftube'}, {'title': 'FirstTube : Hindi, Tamil, Telugu, Punjabi'})
        addon.add_directory({'mode': 'hlinks'}, {'title': 'HindiLinks4U : Hindi'})
        addon.add_directory({'mode': 'mersal'}, {'title': 'Mersalaayitten : Malayalam, Tamil, Telugu, Hindi'})
        addon.add_directory({'mode': 'GetMovies', 'subUrl': 'olangalMovies-Recent'}, {'title':'Olangal : Malayalam'})
        addon.add_directory({'mode': 'rajTamil'}, {'title': 'RajTamil : Tamil'})
        addon.add_directory({'mode': 'tamilgun'}, {'title': 'TamilGun : Tamil'})
        addon.add_directory({'mode': 'thiruttuvcd'}, {'title': 'Thiruttu VCD : Malayalam, Tamil, Telugu, Hindi'})
        addon.add_directory({'mode': 'Worship Songs'}, {'title': '[COLOR yellow]+ Worship Songs+[/COLOR]'})
        addon.add_directory({'mode': 'Worship Messages'}, {'title': '[COLOR yellow]+ Worship Messages+[/COLOR]'})
        addon.add_directory({'mode': 'PublicPlaylists'}, {'title': '[COLOR green]User submitted content[/COLOR]'})

#         addon.add_directory({'mode': 'ViewFavorites'}, {'title': 'Favorites'}, img=img_path + '/favorites.PNG')
#         addon.add_directory({'mode': 'ViewHistory'}, {'title': 'History'})
        if ALLOW_HIT_CTR == 'true':
            tracker.track_pageview(Page('/Main'), session, visitor)

if not play:
    addon.end_of_directory()
