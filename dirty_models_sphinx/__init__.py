import sphinx.ext.autodoc
import sphinx.domains.python
import sphinx.roles
from sphinx.locale import l_
from sphinx import addnodes
from docutils.parsers.rst import directives
from sphinx.util.docfields import Field, GroupedField, TypedField
from .documenters import DirtyModelDocumenter, DirtyModelAttributeDocumenter


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


class DirtyModelAttributeDirective(sphinx.domains.python.PyClassmember):

    r"""An `'dirtymodelattribute'` directive."""

    option_spec = {
        'noindex': directives.flag,
        'module': directives.unchanged,
        'annotation': directives.unchanged,
        'readonly': directives.flag,
        'type': directives.unchanged,
    }

    doc_field_types = [
        GroupedField('aliases', label=l_('Aliases'), rolename='obj',
                     names=('alias',),
                     can_collapse=True),
        Field('type', label=l_('Type'),  has_arg=False,
              names=('fieldtype',)),
    ]

    def handle_signature(self, sig, signode):
        result = super(DirtyModelAttributeDirective, self).handle_signature(sig, signode)
        fieldtype = self.options.get('type', None)
        if fieldtype:
            fieldtypestr = ': {0}'.format(fieldtype)
            signode += addnodes.desc_type(fieldtypestr, fieldtypestr)
        readonly = 'readonly' in self.options
        if readonly:
            signode += addnodes.desc_addname(' [READ ONLY]', ' [READ ONLY]')
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
