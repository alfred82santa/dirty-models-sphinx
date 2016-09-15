from datetime import time

from dirty_models.fields import IntegerField, StringField, FloatField, StringIdField, BooleanField, TimeField, \
    DateField, DateTimeField, TimedeltaField, HashMapField, ModelField, ArrayField, MultiTypeField, BlobField
from dirty_models.models import BaseModel


class SimpleModel(BaseModel):

    """
    Model with simple type fields
    """

    integer_field = IntegerField(read_only=True)
    """
    Documented integer field
    """

    float_field = FloatField(doc="Inner documented float field")

    #: Prefix documented boolean field
    bool_field = BooleanField()
    string_field = StringField(default="default value")
    string_id_field = StringIdField()
    time_field = TimeField(parse_format="%H:%M:%S")
    date_field = DateField(parse_format={'parser': '"%d/%m/%y"'})
    datetime_field = DateTimeField(parse_format={'parser': '"%d/%m/%y %H:%M:%S"',
                                                 'formatter': '%d/%m/%y %H:%M:%S'})
    timedelta_field = TimedeltaField()
    blob_field = BlobField()


class ComposedModel(SimpleModel):

    """
    Model with composed fields
    """

    hashmap_int_field = HashMapField(field_type=IntegerField())
    hashmap_str_field = HashMapField(field_type=StringField())
    model_field = ModelField(model_class=SimpleModel)
    array_int_field = ArrayField(field_type=IntegerField())
    array_str_field = ArrayField(field_type=StringField())
    multitype_field = MultiTypeField(field_types=[IntegerField(),
                                                  StringField()])


def hour_to_time(hour):
    """
    Create time with hour.

    :param hour: Hour
    :type hour: int
    :rtype: datetime.time
    """

    return time(hour=hour, minute=0, second=0)


class AliasModel(BaseModel):

    """
    Model alias fields
    """

    CONSTANT_1 = 'constant1'
    """
    Documented constant 1
    """

    CONSTANT_2 = 'constant2'
    """
    Documented constant 2
    """

    _default_data = {'int_field': 3,
                     'boolean_field': False}

    integer_field = IntegerField(name='int_field', alias=['number_field', 'scalar_field'])
    string_field = StringField(alias=['text_field'])
    bool_field = BooleanField(name='boolean_field')
    time_field = TimeField(parse_format=hour_to_time)
