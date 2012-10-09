# -*- coding: utf-8 -*-

import os
import random
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db.transaction import commit_on_success
from demosite.models import GeoData, OtherData

def daterange(start_date, end_date, step=1, include_weekends=True):
    """
    Iterate over a range of dates, incrementing at given step, and
    optionally skip weekends.
    """
    for n in xrange(0, int((end_date - start_date).days), step):
        date = start_date + timedelta(n)
        if not include_weekends and date.isoweekday() in (6, 7):
            continue
        yield date

class Command(NoArgsCommand):
    """
    Initialize the database with some test data.
    """
    @commit_on_success
    def handle_noargs(self, **options):
        
        # Create some data for the GeoData model
        # This data is really random and by no means correct!
        p = os.path.join(settings.PROJECT_PATH, "demosite", "countries.txt")
        with open(p, "r") as fname:
            countries = fname.readlines()

        for _, c in enumerate(countries):
            code, name = c.split(":")
            data = {
                "country_name": name,
                "country_code": code,
                "population": random.randint(1, 1000),
                "fertility_rate": random.uniform(0.7, 7.2)
            }
            GeoData.objects.create(**data)
            self.stdout.write(".")
            self.stdout.flush()
        self.stdout.write("\n")
        
        # Create some data for the OtherData model
        today = datetime.today()
        otherday = today - relativedelta(years=2)
        
        p = os.path.join(settings.PROJECT_PATH, "demosite", "names.txt")
        with open(p, "r") as fname:
            names = fname.readlines()
            
        for d in daterange(otherday, today):
            for n in names:
                data = {
                    "name": n,
                    "number": random.randint(10, 100),
                    "date": d
                }
                OtherData.objects.create(**data)
                self.stdout.write(".")
                self.stdout.flush()
        self.stdout.write("\n")
        
        
            
        