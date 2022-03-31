import web
import os
from git import Repo
import json

urls = ('/update_server', 'update')
app = web.application(urls, globals()) 
class update:
    def POST(self):
        i = json.loads(web.data())
        if i.token == 'mxu3nv74oiy7vi34n89xnf982bv824tdf34':
            dirfile = ''
            repo = Repo(dirfile)
            g = repo.git
            i = 0
            while i < 5:
                i += 1
                try:
                    g.push()
                except Exception as e:
                    print(e)
                else:
                    print("Successful pull!")
                    break

if __name__ == '__main__':
    app.run()
