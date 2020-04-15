from datetime import time
from enum import Enum

from dirty_models.fields import IntegerField, StringField, FloatField, StringIdField, BooleanField, TimeField, \
    DateField, DateTimeField, TimedeltaField, HashMapField, ModelField, ArrayField, MultiTypeField, BlobField, EnumField
from dirty_models.models import BaseModel
from pytz import timezone

from dirty_models_sphinx.documenters import AccessMode


class TestEnum(Enum):
    """
    Test enumeration
    """

    #: Value 1
    value_1 = 1

    #: Value 2
    value_2 = 2


class SimpleModel(BaseModel):
    """
    Model with simple type fields
    """

    class InnerTestEnum(Enum):
        """
        Inner enumeration
        """

        #: Value 1
        value_1 = 1

        #: Value 2
        value_2 = 2

    integer_field = IntegerField(read_only=True)
    """
    Documented integer field
    """

    float_field = FloatField(doc="Inner documented float field")

    #: Prefix documented boolean field
    bool_field = BooleanField()
    string_field = StringField(default="default value")
    string_id_field = StringIdField()
    time_field = TimeField(parse_format="%H:%M:%S", default_timezone=timezone('Europe/Paris'))
    date_field = DateField(parse_format={'parser': '%d/%m/%y'})
    datetime_field = DateTimeField(parse_format={'parser': '"%d/%m/%y %H:%M:%S"',
                                                 'formatter': '%d/%m/%y %H:%M:%S'},
                                   default_timezone=timezone('Europe/London'),
                                   force_timezone=True)
    timedelta_field = TimedeltaField()
    blob_field = BlobField()
    enum_field = EnumField(enum_class=TestEnum, default=TestEnum.value_2)
    inner_enum_field = EnumField(enum_class=InnerTestEnum, default=TestEnum.value_1)

    writable_on_creation_field = IntegerField(access_mode=AccessMode.WRITABLE_ONLY_ON_CREATION)
    read_only_field = IntegerField(access_mode=AccessMode.READ_ONLY)
    hidden_field = IntegerField(access_mode=AccessMode.HIDDEN)


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

    def model_method(self):
        """
        Model method
        """
        pass

    @classmethod
    def model_class_method(cls):
        """
        Model method
        """
        pass


class TreeModel(BaseModel):
    """
    Tree model.
    """

    class InnerModel(BaseModel):

        """
        Inner model.
        """

        inner_int_field = IntegerField()
        inner_str_field = StringField()

    int_field = IntegerField()
    str_field = StringField()
