import os
import json
import urllib
from datetime import datetime
from django.shortcuts import render

from tethys_apps.sdk.gizmos import *
from tethys_apps.sdk import get_spatial_dataset_engine

from .utilities import generate_flood_hydrograph, write_hydrograph_input_file, convert_raster_to_wkb
from .model import SessionMaker, FloodExtent
from sqlalchemy import select


def home(request):
    """
    Controller for the app home page.
    """
    peak_flow_slider = RangeSlider(
                display_text='Peak Flow (cms)',
                name='peak_flow',
                min=500,
                max=1200,
                initial=800,
                step=50
    )

    time_peak_slider = RangeSlider(
                display_text='Time to Peak (hrs.)',
                name='time_to_peak',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    peak_duration_slider = RangeSlider(
                display_text='Peak Duration (hrs.)',
                name='peak_duration',
                min=1,
                max=12,
                initial=6,
                step=1
    )

    falling_limb_duration = RangeSlider(
                display_text='Falling Limb Duration (hrs.)',
                name='falling_limb_duration',
                min=12,
                max=48,
                initial=24,
                step=1
    )

    submit_button = Button(
                display_text='Generate Hydrograph',
                name='submit',
                attributes='form=hydrograph-form',
                submit=True
    )

    context = {'peak_flow_slider': peak_flow_slider,
               'time_peak_slider': time_peak_slider,
               'peak_duration_slider': peak_duration_slider,
               'falling_limb_duration': falling_limb_duration,
               'submit_button': submit_button
    }

    return render(request, 'dam_break/home.html', context)

def hydrograph(request):
    """
    Controller for the hydrograph page.
    """
    peak_flow = 800.0
    time_to_peak = 6
    peak_duration = 6
    falling_limb_duration = 24

    if request.POST  and 'submit' in request.POST:
        peak_flow = float(request.POST['peak_flow'])
        time_to_peak = int(request.POST['time_to_peak'])
        peak_duration = int(request.POST['peak_duration'])
        falling_limb_duration = int(request.POST['falling_limb_duration'])

    # Generate hydrograph
    hydrograph = generate_flood_hydrograph(
        peak_flow=peak_flow, 
        time_to_peak=time_to_peak, 
        peak_duration=peak_duration, 
        falling_limb_duration=falling_limb_duration
    )

    # Write GSSHA file
    write_hydrograph_input_file(
        username=request.user.username, 
        hydrograph=hydrograph                  
    )

    # Configure the Hydrograph Plot View
    flood_hydrograph_plot = HighChartsTimeSeries(
            title='Flood Hydrograph',
            y_axis_title='Flow',
            y_axis_units='cms',
            series=[
               {
                   'name': 'Flood Hydrograph',
                   'color': '#0066ff',
                   'data': hydrograph
               },
            ]
    )

    flood_plot = PlotView(
        highcharts_object=flood_hydrograph_plot,
        width='100%',
        height='500px'
    )

    context = {'flood_plot': flood_plot}

    return render(request, 'dam_break/hydrograph.html', context)


def map(request):
    """
    Controller to handle map page.
    """
    # Constants
    GEOSERVER_WORKSPACE = 'dambreak'
    GEOSERVER_URI = 'tethys.ci-water.org/dam-break'
    ADDRESS_LAYER_ID = GEOSERVER_WORKSPACE + ':provo_address_points'
    BOUNDARY_LAYER_ID = GEOSERVER_WORKSPACE + ':provo_boundary'
    PROJECT_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(PROJECT_DIR, 'data')

    # Initialize GeoServer Layers if not Created Already
    geoserver_engine = get_spatial_dataset_engine('default')

    response = geoserver_engine.list_workspaces()
    
    if response['success']:
        workspaces = response['result']

        if GEOSERVER_WORKSPACE not in workspaces:
            # Create a GeoServer Workspace for the App
            response = geoserver_engine.create_workspace(workspace_id=GEOSERVER_WORKSPACE, 
                                                         uri=GEOSERVER_URI)
            # Upload the Two Shapefiles
            address_zip = os.path.join(DATA_DIR, 'Provo Address Points', 'Provo Address Points.zip')
            response = geoserver_engine.create_shapefile_resource(
                store_id=ADDRESS_LAYER_ID,
                shapefile_zip=address_zip,
                overwrite=True,
                debug=True
            )

            boundary_zip = os.path.join(DATA_DIR, 'Provo Boundary', 'Provo Boundary.zip')
            response = geoserver_engine.create_shapefile_resource(
                store_id=BOUNDARY_LAYER_ID,
                shapefile_zip=boundary_zip,
                overwrite=True,
                debug=True
            )

    # Convert Raster File into Well Known Binary (WKB)
    raster_file = os.path.join(DATA_DIR, '0084_maxFlood.txt')
    wkb = convert_raster_to_wkb(
        raster_path=raster_file,
        srid=26912, 
        no_data=0
    )

    # Add Raster to PostGIS Database
    db_session = SessionMaker()
    flood_extent = FloodExtent(
        username=request.user.username,
        wkb=wkb
    )
    db_session.add(flood_extent)
    db_session.commit()

    # Query for last raster for the current user and convert to GeoJSON
    sql = '''
           SELECT val, ST_AsGeoJSON(ST_Transform(geom, 4326)) As polygon
           FROM (
              SELECT (ST_DumpAsPolygons(raster)).*
              FROM flood_extents WHERE id={0}
           ) As foo
           ORDER BY val;
           '''.format(1)
    result = db_session.execute(sql)

    # Assemble a list of flood extent GeoJSON features
    flood_extent_polygons = []
    for row in result:
        polygon_feature = {
            'type': 'Feature',
            'geometry': json.loads(row.polygon)
        }
        flood_extent_polygons.append(polygon_feature)

    flood_extent_geojson = {
        'type': 'FeatureCollection',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': flood_extent_polygons
    }

    flood_extent_layer = MVLayer(
        source='GeoJSON',
        options=flood_extent_geojson,
        legend_title='Flood',
        legend_extent=[-111.74, 40.21, -111.61, 40.27],
        legend_classes=[
                MVLegendClass('polygon', 'Flood Extent', fill='#ffffff', stroke='#3399CC'),
    ])

    # Filter Addresses by Flood Extent
    sql = '''
           SELECT val, ST_AsGML(ST_Transform(geom, 4326)) As polygon
           FROM (
              SELECT (ST_DumpAsPolygons(raster)).*
              FROM flood_extents WHERE id={0}
           ) As foo
           ORDER BY val;
           '''.format(1)
    result = db_session.execute(sql)

    gml_polygons = ''
    for row in result:
        intersects = '<Intersects>'\
                         '<PropertyName>the_geom</PropertyName>'\
                         '{0}'\
                     '</Intersects>'.format(row.polygon)
        gml_polygons = intersects

    filter_query = '<Filter xmlns:gml="http://www.opengis.net/gml">'\
                        '{0}'\
                    '</Filter>'.format(gml_polygons)

    filter_query = urllib.quote(filter_query)
    print(filter_query)

    # Create Address and Boundary Layers
    address_layer = MVLayer(
            source='ImageWMS',
            options={'url': 'http://localhost:8181/geoserver/wms',
                     'params': {'LAYERS': ADDRESS_LAYER_ID,
                                'FILTER': filter_query},
                     'serverType': 'geoserver'},
            legend_title='Provo Addresses',
            legend_extent=[-111.74, 40.20, -111.61, 40.33],
            legend_classes=[
                MVLegendClass('point', 'Addresses', fill='#ff0000'),
    ])

    boundary_layer = MVLayer(
            source='ImageWMS',
            options={'url': 'http://localhost:8181/geoserver/wms',
                     'params': {'LAYERS': BOUNDARY_LAYER_ID},
                     'serverType': 'geoserver'},
            legend_title='Provo City',
            legend_extent=[-111.74, 40.18, -111.61, 40.33],
            legend_classes=[
                MVLegendClass('polygon', 'City Boundaries', fill='#999999', stroke='#000000'),
    ])

    initial_view = MVView(
        projection='EPSG:4326',
        center=[-111.6608, 40.2444],
        zoom=12
    )

    map_options = MapView(height='500px',
                          width='100%',
                          layers=[flood_extent_layer, address_layer, boundary_layer],
                          legend=True,
                          view=initial_view
    )

    context = {'map_options': map_options}
    return render(request, 'dam_break/map.html', context)