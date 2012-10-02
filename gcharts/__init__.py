# -*- coding: utf-8 -*-
import logging
from django.db import models
from django.db.models.query import QuerySet, ValuesQuerySet, ValuesListQuerySet
from django.db.models.fields import FieldDoesNotExist

try:
    import gviz_api
except ImportError:
    raise ImportError("You must install the gviz_api library.")

class _GChartsConfig(object):
    
    logger = None
    
    @classmethod
    def get_logger(cls):
        """
        Instantiate and return a default logger.
        The NullHandler logger does nothing, and is supposed 
        to be overridden in settings.py by creating a logger
        named 'gcharts'.
        """
        if cls.logger is None:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass
            
            cls.logger = logging.getLogger("gcharts")
            cls.logger.addHandler(NullHandler())
            
        return cls.logger

# Global logger
logger = _GChartsConfig.get_logger()

class GChartsManager(models.Manager):
    
    def get_query_set(self):
        return GChartsQuerySet(self.model, using=self._db)
    
    def to_javascript(self, name, order=None, labels=None, properties=None):
        return self.get_query_set().to_javascript(name, order, labels, properties)
    
    def to_html(self, order=None, labels=None, properties=None):
        return self.get_query_set().to_html(order, labels, properties)
    
    def to_csv(self, order=None, labels=None, properties=None, separator=","):
        return self.get_query_set().to_csv(order, labels, properties, separator)
    
    def to_tsv_excel(self, order=None, labels=None, properties=None):
        return self.get_query_set().to_tsv_excel(order, labels, properties)
    
    def to_json(self, order=None, labels=None, properties=None):
        return self.get_query_set().to_json(order, labels, properties)
    
    def to_json_response(self, order=None, labels=None, properties=None,
                     req_id=0, handler="google.visualization.Query.setResponse"):
        return self.get_query_set().to_json_response(order, labels, properties,
                                                     req_id, handler)
    

class GChartsQuerySet(QuerySet):
    """
    A QuerySet which returns google charts compatible data
    output
    """
    def __init__(self, *args, **kwargs):
        super(GChartsQuerySet, self).__init__(*args, **kwargs)
        
    def javascript_field(self, field):
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
    
    def table_description(self, labels=None):
        """
        Return table description for QuerySet.
        """
        table_description = {}
        labels = labels or {}
        
        # resolve aggregates
        aggregates = getattr(self, "aggregate_names", None)
        if aggregates is not None:
            for alias, aggregate_expr in self.query.aggregates.iteritems():
                label = labels.pop(alias, alias)
                field_jstype = self.javascript_field(aggregate_expr.field)
                table_description.update({alias: (field_jstype, label)})
        
        # resolve extra fields
        # Extra fields need to be defined manually in the labels
        # dict as follows: labels={"extra_name": {"javascript type": "label"}, ... }
        extra = getattr(self, "extra_names", None)
        valid_jstypes = ("string", "number", "boolean", "date", "datetime", "timeofday")
        if extra is not None:
            for alias in self.query.extra.iterkeys():
                try:
                    descr = labels.pop(alias)
                    if (not isinstance(descr, dict) and len(descr)) == 1:
                        raise Exception("Field description must be a dict and must contain exactly one element.")
                    field_jstype, label = descr.popitem()
                    if field_jstype not in valid_jstypes:
                        raise Exception("Invalid javascript type. Valid types are %s." % \
                                        ", ".join(valid_jstypes))
                    table_description.update({alias: (field_jstype, label)})
                except KeyError:
                    raise KeyError("No label found for extra field '%s'. Extra field labels must be configured as: labels={'extra_name': {'javascript type', 'label'}}" % alias)
                except Exception, e:
                    raise e
        
        # resolve other fields of interest
        fields = set(getattr(self, "_fields", [f.name for f in self.model._meta.fields]))
        
        # remove fields that has already been 
        # put in the table_description
        def clean_parsed_fields():
            for f in table_description.iterkeys():
                if f in fields:
                    fields.remove(f) 
        clean_parsed_fields()
        
        for f_name in fields:
            # local fields
            if f_name in self.model._meta.get_all_field_names():
                field = self.model._meta.get_field(f_name)
                if field.attname in labels:
                    labels[field.name] = labels.pop(field.attname)
                label = labels.pop(field.name, field.name)
                field_jstype = self.javascript_field(field)
                table_description.update({field.name: (field_jstype, label)})
            else:
                # lookup fields (with double underscore) left in fields set
                # should now only be join fields, and be present in the
                # local field.related.parent_model's field list
                if "__" in f_name:
                    field, rel_field = f_name.split("__")
                    field = self.model._meta.get_field(field)
                    relation = getattr(field, "related", None)
                    if relation is not None:
                        rel_field = relation.parent_model._meta.get_field(rel_field)
                        label = labels.pop(f_name, f_name)
                        rel_field_jstype = self.javascript_field(rel_field)
                        table_description.update({f_name: (rel_field_jstype, label)})
        
        clean_parsed_fields()
        if fields:
            logger.warning("Could not create table description for the following fields %s:" % \
                           ", ".join(fields))
        return table_description
        
        
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

        
    #
    # Methods which serialize data to various outputs.
    # These methods are just a convenient wrapper to the
    # methods in the gviz_api calls.
    # 
    def to_javascript(self, name, order=None, labels=None, properties=None):
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
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToJSCode(name=name, columns_order=order)
    
    def to_html(self, order=None, labels=None, properties=None):
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
        
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToHtml(columns_order=order)
    
    def to_csv(self, order=None, labels=None, properties=None, separator=","):
        """
        Does _not_ return a new QuerySet.
        Return QuerySet data as a csv string.
        
        Output is encoded in UTF-8 because the Python "csv" 
        module can't handle Unicode properly according to 
        its documentation.
        
        kwargs:
            separator: character to be used as separator. Defaults
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
        
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToCsv(columns_order=order, separator=separator)
    
    def to_tsv_excel(self, order=None, labels=None, properties=None):
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
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToTsvExcel(columns_order=order)
    
    def to_json(self, order=None, labels=None, properties=None):
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
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToJSon(columns_order=order)
    
    def to_json_response(self, order=None, labels=None, properties=None,
                 req_id=0, handler="google.visualization.Query.setResponse"):
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
        table_descr = self.table_description(labels)
        fields = table_descr.keys()
        data_table = gviz_api.DataTable(table_description=table_descr,
                                        custom_properties=properties, 
                                        data=self.values(*fields))
        return data_table.ToJSonResponse(columns_order=order, 
                             req_id=req_id, response_handler=handler)
    
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
        
