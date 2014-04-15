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
    objtype = 'dirtymodel'               # Called 'autodirtymodel'

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
    objtype = 'dirtymodelattribute'   # Called 'autodirtymoldelattribute'
    priority = 100 + sphinx.ext.autodoc.AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, BaseField)

    def add_content(self, more_content, no_docstring=False):
        # Revert back to default since the docstring *is* the correct thing to
        # display here.
        sphinx.ext.autodoc.ClassLevelDocumenter.add_content(
            self, more_content, no_docstring)

    def generate(self, more_content=None, real_modname=None,
                 check_module=False, all_members=False):

        super(DirtyModelAttributeDocumenter, self).generate(more_content, real_modname,
                                                            check_module, all_members)

        for alias in (self.object.alias or []):
            self.add_line(":alias field: {0}".format(alias), '<autodoc>')
