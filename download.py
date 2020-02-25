#! /usr/env/bin python3

import requests, json, os, subprocess
import time

def getUrls(baseUrl):
    res = []
    r = requests.get(baseUrl)
    links = r.text.split(baseUrl.strip("https://www.tvnow.de"))
    for l in links:
        if 'href="' in l:
            if "title=" in l:
                if "episode-" in l:
                    res.append(baseUrl + l.split('title="')[0].split('"')[0])
    return res


class Downloader():
    def __init__(self, db):
        self.dbfile = db
        with open(self.dbfile) as f:
            self.db = json.load(f)

    def add(self, name, url):
        self.db.setdefault(name, {}).setdefault(url, {})
        if not os.path.exists(name):
            os.mkdir(name)
        self.update()
        return 0

    def delete(self, name):
        del self.db[name]
        self.dump()

    def dump(self):
        with open(self.dbfile, "w") as o:
            json.dump(self.db, o, sort_keys=True, indent=4)
    
    def update(self): 
        for name in self.db:
            for url in self.db[name]:
                dls = self._getUrls(url)
                for d in dls:
                    self.db[name][url].setdefault(d, 0)
        self.dump()
        return 0

    def download(self):
        for name in sorted(self.db):
            for url in self.db[name]:
                for link in sorted(self.db[name][url]):
                    if self.db[name][url][link] == 0 or self.db[name][url][link] == "drm":
                        date = time.strftime("%Y%m%d")
                        outname = os.path.join("/media/mediadrive/video/downloader", name) + "/" + date + "_" + link.split("/")[-1]
                        #res = subprocess.check_output("/usr/local/bin/youtube-dl -o {} {}".format(outname, link), stderr=subprocess.STDOUT, shell = 1)
                        #res = subprocess.check_output(["/usr/local/bin/youtube-dl", "-o {} {}".format(outname, link)], stderr=subprocess.STDOUT)
                        try:
                            print("Now requesting: ", outname, link) 
                            res = subprocess.check_output("/usr/local/bin/youtube-dl -q -o {} {}".format(outname, link), stderr=subprocess.STDOUT, shell = 1)
                            #res = subprocess.run(["/usr/local/bin/youtube-dl -o {} {}".format(outname, link)], capture_output = 1)
                            #print('test', res)
                            if b"error" not in res.lower():
                                self.db[name][url][link] = 1
                            else:
                                if b"drm" in res.lower():
                                    self.db[name][url][link] = "drm"
                                else:
                                    self.db[name][url][linl] = "error1"
                        except subprocess.CalledProcessError as e:
                            if b"drm" in e.output.lower():
                                self.db[name][url][link] = 'drm'   
                            else:
                                self.db[name][url][link] = 'error2'
        self.dump()
        return 0

    def _getUrls(self, baseUrl):
        res = []
        r = requests.get(baseUrl)
        links = r.text.split(baseUrl.strip("https://www.tvnow.de"))
        for l in links:
            if 'href="' in l:
                if "title=" in l:
                    if "episode-" in l:
                        res.append(baseUrl + l.split('title="')[0].split('"')[0])
        return res




if __name__ == "__main__":
    DL = Downloader("/media/mediadrive/video/downloader/test.json")
    DL.update()
    DL.download()

