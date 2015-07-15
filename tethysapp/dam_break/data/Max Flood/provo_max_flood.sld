<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>provo_max_flood</sld:Name>
    <sld:UserStyle>
      <sld:Name>provo_max_flood</sld:Name>
      <sld:Title>Provo Max Flood</sld:Title>
      <sld:Abstract>Color Provo Max Flood Raster Maps</sld:Abstract>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#000000" opacity="0.0" quantity="0" label="nodata"/>
              <sld:ColorMapEntry color="#0000FF" opacity="0.5" quantity="1" label="values"/>
              <sld:ColorMapEntry color="#000000" opacity="0.0" quantity="2" label="artifact"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
