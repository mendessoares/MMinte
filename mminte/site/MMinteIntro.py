from pkg_resources import resource_filename
from spyre import server

from mminte.site import MMinteApp, MMinteRoot


server.Root = MMinteRoot


class Intro(MMinteApp):
    title = 'Intro'

    outputs = [
        {"output_type": "html",
         "output_id": "Index",
         "on_page_load": True}
    ]
    
    def getHTML(self, params):
        with open(resource_filename(__name__, 'static/intro.html')) as page:
            return page.read()


if __name__ == '__main__':
    app = Intro()
    app.launch()
