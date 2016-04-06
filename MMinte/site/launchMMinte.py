#!/usr/bin/env python

__author__ = 'HMS'



from spyre import server
import os
import cherrypy
cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})


from MMinteIntro import Index
from MMinteW1 import Widget1
from MMinteW2 import Widget2
from MMinteW3 import Widget3
from MMinteW4 import Widget4
from MMinteW5 import Widget5
from MMinteW6 import Widget6
from MMinteW7 import Widget7
from MMrunAll import WidgetRunAll


site = server.Site(Index)


site.addApp(Widget1, '/app1')
site.addApp(Widget2, '/app2')
site.addApp(Widget3, '/app3')
site.addApp(Widget4, '/app4')
site.addApp(Widget5, '/app5')
site.addApp(Widget6, '/app6')
site.addApp(Widget7, '/app7')
site.addApp(WidgetRunAll, '/app8')

site.root.templateVars['app_bar']=[('/','Intro'),('/app1','Widget1'),('/app2','Widget2'),('/app3','Widget3'),('/app4','Widget4'),('/app5','Widget5'),('/app6','Widget6'),('/app7','Widget7'),('/app8','WidgetRunAll')]


for fullRoute, _ in site.site_app_bar[1:]:
            parent, route = site.get_route(fullRoute)
            
            


if __name__ == '__main__':
    site.launch()
