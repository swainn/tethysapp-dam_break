from tethys_apps.base import TethysAppBase, url_map_maker
from tethys_apps.base import PersistentStore
from tethys_compute.job_manager import JobTemplate, JobManager
import os

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
                    UrlMap(name='run',
                           url='dam-break/run',
                           controller='dam_break.controllers.run'),
                    UrlMap(name='jobs',
                           url='dam-break/jobs',
                           controller='dam_break.controllers.jobs'),
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

    @classmethod
    def job_templates(cls):
        """
        Example job_templates method.
        """
        job_templates = (JobTemplate(name='custom_flood',
                                     type=JobManager.JOB_TYPES_DICT['CONDOR'],
                                     parameters={'executable': 'gssha_custom_flood.py',
                                                 'condorpy_template_name': 'vanilla_transfer_files',
                                                 'attributes': {'transfer_input_files': '../gssha_provo_flood, ../ProvoStochastic.ihg'},
                                                 'remote_input_files': ['../../data/gssha_provo_flood/gssha_custom_flood.py',
                                                                        '../../data/gssha_provo_flood',
                                                                        'ProvoStochastic.ihg'],
                                                },
                                     ),
                         )

        return job_templates