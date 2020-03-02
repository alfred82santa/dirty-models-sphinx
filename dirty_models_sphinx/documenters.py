"""
Auto Documenters
"""

from enum import Enum
from inspect import getdoc
from logging import getLogger
from typing import Any

import sphinx.ext.autodoc
import sphinx.roles
from dirty_models.fields import (ArrayField, BlobField, BooleanField, DateField, DateTimeField, EnumField,
                                 FloatField, HashMapField, IntegerField, ModelField, MultiTypeField, StringField,
                                 StringIdField, TimeField, TimedeltaField)
from dirty_models.models import BaseField, BaseModel
from dirty_models.utils import factory
from sphinx.util.docstrings import prepare_docstring

logger = getLogger(__name__)


class DirtyModuleDocumenter(sphinx.ext.autodoc.ModuleDocumenter):
    """
    A Documenter for module.
    """
    objtype = 'dirtymodule'  # Called 'autodirtyenum'

    # Since these have very specific tests, we give the classes defined here
    # very high priority so that they override any other documenters.
    priority = 100 + sphinx.ext.autodoc.ModuleDocumenter.priority

    option_spec = {
        **sphinx.ext.autodoc.ModuleDocumenter.option_spec,
        'as-structure': sphinx.ext.autodoc.bool_option,
        'hide-readonly': sphinx.ext.autodoc.bool_option,
        'hide-alias': sphinx.ext.autodoc.bool_option,
        'show-readonly': sphinx.ext.autodoc.bool_option,
        'show-alias': sphinx.ext.autodoc.bool_option,
        'struct-expand-enums': sphinx.ext.autodoc.bool_option,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(DirtyModuleDocumenter, self).__init__(*args, **kwargs)

        if 'as-structure' in self.options:
            self.options['noindex'] = True


class DirtyEnumDocumenter(sphinx.ext.autodoc.ClassDocumenter, sphinx.ext.autodoc.ClassLevelDocumenter):
    """
    A Documenter for :class:`enum.Enum`.
    """

    objtype = 'dirtyenum'  # Called 'autodirtyenum'

    # Since these have very specific tests, we give the classes defined here
    # very high priority so that they override any other documenters.
    priority = 100 + sphinx.ext.autodoc.ClassDocumenter.priority

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, Enum)
        except TypeError:
            return False


def merge_options(options, config):
    if 'hide-alias' not in options:
        options['hide-alias'] = config.dirty_model_hide_alias

    if 'show-alias' in options:
        options['hide-alias'] = False

    if 'hide-readonly' not in options:
        options['hide-readonly'] = config.dirty_model_hide_readonly

    if 'show-readonly' in options:
        options['hide-readonly'] = False

    if 'struct-expand-enums' not in options:
        options['struct-expand-enums'] = config.dirty_model_structure_expand_enums


class DirtyModelDocumenter(sphinx.ext.autodoc.ClassDocumenter):
    """
    A Documenter for :class:`dirty_models.models.BaseModel`.
    """
    objtype = 'dirtymodel'  # Called 'autodirtymodel'

    # Since these have very specific tests, we give the classes defined here
    # very high priority so that they override any other documenters.
    priority = 100 + sphinx.ext.autodoc.ClassDocumenter.priority

    option_spec = {
        **sphinx.ext.autodoc.ClassDocumenter.option_spec,
        'title': lambda x: x if x and isinstance(x, str) and len(x) else False,
        'as-structure': sphinx.ext.autodoc.bool_option,
        'hide-readonly': sphinx.ext.autodoc.bool_option,
        'hide-alias': sphinx.ext.autodoc.bool_option,
        'show-readonly': sphinx.ext.autodoc.bool_option,
        'show-alias': sphinx.ext.autodoc.bool_option,
        'struct-expand-enums': sphinx.ext.autodoc.bool_option,
    }

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)

        merge_options(self.options, self.env.app.config)

        if self.options.title:
            self.options.noindex = True

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        try:
            return issubclass(member, BaseModel)
        except TypeError:
            return isinstance(member, BaseModel)

    def format_args(self, **kwargs: Any) -> str:
        return None

    def add_directive_header(self, sig: str) -> None:
        """
        Add the directive header and options to the generated content
        ."""

        super(DirtyModelDocumenter, self).add_directive_header(sig)

        sourcename = self.get_sourcename()
        if self.options.title:
            self.add_line('   :title: %s' % self.options.title, sourcename)

    def get_object_members(self, want_all):
        members_check_module, members = super(DirtyModelDocumenter, self).get_object_members(True)

        new_members = []

        if 'as-structure' not in self.options:
            for name, member in members:
                if not isinstance(member, BaseField):
                    new_members.append((name, member))

        for field_name, member in self.object.get_structure().items():
            if member.metadata is not None and member.metadata.get('hidden', False):
                continue

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
    """
    A Documenter for :class:`dirty_models.fields.BaseField`
    interface attributes.
    """

    objtype = 'dirtymodelattribute'  # Called 'autodirtymoldelattribute'

    priority = 100 + sphinx.ext.autodoc.AttributeDocumenter.priority

    option_spec = {
        **sphinx.ext.autodoc.AttributeDocumenter.option_spec,
        'as-structure': sphinx.ext.autodoc.bool_option,
        'hide-readonly': sphinx.ext.autodoc.bool_option,
        'hide-alias': sphinx.ext.autodoc.bool_option,
        'show-readonly': sphinx.ext.autodoc.bool_option,
        'show-alias': sphinx.ext.autodoc.bool_option,
        'struct-expand-enums': sphinx.ext.autodoc.bool_option,
    }

    def __init__(self, *args, **kwargs):
        super(DirtyModelAttributeDocumenter, self).__init__(*args, **kwargs)

        merge_options(self.options, self.env.app.config)

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, BaseField)

    def get_inner_field(self, field_spec, lst=0):
        if isinstance(field_spec, ArrayField):
            return self.get_inner_field(field_spec.field_type, lst + 1)
        return field_spec, lst

    def add_directive_header(self, sig):
        super(DirtyModelAttributeDocumenter, self).add_directive_header(sig)

        self.build_options(self.object, indent='   ')

        self.add_line('   ', '<autodoc>')

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
            if '<locals>' in field_desc.model_class.__qualname__:
                return ':py:class:`~{0}`'.format(field_desc.model_class.__name__)

            return ':py:class:`~{0}.{1}` hash map which values are {2}'.format(field_desc.model_class.__module__,
                                                                               field_desc.model_class.__qualname__,
                                                                               self._get_field_type_str(
                                                                                   field_desc.field_type))
        elif isinstance(field_desc, ModelField):
            if '<locals>' in field_desc.model_class.__qualname__:
                return ':py:class:`~{0}`'.format(field_desc.model_class.__name__)

            return ':py:class:`~{0}.{1}`'.format(field_desc.model_class.__module__,
                                                 field_desc.model_class.__qualname__)

        elif isinstance(field_desc, EnumField):
            if '<locals>' in field_desc.enum_class.__qualname__:
                return ':py:class:`~{0}`'.format(field_desc.enum_class.__name__)

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

        self.add_line('', '<autodoc>')
        self.build_fields(self.object, '')

        if self.options.get('as-structure', False):
            inner_field, lst = self.get_inner_field(self.object)

            if isinstance(inner_field, ModelField):
                self.document_structure_inner_model(inner_field.model_class)

        self.add_line('', '<autodoc>')

    def build_suffix(self, field_spec, indent):
        if not self.options.get('as-structure', False):
            return

        inner_field, lst = self.get_inner_field(field_spec)

        suffix = ''
        if lst > 0:
            suffix += '[]' * lst

        if len(suffix):
            self.add_line(indent + ':suffix: {0}'.format(suffix), '<autodoc>')

    def build_type(self, field_spec, indent):
        if self.options.get('as-structure', False):
            field_spec, lst = self.get_inner_field(field_spec)

        fieldtype = self._get_field_type_str(field_spec)

        if self.options.get('as-structure', False):
            if isinstance(field_spec, ModelField):
                return

            if isinstance(field_spec, EnumField) and self.options.get('struct-expand-enums'):
                self.add_line(indent + ':type: enum', '<autodoc>')
                return

        self.add_line(indent + ':type: {0}'.format(fieldtype), '<autodoc>')

    def build_readonly(self, field_spec, indent):
        if field_spec.read_only and not self.options.get('hide-readonly', False):
            self.add_line(indent + ':readonly:', '<autodoc>')

    def build_options(self, field_spec, indent):
        # if self.options.get('noindex'):
        #     self.add_line(indent + ':noindex:', '<autodoc>')

        if self.options.get('as-structure'):
            self.add_line(indent + ':as-structure:', '<autodoc>')

        self.build_type(field_spec, indent)
        self.build_readonly(field_spec, indent)

    def build_autodoc_options(self, field_spec, indent):
        if self.options.get('hide-readonly'):
            self.add_line(indent + ':hide-readonly:', '<autodoc>')

        if self.options.get('hide-alias'):
            self.add_line(indent + ':hide-alias:', '<autodoc>')

    def build_default_value(self, field_spec, indent):
        if field_spec.default is None:
            return
        default = field_spec.default
        if isinstance(default, factory):
            default = default()

        if hasattr(self.object, 'get_formatted_value'):
            default = field_spec.get_formatted_value(default)

        if isinstance(default, Enum):
            if self.options.get('as-structure'):
                default = default.value
            else:
                default = ':py:attr:`{0}.{1}`'.format(default.__class__.__qualname__,
                                                      default.name)
        self.add_line(indent + ':default: {0}'.format(default), '<autodoc>')

    def build_timezone(self, field_spec, indent):
        try:
            if field_spec.default_timezone is not None:
                try:
                    if field_spec.force_timezone:
                        self.add_line(indent + ':forcedtimezone: {0}'.format(field_spec.default_timezone),
                                      '<autodoc>')
                    else:
                        raise AttributeError()
                except AttributeError:
                    self.add_line(indent + ':defaulttimezone: {0}'.format(field_spec.default_timezone),
                                  '<autodoc>')
        except AttributeError:
            pass

    def build_format(self, field_spec, indent):
        try:
            frt = field_format(field_spec.parse_format)
            if frt:
                self.add_line(indent + ':fieldformat: {0}'.format(frt), '<autodoc>')
        except AttributeError:
            pass

    def build_alias(self, field_spec, indent):
        if self.options.get('hide-alias', False):
            return
        for alias in (field_spec.alias or []):
            self.add_line(indent + ':alias {0}:'.format(alias), '<autodoc>')

    def build_field_options(self, field_spec, indent):
        if not self.options.get('as-structure', False) \
                or not isinstance(field_spec, EnumField) \
                or not self.options.get('struct-expand-enums'):
            return

        for v in field_spec.enum_class:
            self.add_line(indent + ':option {0}:'.format(v.value), '<autodoc>')

    def build_fields(self, field_spec, indent):
        self.build_default_value(field_spec, indent)
        self.build_timezone(field_spec, indent)
        self.build_format(field_spec, indent)
        self.build_alias(field_spec, indent)
        self.build_field_options(field_spec, indent)

    def document_structure_inner_model(self, model, indent=''):
        self.add_line(indent + '', '<autodoc>')

        for field_name, member in model.get_structure().items():
            if member.metadata is not None and member.metadata.get('hidden', False):
                continue

            self.add_line(indent + f'.. py:dirtymodelattribute:: {model.__qualname__}.{field_name}', '<autodoc>')
            self.add_line(indent + f'   :module: {model.__module__}', '<autodoc>')
            self.build_suffix(member, indent + '   ')

            member, lst = self.get_inner_field(member)

            self.build_options(member, indent + '   ')
            if self.options.get('noindex'):
                self.add_line(indent + '   :noindex:', '<autodoc>')

            self.add_line(indent + '   ', '<autodoc>')

            docstring = getdoc(member)
            if docstring:
                tab_width = self.directive.state.document.settings.tab_width
                [self.add_line(indent + '   ' + l, '<autodoc>') for l in prepare_docstring(docstring, 1, tab_width)]

            self.add_line(indent + '   ', '<autodoc>')
            self.build_fields(member, indent + '   ')

            self.add_line(indent + '', '<autodoc>')

            if isinstance(member, ModelField):
                self.document_structure_inner_model(member.model_class, indent=indent + '   ')

                self.add_line(indent + '', '<autodoc>')
