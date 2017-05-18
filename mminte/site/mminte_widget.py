from os.path import expanduser, join
from pkg_resources import resource_filename
from io import BytesIO
import cherrypy
from spyre import server


class MMinteRoot(server.Root):
    """ Custom cherrypy Root for MMinte website. """

    @cherrypy.expose
    def image1(self):
        data = BytesIO()
        with open(resource_filename(__name__, 'static/logo.jpg')) as handle:
            data.write(handle.read())
        return data.getvalue()

    @cherrypy.expose
    def image2(self):
        data = BytesIO()
        with open(resource_filename(__name__, 'static/flow.jpg')) as handle:
            data.write(handle.read())
        return data.getvalue()

    @cherrypy.expose
    def widget6_out(self):
        with open(resource_filename(__name__, 'static/plot.html')) as handle:
            return handle.read()

    @cherrypy.expose
    def d3(self):
        with open(resource_filename(__name__, 'static/d3.v3.min.js')) as handle:
            return handle.read()

    @cherrypy.expose
    def data4plot_filename(self):
        return join(expanduser('~'), '.mminte_data4plot.json')

    @cherrypy.expose
    def data4plot_json(self):
        with open(self.data4plot_filename()) as handle:
            return handle.read()


class MMinteApp(server.App):
    """ Base class for spyre apps in MMinte website. """

    root = None
    analysis_folder = join(expanduser('~'), 'mminte_site_tutorial')

    def getRoot(self):
        return self.root

    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/mminte_style.css')) as style:
            return style.read()
