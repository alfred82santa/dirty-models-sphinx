"""dsdsdsdsd"""

import sphinx.ext.autodoc
import sphinx.domains.python
import sphinx.roles

from dirty_models.models import BaseModel
from dirty_models.fields import (BaseField, IntegerField, FloatField, StringField,
                                 StringIdField, BooleanField, TimeField, DateField,
                                 DateTimeField, ModelField, ArrayField)


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
        """
        Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        members_check_module, members = super(DirtyModelDocumenter, self).get_object_members(want_all)

        new_members = []

        for name, member in members:
            if isinstance(member, BaseField) and (name != member.name):
                if member.alias is None:
                    member.alias = []
                if name not in member.alias:
                    member.alias.append(name)
            else:
                new_members.append((name, member))

        return members_check_module, new_members


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

#     def add_content(self, more_content, no_docstring=False):
#         # Revert back to default since the docstring *is* the correct thing to
#         # display here.
#
#         return sphinx.ext.autodoc.ClassLevelDocumenter.add_content(
#             self, more_content, no_docstring)

    def add_directive_header(self, sig):
        super(DirtyModelAttributeDocumenter, self).add_directive_header(sig)
        if self.object.read_only:
            self.add_line(u'   :readonly:', '<autodoc>')
        fieldtype = self._get_field_type_str()
        if fieldtype:
            self.add_line('', '<autodoc>')
            self.add_line("   **Type:** {0}".format(fieldtype), '<autodoc>')

    def _get_field_type_str(self, field_desc=None):
        if field_desc is None:
            field_desc = self.object

        if isinstance(field_desc, IntegerField):
            return ':class:`int`'
        elif isinstance(field_desc, FloatField):
            return ':class:`float`'
        elif isinstance(field_desc, BooleanField):
            return ':class:`bool`'
        elif isinstance(field_desc, StringField):
            return ':class:`str`'
        elif isinstance(field_desc, StringIdField):
            return ':class:`str` (not empty)'
        elif isinstance(field_desc, TimeField):
            return ':class:`datetime.time`{0}'.format('format: {0})'.format(field_desc.parse_format)
                                                      if field_desc.parse_format else '')
        elif isinstance(field_desc, DateField):
            return ':class:`datetime.date`{0}'.format('format: {0})'.format(field_desc.parse_format)
                                                      if field_desc.parse_format else '')
        elif isinstance(field_desc, DateTimeField):
            return ':class:`datetime.datetime`{0}'.format('format: {0})'.format(field_desc.parse_format)
                                                          if field_desc.parse_format else '')
        elif isinstance(field_desc, ModelField):
            return ':class:`{0}.{1}`'.format(field_desc.model_class.__module__,
                                    field_desc.model_class.__name__)
        elif isinstance(field_desc, ArrayField):
            return 'List of {0}'.format(self._get_field_type_str(field_desc.field_type))

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):

        super(DirtyModelAttributeDocumenter, self).generate(more_content, real_modname,
                                                            check_module, all_members)

        for alias in (self.object.alias or []):
            self.add_line(":alias {0}:".format(alias), '<autodoc>')