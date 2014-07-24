# Create your views here.
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render_to_response
from demosite.models import GeoData, OtherData
from django.template.context import RequestContext
from django.db.models.aggregates import Sum


def home(request):
    """
    Gather some data for the demo site
    """
    if request.method == "GET":
        
        # GeoChart demo
        geo_qset = GeoData.objects.order_by("-population").all()[:100]
        geo_data = geo_qset.values("country_name", "population", "fertility_rate") \
                    .to_json(labels={"country_name": "Country",
                                     "population": "Population",
                                     "fertility_rate": "Birth rate"},
                             formatting={"population": "{0:d} millions",
                                         "fertility_rate": "{0:.3f}"},
                             order=("country_name", "population", "fertility_rate"))
        
        # AreaChart
        area_series_age = datetime.today() - relativedelta(months=1)
        area_qset = OtherData.objects.filter(date__gte=area_series_age) \
                        .values("date").annotate(Sum("number1")) \
                        .annotate(Sum("number2")).order_by()
        area_data = area_qset.order_by("-date").to_json(order=("date", "number1__sum",
                                                               "number2__sum"),
                                                        labels={"number1__sum": "A number",
                                                                "number2__sum": "Another number"})
        
        # PieChart
        pie_qset = OtherData.objects.values("name").annotate(Sum("number1")).order_by()
        pie_data = pie_qset.order_by("name").to_json(order=("name", "number1__sum"),
                             formatting={"number1__sum": "{0:d} Sum total"})
        
        # You get the idea....
        bar_data = line_data = column_data = combo_data = area_data
        
        # Table
        table_series_age = datetime.today() - relativedelta(months=3)
        table_qset = OtherData.objects.filter(date__gte=table_series_age) \
                .values("date").annotate(num_baked=Sum("number1")) \
                .annotate(num_eaten=Sum("number2")).order_by("-date")
        table_data = table_qset.to_json(labels={"date": "Date",
                                         "num_baked": "Rat cakes baked",
                                         "num_eaten": "Rat cakes eaten"},
                                 order=("date", "num_baked", "num_eaten"),
                                 formatting={"num_baked": "{0:d} Kg",
                                             "num_eaten": "{0:d} Kg"})
        
    return render_to_response("home.html", locals(),
                              context_instance=RequestContext(request))
