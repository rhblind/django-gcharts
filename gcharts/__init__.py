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
        flat = kwargs.pop("flat", False)
        if kwargs:
            raise TypeError("Unexpected keyword arguments to values_list: %s"
                    % (kwargs.keys(),))
        if flat and len(fields) > 1:
            raise TypeError("'flat' is not valid when values_list is called with more than one field.")
        return self._clone(klass=GChartsValuesListQuerySet, setup=True, flat=flat,
                _fields=fields)
    
    def get_properties(self, **kwargs):
        """
        Return properties from kwargs, or set default if not set.
        """
        properties = {
            "order":  kwargs.pop("order", None),
            "properties": kwargs.pop("properties", {}),
            "description": self.table_description(labels=kwargs.pop("labels", {}))
        }
        return properties
        
    #
    # Methods which serialize data to various outputs.
    # These methods are just a convenient wrapper to the
    # methods in the gviz_api calls.
    # 
    def to_javascript(self, name, **kwargs):
        """
        Does _not_ return a new QuerySet.
        Return QuerySet data as javascript code string.
        
        This method writes a string of JS code that can be run to
        generate a DataTable with the specified data. Typically used 
        for debugging only.
        
        kwargs:
            name:   Name of the variable which the data table
                    is saved.
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToJSCode(name=name, columns_order=properties["order"])
    
    def to_html(self, **kwargs):
        """
        Does _not_ return a new QuerySet.
        Return QuerySet data as a html table code string.
        
        kwargs:
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToHtml(columns_order=properties["order"])
    
    def to_csv(self, seperator=",", **kwargs):
        """
        Does _not_ return a new QuerySet.
        Return QuerySet data as a csv string.
        
        Output is encoded in UTF-8 because the Python "csv" 
        module can't handle Unicode properly according to 
        its documentation.
        
        kwargs:
            seperator: character to be used as seperator. Defaults
                    to comma(,).
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToCsv(columns_order=properties["order"], seperator=seperator)
    
    def to_tsv_excel(self, **kwargs):
        """
        Does _not_ return a new QuerySet.
        Returns a file in tab-separated-format readable by MS Excel.
        
        Returns a file in UTF-16 little endian encoding, with tabs 
        separating the values.
        
        kwargs:
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToTsvExcel(columns_order=properties["order"])
    
    def to_json(self, **kwargs):
        """
        Does _not_ return a new QuerySet.
        Return QuerySet data as json serialized string.
        
        This method writes a JSON string that can be passed directly into a Google
        Visualization API DataTable constructor. Use this output if you are
        hosting the visualization HTML on your site, and want to code the data
        table in Python. Pass this string into the
        google.visualization.DataTable constructor, e.g,:
          ... on my page that hosts my visualization ...
          google.setOnLoadCallback(drawTable);
          function drawTable() {
            var data = new google.visualization.DataTable(_my_JSon_string, 0.6);
            myTable.draw(data);
          }
        
        kwargs:
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToJSon(columns_order=properties["order"])
    
    def to_json_response(self, handler="google.visualization.Query.setResponse",
                         req_id=0, **kwargs):
        """
        Does _not_ return a new QuerySet.
        Writes a table as a JSON response that can be returned as-is to a client.

        This method writes a JSON response to return to a client in response to a
        Google Visualization API query. This string can be processed by the calling
        page, and is used to deliver a data table to a visualization hosted on
        a different page.
        
        kwargs:
            req_id: Response id, as retrieved by the request.
            handler: The response handler, as retrieved by the
                    request.
            order:  Iterable with field names in which the
                    columns should be ordered. If columns order
                    are specified, any field not specified will be
                    discarded.
            labels: Dictionary mapping {'field': 'label'}
                    where field is the name of the field in model,
                    and label is the desired label on the chart.
            properties: Dictionary with custom properties.
        """
        properties = self.get_properties(**kwargs)
        fields = properties["description"].keys()
        data_table = gviz_api.DataTable(table_description=properties["description"],
                                        custom_properties=properties["properties"],
                                        data=self.values(*fields))
        return data_table.ToJSonResponse(columns_order=properties["order"], 
                                         response_handler=handler, req_id=req_id)
    
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
        
