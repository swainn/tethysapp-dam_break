from tethys_apps.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore


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

    def persistent_stores(self):
        """
        Register one or more persistent stores for your app.
        """

        stores = (PersistentStore(name='flood_extents',
                                 initializer='init_stores:init_flood_extents_db',
                                 spatial=True),
        )

        return stores