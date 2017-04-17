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

    def getCustomCSS(self):
        # Remove menu panel from the Intro page.
        with open(resource_filename(__name__, 'static/mminte_style.css')) as style:
            return style.read()+'\n.menu{display: none;width:5px;}.content{margin-left: 5px;}'

    def getHTML(self, params):
        with open(resource_filename(__name__, 'static/intro.html')) as page:
            return page.read()


if __name__ == '__main__':
    app = Intro()
    app.launch()
