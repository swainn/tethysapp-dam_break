from tethys_apps.base import TethysAppBase, url_map_maker


class ProvoDamBreak(TethysAppBase):
    """
    Tethys app class for Provo Dam Break.
    """

    name = 'Provo Dam Break'
    index = 'dam_break:home'
    icon = 'dam_break/images/icon.gif'
    package = 'dam_break'
    root_url = 'dam-break'
    color = '#9b59b6'
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='dam-break',
                           controller='dam_break.controllers.home'),
                    UrlMap(name='hydrograph',
                           url='dam-break/hydrograph',
                           controller='dam_break.controllers.hydrograph'),
                    UrlMap(name='map',
                           url='dam-break/map',
                           controller='dam_break.controllers.map'),
        )

        return url_maps