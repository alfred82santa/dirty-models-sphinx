from logging import getLogger

import sphinx.domains.python
import sphinx.ext.autodoc
import sphinx.roles
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.locale import _
from sphinx.util.docfields import Field, GroupedField

from .documenters import DirtyEnumDocumenter, DirtyModelAttributeDocumenter, DirtyModelDocumenter, DirtyModuleDocumenter

logger = getLogger(__name__)

__version__ = '0.6.0'

access_mode_labels = {'read-and-write': None,
                      'writable-only-on-creation': 'WRITABLE ONLY ON CREATION',
                      'read-only': 'READ ONLY',
                      'hidden': 'HIDDEN'}


def access_mode(argument):
    return directives.choice(argument, values=list(access_mode_labels.keys()))


class ModelHeading(object):
    """
    A heading level that is not defined by a string. We need this to work with
    the mechanics of
    :py:meth:`docutils.parsers.rst.states.RSTState.check_subsection`.

    The important thing is that the length can vary, but it must be equal to
    any other instance of FauxHeading.
    """

    def __init__(self):
        pass

    def __len__(self):
        return 0

    def __eq__(self, other):
        return isinstance(other, ModelHeading)


class DirtyModuleDirective(sphinx.domains.python.PyModule):
    """
    A `'dirtymodule'` directive.
    """

    pass


class DirtyEnumDirective(sphinx.domains.python.PyClasslike):
    """
    A `'dirtyenum'` directive.
    """

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'dirtyenum':
            label = _(self.env.app.config.dirty_enum_label or '')
            if not modname:
                return '%s (%s)' % (name_cls[0], label)

            return '%s (%s %s)' % (name_cls[0], modname, label)
        else:
            return ''

    def get_signature_prefix(self, sig):
        if self.env.app.config.dirty_enum_label is None:
            return super(DirtyEnumDirective, self).get_signature_prefix(sig)
        return '{} '.format(_(self.env.app.config.dirty_enum_label))

    def needs_arglist(self):
        return False


class DirtyModelDirective(sphinx.domains.python.PyClasslike):
    """
    A `'dirtymodel'` directive.
    """

    option_spec = {
        **sphinx.domains.python.PyClasslike.option_spec,
        'title': directives.unchanged,
    }

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'dirtymodel':
            label = _(self.env.app.config.dirty_model_class_label or '')
            if not modname:
                return '%s (%s)' % (name_cls[0], label)

            return '%s (%s %s)' % (name_cls[0], modname, label)
        else:
            return ''

    def get_signature_prefix(self, sig):
        if self.env.app.config.dirty_model_class_label is None:
            return super(DirtyModelDirective, self).get_signature_prefix(sig)
        return '{} '.format(_(self.env.app.config.dirty_model_class_label))

    def needs_arglist(self):
        return False

    def handle_signature(self, sig, signode):
        if not self.options.get('title', False):
            return super(DirtyModelDirective, self).handle_signature(sig, signode)

        signode += addnodes.desc_name(self.options['title'], self.options['title'])

        return self.options['title'], self.options['title']

    def run(self):
        result = super(DirtyModelDirective, self).run()

        if self.env.app.config.dirty_model_add_classes_to_toc:
            signode = result[1][0]
            if len(signode['ids']) == 0:
                return result

            result[1] = nodes.section(signode['fullname'], nodes.title(signode['fullname'], signode['fullname'],
                                                                       classes=['remove-node']),
                                      result[1],
                                      ids=signode['ids'])
            if self.env.app.config.dirty_model_add_attributes_to_toc:

                def get_desc_name(node):
                    for subnode in node:
                        if isinstance(subnode, addnodes.desc_name):
                            return subnode

                    return node[0]

                for node in result[1][1][1]:
                    if not isinstance(node, addnodes.desc) \
                            or node['desctype'] not in ('attribute',
                                                        'dirtymodelattribute',
                                                        'method',
                                                        'classmethod',
                                                        'class') \
                            or len(node[0]['ids']) == 0:
                        continue
                    namenode = get_desc_name(node[0])
                    label = namenode.astext()
                    if node['desctype'] in ('method', 'classmethod'):
                        label += '()'
                    result[1] += nodes.section(label,
                                               nodes.title(label,
                                                           label),
                                               ids=node[0]['ids'],
                                               classes=['remove-node'])

        return result


class AliasGroupedField(GroupedField):

    def make_field(self, types, domain, items, env=None):
        fieldname = nodes.field_name('', self.label)
        listnode = self.list_type()
        if len(items) == 1 and self.can_collapse:
            return Field.make_field(self, types, domain, items[0])
        for fieldarg, content in items:
            par = nodes.paragraph()
            par += self.make_xref(self.rolename, domain, fieldarg, nodes.strong)
            listnode += nodes.list_item('', par)
        fieldbody = nodes.field_body('', listnode)
        return nodes.field('', fieldname, fieldbody)


class DirtyModelAttributeDirective(sphinx.domains.python.PyClassmember):
    """An `'dirtymodelattribute'` directive."""

    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
        'annotation': directives.unchanged,
        'access-mode': access_mode,
        'type': directives.unchanged,
        'as-structure': directives.flag,
        'suffix': directives.unchanged,
    }

    doc_field_types = [
        Field('fieldtype', label=_('Type'), has_arg=False,
              names=('fieldtype',)),
        Field('fieldformat', label=_('Format'), has_arg=False,
              names=('fieldformat',)),
        Field('defaultvalue', label=_('Default value'), has_arg=False,
              names=('default',)),
        Field('defaulttimezone', label=_('Default timezone'), has_arg=False,
              names=('defaulttimezone',)),
        Field('forcedtimezone', label=_('Timezone'), has_arg=False,
              names=('forcedtimezone',)),
        AliasGroupedField('aliases', label=_('Aliases'), rolename=None,
                          names=('alias',),
                          can_collapse=False),
        AliasGroupedField('options', label=_('Options'), rolename=None,
                          names=('option',),
                          can_collapse=False)
    ]

    def get_index_text(self, modname, name_cls):
        name, cls = name_cls
        add_modules = self.env.config.add_module_names

        if self.objtype == 'dirtymodelattribute':
            label = _(self.env.app.config.dirty_model_property_label or '')
            clsname, attrname = name.rsplit('.', 1)
            if modname and add_modules:
                return '%s (%s.%s %s)' % (attrname, modname, clsname, label)
            else:
                return '%s (%s %s)' % (attrname, clsname, label)
        else:
            return ''

    def handle_signature(self, sig, signode):
        if 'as-structure' in self.options:
            sig = sig.split('.')[-1]

        result = super(DirtyModelAttributeDirective, self).handle_signature(sig, signode)

        if 'suffix' in self.options:
            signode += addnodes.desc_annotation('', self.options['suffix'])

        typ = self.options.get('type')

        if typ:
            signode += addnodes.desc_annotation('', ': ')
            self.state.nested_parse(ViewList([self.options.get('type')]), 0, signode)

            para = signode.pop(-1)
            for child in para.children:
                child.parent = signode
                signode += child

            para.children = []
        elif 'as-structure' in self.options:
            signode += addnodes.desc_annotation('', ': ')

        access_mode = self.options.get('access-mode', 'read-and-write')
        signode['classes'].append('access-mode-{}'.format(access_mode))

        access_mode_label = access_mode_labels.get(access_mode)
        if access_mode_label:
            t = ' [{}]'.format(_(access_mode_label))
            signode += addnodes.desc_annotation('', t, classes=['access-mode-label'])

        return result

    def get_signature_prefix(self, sig):
        if 'as-structure' in self.options:
            return ''
        if self.env.app.config.dirty_model_class_label is None:
            return super(DirtyModelAttributeDirective, self).get_signature_prefix()
        return '{} '.format(_(self.env.app.config.dirty_model_property_label))


def process_dirty_model_toc(app, doctree):
    """
    Insert items described in autosummary:: to the TOC tree, but do
    not generate the toctree:: list.

    """
    if not app.config.dirty_model_add_classes_to_toc:
        return

    crawled = {}

    def crawl_toc(node):
        crawled[node] = True
        for j, subnode in enumerate(node):
            try:
                if 'remove-node' in subnode['classes']:
                    subnode.replace_self(nodes.comment())
            except Exception:
                continue
            if subnode not in crawled:
                crawl_toc(subnode)

    crawl_toc(doctree)


def setup(app):
    app.add_autodocumenter(DirtyModuleDocumenter)
    app.add_autodocumenter(DirtyEnumDocumenter)
    app.add_autodocumenter(DirtyModelDocumenter)
    app.add_autodocumenter(DirtyModelAttributeDocumenter)

    app.add_config_value('dirty_model_add_classes_to_toc', True, True)
    app.add_config_value('dirty_model_add_attributes_to_toc', True, True)
    app.add_config_value('dirty_model_class_label', 'Model', True)
    app.add_config_value('dirty_model_property_label', 'property', True)
    app.add_config_value('dirty_enum_label', 'enum', True)

    app.add_config_value('dirty_model_hide_alias', False, True)

    app.add_config_value('dirty_model_hide_access_mode', False, True)
    app.add_config_value('dirty_model_hide_access_mode_writable_on_creation', False, True)
    app.add_config_value('dirty_model_hide_access_mode_read_only', False, True)
    app.add_config_value('dirty_model_hide_access_mode_hidden', True, True)

    app.add_config_value('dirty_model_structure_expand_enums', True, True)

    app.connect('doctree-read', process_dirty_model_toc)

    domain = sphinx.domains.python.PythonDomain

    domain.object_types['dirtymodule'] = sphinx.domains.python.ObjType(_('Module'), 'dirtymodule', 'module')
    domain.directives['dirtymodule'] = DirtyModuleDirective
    domain.roles['dirtymodule'] = sphinx.domains.python.PyXRefRole()

    domain.object_types['dirtyenum'] = sphinx.domains.python.ObjType(_('Enum'), 'dirtyenum', 'obj', 'class')
    domain.directives['dirtyenum'] = DirtyEnumDirective
    domain.roles['dirtyenum'] = sphinx.domains.python.PyXRefRole()

    domain.object_types['dirtymodel'] = sphinx.domains.python.ObjType(_('Model'), 'dirtymodel', 'obj', 'class')
    domain.directives['dirtymodel'] = DirtyModelDirective
    domain.roles['dirtymodel'] = sphinx.domains.python.PyXRefRole()

    domain.object_types['dirtymodelattribute'] = sphinx.domains.python.ObjType(_('Attribute'), 'dirtymodelattribute',
                                                                               'obj', 'attr')
    domain.directives['dirtymodelattribute'] = DirtyModelAttributeDirective
    domain.roles['dirtymodelattribute'] = sphinx.domains.python.PyXRefRole()
