Yet another Google Charts library for Django

- Requires installation of the gviz_api library which is freely available from Google.
- See http://code.google.com/p/google-visualization-python/ for details.

## Note ##
This library is yet in pre-alpha development mode, and only uploaded to github for the purpose of having it
for my own sake. It's still not ready for use, do _NOT_ use this for anything except experimenting.

Please feel free to fork or submit patches ;)

### Disclaimer ###
This library is heavy influenced by [mvasilkov's django-google-charts](https://github.com/mvasilkov/django-google-charts),
and some of the code (template tags and javascript code) are directly copied from him. I've done some minor adjustments to
make it work for my approach.

### About django-gcharts ###
As I find mvasilkov's approach very clever, I think it's can be done easier. My solution is to subclass the QuerySet
which we are all familiar with, and create a custom manager which can be hooked into the models you wish to draw a chart for.
This is really just a simple wrapper to Google's gviz_api module (which is a requirement for this module to work. See above.).

### Configuration ###

#### settings.py ####
        GOOGLECHARTS_API = "1.1"
        GOOGLECHARTS_PACKAGES = ["corechart"]
        
        INSTALLED_APPS = (
                ...
                'gcharts',
                ...
        )

* GOOGLECHARTS_API - Optional. Defaults to 1.1
* GOOGLECHARTS_PACKAGES - Optional. List of packages that should be loaded. Defaults to only "corechart".
  
#### Packages ####
* corechart contains these charts
  * [AreaChart](https://developers.google.com/chart/interactive/docs/gallery/areachart)
  * [BarChart](https://developers.google.com/chart/interactive/docs/gallery/barchart)
  * [BubbleChart](https://developers.google.com/chart/interactive/docs/gallery/bubblechart)
  * [CandleStickChart](https://developers.google.com/chart/interactive/docs/gallery/candlestickchart)
  * [ColumnChart](https://developers.google.com/chart/interactive/docs/gallery/columnchart)
  * [ComboChart](https://developers.google.com/chart/interactive/docs/gallery/combochart)
  * [LineChart](https://developers.google.com/chart/interactive/docs/gallery/linechart)
  * [PieChart](https://developers.google.com/chart/interactive/docs/gallery/piechart)
  * [ScatterChart](https://developers.google.com/chart/interactive/docs/gallery/scatterchart)
  * [SteppedAreaChart](https://developers.google.com/chart/interactive/docs/gallery/steppedareachart)
* gauge
  * [Gauge](https://developers.google.com/chart/interactive/docs/gallery/gauge)
* geochart
  * [GeoChart](https://developers.google.com/chart/interactive/docs/gallery/geochart)
* table
  * [TableChart](https://developers.google.com/chart/interactive/docs/gallery/table)
* treemap
  * [TreeMap](https://developers.google.com/chart/interactive/docs/gallery/treemap)

### Examples ###
Coming soon™