# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.query import QuerySet, ValuesQuerySet, ValuesListQuerySet

try:
    import gviz_api
except ImportError:
    raise ImportError("You must install the gviz_api library.")

class GChartsManager(models.Manager):
    
    def get_query_set(self):
        return GChartsQuerySet(self.model, using=self._db)
    
    def to_string(self, *args, **kwargs):
        return self.get_query_set().to_string(*args, **kwargs)
    
    def to_javascript(self, name, *args, **kwargs):
        return self.get_query_set().to_javascript(name, *args, **kwargs)
    
    def to_html(self, *args, **kwargs):
        return self.get_query_set().to_html(*args, **kwargs)
    
    def to_csv(self, *args, **kwargs):
        return self.get_query_set().to_csv(*args, **kwargs)
    
    def to_tsv_excel(self, *args, **kwargs):
        return self.get_query_set().to_tsv_excel(*args, **kwargs)
    
    def to_json(self, **kwargs):
        return self.get_query_set().to_json(**kwargs)
    
    def to_json_response(self, *args, **kwargs):
        return self.get_query_set().to_json_response(*args, **kwargs)
    
    def to_response(self, *args, **kwargs):
        return self.get_query_set().to_response(*args, **kwargs)


class GChartsQuerySet(QuerySet):
    """
    A QuerySet which returns google charts compatible data
    output
    """
    def __init__(self, *args, **kwargs):
        super(GChartsQuerySet, self).__init__(*args, **kwargs)
        
    def __javascript_field__(self, field):
        """
        Return the javascript data type for
        field
        """
        fields = {
            ("CharField", "CommaSeparatedIntegerField", "EmailField",
             "FilePathField", "IPAddressField", "GenericIPAddressField",
             "SlugField", "TextField", "URLField"): "string",
            ("AutoField", "DecimalField", "FloatField", "IntegerField",
             "BigIntegerField", "PositiveIntegerField", "ForeignKey",
             "PositiveSmallIntegerField", "SmallIntegerField"): "number",
            ("BooleanField", "NullBooleanField"): "boolean",
            ("DateField"): "date",
            ("DateTimeField"): "datetime",
            ("TimeField"): "timeofday",
        }
        
        for k, v in fields.iteritems():
            if field.get_internal_type() in k:
                return v
        # Should never hit this
        raise KeyError("%s is not a valid field" % field)
    
    def table_description(self, **kwargs):
        """
        Create table description for QuerySet
        """
        # TODO: Implement support for extra fields
        table = {}
        labels = kwargs.pop("labels", {})
        fields = getattr(self, "field_names", self.model._meta.get_all_field_names())
        defaults = dict([(k, k) for k in fields])
        for f in self.model._meta.fields:
            if f.attname in labels:
                labels[f.name] = labels.pop(f.attname)
            defaults.update(**labels)
            if f.name in defaults:
                f_jstype = self.__javascript_field__(f)
                table.update({f.name: (f_jstype, defaults[f.name])})
        return table
    
    def values(self, *fields):
        return self._clone(klass=GChartsValuesQuerySet, setup=True, _fields=fields)
    
    def values_list(self, *fields, **kwargs):
        flat = kwargs.pop('flat', False)
        if kwargs:
            raise TypeError('Unexpected keyword arguments to values_list: %s'
                    % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
        return self._clone(klass=GChartsValuesListQuerySet, setup=True, flat=flat,
                _fields=fields)
    
    #
    # Methods which serialize data to various outputs
    # These methods does _not_ return a new QuerySet
    #
    
    def to_json(self, **kwargs):
        """
        Return QuerySet data as json serialized string.
        
        kwargs:
            columns_order: iterable with field names in which the
                    columns should be ordered.
            labels: dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
        """
        
        labels = kwargs.pop("labels", {})
        columns_order = kwargs.pop("columns_order", None)

        assert isinstance(labels, dict), \
            "labels must be a dictionary {'field_name': 'label'}"
        
        table_description = self.table_description(labels=labels)
        fields = table_description.keys()
        data_table = gviz_api.DataTable(table_description=table_description,
                                        data=self.values(*fields))
        return data_table.ToJSon(columns_order=columns_order)
    
    #
    # Methods that modifies database are not allowed
    #
    def create(self, *kwargs):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    
    def bulk_create(self, objs):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    
    def get_or_create(self, *kwargs):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    
    def delete(self):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    
    def update(self, *kwargs):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    
    def _update(self, *kwargs):
        raise NotImplementedError("GChartsQuerySet is not able to modify the database")
    

class GChartsValuesQuerySet(GChartsQuerySet, ValuesQuerySet):
    def __init__(self, *args, **kwargs):
        super(GChartsValuesQuerySet, self).__init__(*args, **kwargs)


class GChartsValuesListQuerySet(GChartsValuesQuerySet, ValuesListQuerySet):
    def __init__(self, *args, **kwargs):
        super(GChartsValuesListQuerySet, self).__init__(*args, **kwargs)
        
