import sphinx.domains.python
import sphinx.ext.autodoc
import sphinx.roles
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx import addnodes
from sphinx.locale import l_
from sphinx.util.docfields import Field, GroupedField

from .documenters import DirtyModelDocumenter, DirtyModelAttributeDocumenter


__version__ = '0.4.0'


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


class DirtyModelDirective(sphinx.domains.python.PyClasslike):
    """An `'dirtymodel'` directive."""

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'dirtymodel':
            label = l_(self.env.app.config.dirty_model_class_label or 'model')
            if not modname:
                return '%s (%s)' % (name_cls[0], label)
            return '%s (%s %s)' % (name_cls[0], modname, label)
        else:
            return ''

    def get_signature_prefix(self, sig):
        if self.env.app.config.dirty_model_class_label is None:
            return super(DirtyModelDirective, self).get_signature_prefix()
        return '{} '.format(l_(self.env.app.config.dirty_model_class_label))

    def run(self):
        result = super(DirtyModelDirective, self).run()

        if self.env.app.config.dirty_model_add_classes_to_toc:
            signode = result[1][0]
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
                    if not isinstance(node, addnodes.desc) or node['desctype'] not in ('attribute',
                                                                                       'dirtymodelattribute',
                                                                                       'method',
                                                                                       'classmethod',
                                                                                       'class'):
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

    def make_field(self, types, domain, items):
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
        'readonly': directives.flag,
    }

    doc_field_types = [
        Field('fieldtype', label=l_('Type'), has_arg=False,
              names=('fieldtype',)),
        Field('fieldformat', label=l_('Format'), has_arg=False,
              names=('fieldformat',)),
        Field('defaultvalue', label=l_('Default value'), has_arg=False,
              names=('default',)),
        Field('defaulttimezone', label=l_('Default timezone'), has_arg=False,
              names=('defaulttimezone',)),
        Field('forcedtimezone', label=l_('Timezone'), has_arg=False,
              names=('forcedtimezone',)),
        AliasGroupedField('aliases', label=l_('Aliases'), rolename=None,
                          names=('alias',),
                          can_collapse=False)
    ]

    def get_index_text(self, modname, name_cls):
        name, cls = name_cls
        add_modules = self.env.config.add_module_names

        if self.objtype == 'dirtymodelattribute':
            label = l_(self.env.app.config.dirty_model_property_label or 'attribute')
            clsname, attrname = name.rsplit('.', 1)
            if modname and add_modules:
                return '%s (%s.%s %s)' % (attrname, modname, clsname, label)
            else:
                return '%s (%s %s)' % (attrname, clsname, label)
        else:
            return ''

    def handle_signature(self, sig, signode):
        result = super(DirtyModelAttributeDirective, self).handle_signature(sig, signode)

        if self.options.get('annotation'):
            anno = addnodes.desc_annotation()
            old_node = signode[2]
            if not isinstance(old_node, addnodes.desc_annotation):
                old_node = signode[3]
                del signode[1]
            old_node.replace_self(anno)
            self.state.nested_parse(ViewList([':  ', self.options.get('annotation')]), 0, anno)

        readonly = 'readonly' in self.options
        if readonly:
            signode['classes'].append('readonly')
            t = ' [{}]'.format(l_('READ ONLY'))
            signode += nodes.emphasis(t, t, classes=['readonly-label'])

        return result

    def get_signature_prefix(self, sig):
        if self.env.app.config.dirty_model_class_label is None:
            return super(DirtyModelAttributeDirective, self).get_signature_prefix()
        return '{} '.format(l_(self.env.app.config.dirty_model_property_label))


def process_dirty_model_toc(app, doctree):
    """
    Insert items described in autosummary:: to the TOC tree, but do
    not generate the toctree:: list.

    """
    env = app.builder.env
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
    app.add_autodocumenter(DirtyModelDocumenter)
    app.add_autodocumenter(DirtyModelAttributeDocumenter)

    app.add_config_value('dirty_model_add_classes_to_toc', True, True)
    app.add_config_value('dirty_model_add_attributes_to_toc', True, True)
    app.add_config_value('dirty_model_class_label', 'Model', True)
    app.add_config_value('dirty_model_property_label', 'property', True)
    app.add_config_value('dirty_model_field_type_as_annotation', True, True)

    app.connect('doctree-read', process_dirty_model_toc)

    domain = sphinx.domains.python.PythonDomain
    domain.object_types['dirtymodel'] = sphinx.domains.python.ObjType(
        l_('Model'), 'dirtymodel', 'obj')
    domain.directives['dirtymodel'] = DirtyModelDirective
    domain.roles['dirtymodel'] = sphinx.domains.python.PyXRefRole()

    domain.object_types['dirtymodelattribute'] = sphinx.domains.python.ObjType(
        l_('Attribute'), 'dirtymodelattribute', 'obj')
    domain.directives['dirtymodelattribute'] = DirtyModelAttributeDirective
    domain.roles['dirtymodelattribute'] = sphinx.domains.python.PyXRefRole()
