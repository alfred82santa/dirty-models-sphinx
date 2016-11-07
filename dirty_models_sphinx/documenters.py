"""dsdsdsdsd"""

import sphinx.ext.autodoc
import sphinx.domains.python
import sphinx.roles

from dirty_models.models import BaseModel
from dirty_models.fields import (BaseField, IntegerField, FloatField, StringField,
                                 StringIdField, BooleanField, TimeField, DateField,
                                 DateTimeField, ModelField, ArrayField, TimedeltaField, HashMapField, BlobField,
                                 MultiTypeField, EnumField)


class DirtyModelDocumenter(sphinx.ext.autodoc.ClassDocumenter):

    """A Documenter for :class:`dirty_models.models.BaseModel`.
    """
    objtype = 'dirtymodel'  # Called 'autodirtymodel'

    # Since these have very specific tests, we give the classes defined here
    # very high priority so that they override any other documenters.
    priority = 100 + sphinx.ext.autodoc.ClassDocumenter.priority

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, type) and issubclass(member, BaseModel)

    def get_object_members(self, want_all):
        members_check_module, members = super(DirtyModelDocumenter, self).get_object_members(want_all)

        new_members = []

        for name, member in members:
            if not isinstance(member, BaseField):
                new_members.append((name, member))

        for field_name, member in self.object.get_structure().items():
            try:
                member.default = self.object.get_default_data()[field_name]
            except KeyError:
                pass
            new_members.append((field_name, member))

        return members_check_module, new_members


def field_format(parse_format):
    if isinstance(parse_format, str):
        return '``{}``'.format(parse_format)
    elif isinstance(parse_format, dict):
        try:
            return field_format(parse_format['formatter'])
        except KeyError:
            pass
        try:
            return field_format(parse_format['parser'])
        except KeyError:
            pass

        return field_format(None)
    elif callable(parse_format):
        return 'formatted by :py:func:`{0}.{1}`'.format(parse_format.__module__,
                                                        parse_format.__qualname__)


class DirtyModelAttributeDocumenter(sphinx.ext.autodoc.AttributeDocumenter):

    """A Documenter for :class:`dirty_models.fields.BaseField`
    interface attributes.
    """
    objtype = 'dirtymodelattribute'  # Called 'autodirtymoldelattribute'
#     directivetype = 'attribute'

    priority = 100 + sphinx.ext.autodoc.AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, BaseField)

    def add_directive_header(self, sig):
        super(DirtyModelAttributeDocumenter, self).add_directive_header(sig)

        fieldtype = self._get_field_type_str()

        if self.object.read_only:
            self.add_line('   :readonly:', '<autodoc>')

        if self.env.app.config.dirty_model_field_type_as_annotation:
            self.add_line("   :annotation: {0}".format(fieldtype), '<autodoc>')
            self.add_line('   ', '<autodoc>')
        else:
            self.add_line('   ', '<autodoc>')
            self.add_line("   :fieldtype: {0}".format(fieldtype), '<autodoc>')

        if self.object.default is not None:
            self.add_line("   :default: {0}".format(self.object.default), '<autodoc>')

        try:
            if self.object.default_timezone is not None:
                try:
                    if self.object.force_timezone:
                        self.add_line("   :forcedtimezone: {0}".format(self.object.default_timezone), '<autodoc>')
                    else:
                        raise AttributeError()
                except AttributeError:
                    self.add_line("   :defaulttimezone: {0}".format(self.object.default_timezone), '<autodoc>')

        except AttributeError:
            pass

        try:
            frt = field_format(self.object.parse_format)
            if frt:
                self.add_line("   :fieldformat: {0}".format(frt), '<autodoc>')
        except AttributeError:
            pass

    def _get_field_type_str(self, field_desc=None):

        if field_desc is None:
            field_desc = self.object

        if isinstance(field_desc, IntegerField):
            return ':py:class:`int`'
        elif isinstance(field_desc, FloatField):
            return ':py:class:`float`'
        elif isinstance(field_desc, BooleanField):
            return ':py:class:`bool`'
        elif isinstance(field_desc, StringField):
            return ':py:class:`str`'
        elif isinstance(field_desc, StringIdField):
            return ':py:class:`str` (not empty)'

        elif isinstance(field_desc, TimeField):
            return ':py:class:`~datetime.time`'
        elif isinstance(field_desc, DateField):
            return ':py:class:`~datetime.date`'
        elif isinstance(field_desc, DateTimeField):
            return ':py:class:`~datetime.datetime`'
        elif isinstance(field_desc, TimedeltaField):
            return ':py:class:`~datetime.timedelta`'

        elif isinstance(field_desc, HashMapField):
            return ':py:class:`~{0}.{1}` hash map which values are {2}'.format(field_desc.model_class.__module__,
                                                                               field_desc.model_class.__qualname__,
                                                                               self._get_field_type_str(
                                                                                   field_desc.field_type))
        elif isinstance(field_desc, ModelField):
            return ':py:class:`~{0}.{1}`'.format(field_desc.model_class.__module__,
                                                 field_desc.model_class.__qualname__)

        elif isinstance(field_desc, EnumField):
            return ':py:class:`~{0}.{1}`'.format(field_desc.enum_class.__module__,
                                                 field_desc.enum_class.__qualname__)

        elif isinstance(field_desc, ArrayField):
            return 'List of {0}'.format(self._get_field_type_str(field_desc.field_type))

        elif isinstance(field_desc, MultiTypeField):
            return ' or '.join([self._get_field_type_str(field_type) for field_type in field_desc.field_types])
        elif isinstance(field_desc, BlobField):
            return 'anything'

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):

        super(DirtyModelAttributeDocumenter, self).generate(more_content, real_modname,
                                                            check_module, all_members)

        for alias in (self.object.alias or []):
            self.add_line(":alias {0}:".format(alias), '<autodoc>')
