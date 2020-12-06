
import libtorrent as lt
import requests as rs
import time, os, sys

WORKSPACE = "/tmp/ehen"

class kUrl:
    def __init__(self):
        self.link = ""

    def download(self, link, path):
        if len(link) < 1 or len(path) < 1:
            print >> sys.stderr, "Error: Invalid web link or local folder path."
            return False

        name = self.name_from_link(link)
        
        res = ""
        
        try:
            r = rs.get(link)
            with open(path + '/' + name, 'wb') as f:
                f.write(r.content)

            res = path + '/' + name
            
            print  "Result path: " + res
            
            return True, res
        except Exception as e:
            print >> sys.stderr, "Error: " + str(e)

            return False

    def name_from_link(self, link):
        if len(link) < 1:
            return ""

        a = link.split('/')

        if len(a) < 2:
            return link

        return a[-1]

class kTorrent:
    def __init__(self):
        self.link = ""
        self.folder = WORKSPACE

    def dw_torrent(self, link):
        if len(link) < 1:
            return False

        print 'Checking address ' + str(link)
        
        if os.path.exists(self.folder) is False:
            os.mkdir(self.folder)

            if os.path.exists(self.folder) is False:
                print >> sys.stderr, "Error: Unable to create folder " + str(self.folder)
                sys.exit(1)

        self.session = lt.session({'listen_interfaces': '0.0.0.0:6881'})

        self.info = lt.torrent_info(link)
        self.handle = self.session.add_torrent({'ti': self.info, 'save_path': self.folder})
        s = self.handle.status()
        print('starting', s.name)

        res = False
        path = ""

        while (not s.is_seeding):
            s = self.handle.status()

            print '\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, s.state)

            alerts = self.session.pop_alerts()
            for a in alerts:
                if a.category() & lt.alert.category_t.error_notification:
                    print a

            sys.stdout.flush()

            time.sleep(1)

            res = True

        print self.handle.status().name +  ' complete'

        path = self.folder + '/' + self.handle.status().name

        return res, path
        
    def dw_magnet(self, link):
        if len(link) < 1:
            return False

        print 'Checking address ' + str(link)
        
        if os.path.exists(self.folder) is False:
            os.mkdir(self.folder)

            if os.path.exists(self.folder) is False:
                print >> sys.stderr, "Error: Unable to create folder " + str(self.folder)
                sys.exit(1)

        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.params = {
            'save_path': self.folder,
            'storage_mode': lt.storage_mode_t(2),
            'paused': False,
            'auto_managed': True,
            'duplicate_is_error': True}
        
        self.handle = lt.add_magnet_uri(ses, self.link, self.params)
        self.session.start_dht()

        print 'downloading metadata...'
        
        while (not self.handle.has_metadata()):
            time.sleep(1)
            
        print 'got metadata, starting torrent download...'
        
        while (handle.status().state != lt.torrent_status.seeding):
            s = self.handle.status()
            state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
            print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' %  (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, state_str[s.state])
            time.sleep(5)


if len(sys.argv) < 2:
    print('Error: torrent link not provided')
    sys.exit(1)


url = kUrl()
stat, tf = url.download(sys.argv[1], WORKSPACE)

if stat is False:
    print >> sys.stderr, "Error: Cannot dowload web link"
    sys.exit(1)
    
tor = kTorrent()

stat, path = tor.dw_torrent(tf)

if stat is True and len(path) > 0:
    print "Opening result file: " + path
    os.system('mcomix "' + path + '"')
