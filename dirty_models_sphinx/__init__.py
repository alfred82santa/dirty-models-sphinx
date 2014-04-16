import sphinx.ext.autodoc
import sphinx.domains.python
import sphinx.roles
from sphinx.locale import l_
from sphinx import addnodes
from docutils.parsers.rst import directives
from sphinx.util.docfields import Field, GroupedField
from .documenters import DirtyModelDocumenter, DirtyModelAttributeDocumenter
from docutils import nodes
from docutils.nodes import Node


class DirtyModelDirective(sphinx.domains.python.PyClasslike):

    r"""An `'dirtymodel'` directive."""

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'dirtymodel':
            if not modname:
                return '%s (model)' % name_cls[0]
            return '%s (%s model)' % (name_cls[0], modname)
        else:
            return ''

    def get_signature_prefix(self, sig):
        return 'Model '


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

    r"""An `'dirtymodelattribute'` directive."""

    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
        'annotation': directives.unchanged,
        'readonly': directives.flag,
#         'type': directives.unchanged,
    }

    doc_field_types = [
        AliasGroupedField('aliases', label=l_('Aliases'), rolename=None,
                     names=('alias',),
                     can_collapse=False)
    ]

    def handle_signature(self, sig, signode):
        result = super(DirtyModelAttributeDirective, self).handle_signature(sig, signode)
#         fieldtype = self.options.get('type', None)
#         if fieldtype:
# #             fieldtypestr = ': {0}'.format(fieldtype)
#             node = addnodes.pending_xref(fieldtype, reftype='class', refdomain='py', reftarget=fieldtype)
#             node['py:class'] = fieldtype
#             node += nodes.emphasis(fieldtype, fieldtype)
#             signode += node
#             print (node)
        readonly = 'readonly' in self.options
        if readonly:
            signode += nodes.emphasis(' [READ ONLY]', ' [READ ONLY]')
#         print (result)
        return result


def setup(app):
    app.add_autodocumenter(DirtyModelDocumenter)
    app.add_autodocumenter(DirtyModelAttributeDocumenter)

    domain = sphinx.domains.python.PythonDomain
    domain.object_types['dirtymodel'] = sphinx.domains.python.ObjType(
        l_('Model'), 'dirtymodel', 'obj')
    domain.directives['dirtymodel'] = DirtyModelDirective
    domain.roles['dirtymodel'] = sphinx.domains.python.PyXRefRole()

    domain.object_types['dirtymodelattribute'] = sphinx.domains.python.ObjType(
        l_('Attribute'), 'dirtymodelattribute', 'obj')
    domain.directives['dirtymodelattribute'] = DirtyModelAttributeDirective
    domain.roles['dirtymodelattribute'] = sphinx.domains.python.PyXRefRole()
