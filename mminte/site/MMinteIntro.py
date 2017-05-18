from pkg_resources import resource_filename

from mminte.site import MMinteApp, MMinteRoot


class Intro(MMinteApp):
    """ Introduction widget application for spyre """

    title = 'Intro'  # Must be here for button label

    def __init__(self):
        self.outputs = [
            {"output_type": "html",
             "output_id": "Index",
             "on_page_load": True}
        ]

        self.root = MMinteRoot(
            templateVars=self.templateVars,
            title=self.title,
            inputs=self.inputs,
            outputs=self.outputs,
            controls=self.controls,
            tabs=self.tabs,
            spinnerFile=self.spinnerFile,
            getJsonDataFunction=self.getJsonData,
            getDataFunction=self.getData,
            getTableFunction=self.getTable,
            getPlotFunction=self.getPlot,
            getImageFunction=self.getImage,
            getD3Function=self.getD3,
            getCustomJSFunction=self.getCustomJS,
            getCustomCSSFunction=self.getCustomCSS,
            getCustomHeadFunction=self.getCustomHead,
            getHTMLFunction=self.getHTML,
            getDownloadFunction=self.getDownload,
            noOutputFunction=self.noOutput,
            storeUploadFunction=self.storeUpload,
            prefix=self.prefix)

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
