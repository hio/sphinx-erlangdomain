# -*- coding: utf-8 -*-
"""
    sphinxcontrib.erlangdomain
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Erlang domain.

    :copyright: Copyright 2007-2010 by SHIBUKAWA Yoshiki
    :license: BSD, see LICENSE for details.
"""
from typing import Any, Dict, List, Tuple
from docutils.nodes import Node
from sphinx.environment import BuildEnvironment
from docutils.parsers.rst.states import Inliner

import copy
from distutils.version import LooseVersion, StrictVersion
from pkg_resources import get_distribution
import re
import string
import sys

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import _
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType, Index
#from sphinx.util.compat import Directive
from docutils.parsers.rst import Directive
from sphinx.util.nodes import make_refnode
from sphinx.util.docfields import Field, GroupedField, TypedField

# +===+====================+=======+=============+==========+=================+
# | # | directive          | ns(*1)| object_type | decltype | role            |
# +===+====================+=======+=============+==========+=================+
# | 1 | .. callback::      | cb    | callback    | callback | :callback:`...` |
# | 2 | .. clause::        | (*2)  | clause      | (*3)     | (*4)            |
# | 3 | .. function::      | fn    | function    | function | :func:`...`     |
# | 4 | .. macro::         | macro | macro       | macro    | :macro:`...`    |
# | 5 | .. opaque::        | ty    | opaque      | opaque   | :type:`...`     |
# | 6 | .. record::        | rec   | record      | record   | :record:`...`   |
# | 7 | .. type::          | ty    | type        | type     | :type:`...`     |
# +---+--------------------+-------+-------------+----------+-----------------+
# | 8 | .. module::        | (n/a) | module      | (n/a)    | :mod:`...`      |
# | 9 | .. currentmodule:: | (n/a) | (n/a)       | (n/a)    | (n/a)           |
# +===+====================+=======+=============+==========+=================+
#
# (*1) namespace. same grouping as role.
# (*2) decltype of clause is fn or cb. depends on whether its ancestor node
#      is function or callback respectively.
# (*3) decltype of clause is function or callback. depends on whether which its
#      ancestor node is.
# (*4) role of clause is :func:`...` or :callback:`...`. depends on whether
#      which its ancestor node is.


RE_ATOM = re.compile( r'''
    ^
    (?: ([a-z]\w*) | '([-\w.]+)' )
    \Z
    ''', re.VERBOSE)


# any identifier (atom or variable).
RE_NAME = re.compile( r'''
    ^
    (?: ([A-Za-z_]\w*) | '([-\w.]+)' )
    \Z
    ''', re.VERBOSE)


RE_SIGNATURE = re.compile( r'''
    ^
    # modname.
    (?:
        (?P<modname> [a-z]\w*|'[-\w.]+')
        \s*
        :
        \s*
    )?

    # sigil and thing name.
    (?P<sigil>[#?])?
    (?P<name> [a-zA-Z_]\w*|'[-\w.]+')
    \s*

    (?:
        (?:
            [/] \s* (?P<arity>\d+) (?:[.][.](?P<arity_max>\d+))? \s*
        |
            [(] \s* (?P<arg_text>.*?) \s* [)] \s*
        )
        (?:
            [@] \s* (?P<flavor> [a-zA-Z_]\w*|'[-\w.]+') \s*
        |
            \[ \s* [@] \s* (?P<implicit_flavor> [a-zA-Z_]\w*|'[-\w.]+') \s* \] \s*
        )?
        (?: when \s* (?P<when_text> .+?) \s* )?
        (?: -> \s* (?P<ret_ann>\S.*?) \s* )?
    |
        [{] \s* (?P<rec_decl>\S.*?)? \s* [}] \s*
    )?

    # drop a terminal period at this time if any.
    [.;]?
    \Z
    ''', re.VERBOSE)

RE_PUNCS = re.compile(r'(\[,|[\[\]{}(),])')

RE_FULLNAME = re.compile( r'''
    ^
    # modname.
    (?P<modname> [a-z]\w*|'[-\w.]+')
    :
    (?P<name> [a-zA-Z_]\w*|'[-\w.]+')
    (?:
        [/]
        (?P<arity>\d+)
        (?:[.][.](?P<arity_max>\d+))?
    )?
    \Z
    ''', re.VERBOSE)

RE_DROP_IMPLICIT_FLAVOR = re.compile( r'''
    \s*
    \[ \s* [@] \s* (?P<implicit_flavor> [a-zA-Z_]\w*|'[-\w.]+') \s* \] \s*
    \Z
    ''', re.VERBOSE)


# {{{ compat.
if sys.version_info[0] < 3:
    # python 2.
    def _iteritems(d):
        return d.iteritems()
else:
    # python 3.
    def _iteritems(d):
        return d.items()


_SPHINX_VERSION = LooseVersion(get_distribution('Sphinx').version)

if _SPHINX_VERSION < LooseVersion('1.3'):
    def _ref_context(env):
        return env.temp_data
else:
    def _ref_context(env):
        return env.ref_context

if _SPHINX_VERSION < LooseVersion('1.4'):
    def _indexentry(entrytype, entryname, target, ignored, key):
        return (entrytype, entryname, target, ignored)
else:
    def _indexentry(entrytype, entryname, target, ignored, key):
        return (entrytype, entryname, target, ignored, key)

if _SPHINX_VERSION < LooseVersion('1.6'):
    def _warn(env, fmt, *args, **kwargs):
        msg = fmt % args
        (docname, lineno) = kwargs['location']
        env.warn(docname, msg, lineno)
else:
    from sphinx.util import logging
    logger = logging.getLogger(__name__)
    def _warn(env, fmt, *args, **kwargs):
        logger.warn(fmt, *args, **kwargs)

if _SPHINX_VERSION < LooseVersion('4.1.0'):
    def make_xrefs_wrap(self, *args, inliner: Any = None, location: Any = None, **kw) -> List[Node]:
        return self.make_xrefs(*args, **kw)
else:
    def make_xrefs_wrap(self, *args, **kw) -> List[Node]:
        return self.make_xrefs(*args, **kw)

# }}} compat.


class ErlangObjectContext:
    def __init__(self, objtype, sigdata):
        self.objtype = objtype
        self.sigdata = sigdata

class ErlangSignature:
    @classmethod
    def canon_atom(cls, name):
        return cls.canon_name_(name, RE_ATOM)

    @classmethod
    def canon_name(cls, name):
        return cls.canon_name_(name, RE_NAME)

    @staticmethod
    def canon_name_(name, regexp):
        m = regexp.match(name)
        if not m:
            # invalid.
            raise ValueError
        if m.group(1) is not None:
            # valid short form.
            return name
        m = RE_ATOM.match(m.group(2))
        if m and m.group(1):
            # can be described in short form.
            return m.group(1)
        # valid long form.
        return name

    # private constructor.
    def __init__(self, nsname, d, decltype=None):
        self.nsname    = nsname
        self.decltype  = decltype        # Optional[decltype]
        self.modname   = d['modname'  ]  # Optional[str]
        self.sigil     = d['sigil'    ]  # Optional[str]
        self.name      = d['name'     ]  # str
        self.flavor    = d['flavor'   ]  # Optional[str]
        self.explicit_flavor = d['explicit_flavor'] # Optional[bool]
        self.when_text = d['when_text']  # Optional[str]
        self.arity     = d['arity'    ]  # Optional[int]
        self.arity_max = d['arity_max']  # Optional[int]
        self.arg_text  = d['arg_text' ]  # Optional[str]
        self.arg_list  = d['arg_list' ]  # Optional[List[Tuple[str,str]]]
        self.ret_ann   = d['ret_ann'  ]  # Optional[str]
        self.rec_decl  = d['rec_decl' ]  # Optional[str]

        if self.modname is not None:
            self.modname = self.canon_atom(self.modname)
        if nsname == 'macro':
            self.name = self.canon_name(self.name)
        else:
            self.name = self.canon_atom(self.name)

        if self.flavor is not None:
            self.flavor = self.canon_atom(self.flavor)

        # check constraint on sigil.
        if self.sigil:
            if (nsname, self.sigil) not in (('macro', '?'), ('rec', '#')):
                raise ValueError

        # check constraint on arity/arity_max.
        if self.arity_max is not None:
            if self.arity is None:
                raise ValueError
            if self.arity >= self.arity_max:
                raise ValueError

        # compute arity.
        if self.arg_list is not None:
            self.arity = len(list(filter(lambda arg: arg[0] == 'mandatory', self.arg_list)))
            if self.arity == len(self.arg_list):
                self.arity_max = None
            else:
                self.arity_max = len(self.arg_list)

        # check constraint on the body part by nsname.
        if self.arity is not None:
            arg_type = 'arity'
        elif self.arg_text is not None:
            arg_type = 'arglist'
        elif self.rec_decl is not None:
            arg_type = 'record'
        else:
            arg_type = 'none'

        ACCEPTABLE_ARG_TYPES = {
            'cb'   : ['arity', 'arglist', 'none'],
            'fn'   : ['arity', 'arglist', 'none'],
            'macro': ['arity', 'arglist', 'none'],
            'rec'  : ['record', 'none'],
            'ty'   : ['arity', 'arglist', 'none'],
        }
        if arg_type not in ACCEPTABLE_ARG_TYPES[nsname]:
            if arg_type != 'none':
                raise ValueError

        if self.when_text is not None:
            if self.nsname not in ('cb', 'fn', 'macro', 'ty'):
                raise ValueError

        if self.ret_ann is not None:
            if self.nsname not in ('cb', 'fn', 'macro'):
                raise ValueError


    @classmethod
    def from_text(cls, sig_text, nsname, decltype=None):
        # (str, nsname, Optional[decltype]) -> ErlangSignature
        res = ErlangSignatureParser.run(sig_text)
        return cls(nsname, res.to_dict(), decltype)


    def to_disp_name(self):
        if self.modname is None:
            modname = ''
        else:
            modname = '%s:' % (self.modname,)

        name = self.local_disp_name_()

        flavor = ''
        if self.flavor is not None:
            flavor = '@%s' % (self.flavor,)

        if self.ret_ann is not None:
            retann = ' -> %s' % (self.ret_ann,)
        else:
            retann = ''

        return modname + name + flavor + retann

    def local_disp_name_(self):
        if self.nsname == 'rec':
            if self.rec_decl is None:
                return '#%s{}' % (self.name,)
            else:
                return '#%s{ %s }' % (self.name, self.rec_decl)
        else:
            if self.nsname == 'macro':
                sigil = '?'
            else:
                sigil = ''
            if self.arity is None:
                return '%s%s'        % (sigil, self.name)
            elif self.arg_text is not None:
                return '%s%s(%s)'    % (sigil, self.name, self.arg_text)
            elif self.arity_max is None:
                return '%s%s/%d'     % (sigil, self.name, self.arity)
            else:
                return '%s%s/%d..%d' % (sigil, self.name, self.arity, self.arity_max)


    def to_desc_name(self):
        if self.nsname == 'rec':
            return '#%s{}' % (self.name,)
        else:
            if self.nsname == 'macro':
                sigil = '?'
            else:
                sigil = ''
            if self.arity is None:
                return '%s%s'        % (sigil, self.name)
            elif self.arg_text is not None:
                return '%s%s'        % (sigil, self.name)
            elif self.arity_max is None:
                return '%s%s/%d'     % (sigil, self.name, self.arity)
            else:
                return '%s%s/%d..%d' % (sigil, self.name, self.arity, self.arity_max)

    def is_arglist_mandatory(self):
        return self.nsname in ['cb', 'fn', 'ty']

    def to_full_name(self):
        return self.to_full_name_(True)

    def to_full_qualified_name(self):
        return self.to_full_name_(False)

    def to_full_name_(self, creation):
        # sigil is not used for anchor names.
        if self.arity_max is not None and creation:
            fullname = '%s:%s/%d..%d' % (self.modname, self.name, self.arity, self.arity_max)
        elif self.arity is not None:
            fullname = '%s:%s/%d'     % (self.modname, self.name, self.arity)
        elif self.is_arglist_mandatory() and creation:
            # arglist is mandatory. treat as no arguments.
            fullname = '%s:%s/0' % (self.modname, self.name)
        else:
            fullname = '%s:%s'   % (self.modname, self.name)

        if self.flavor is not None:
            fullname += '@%s' % (self.flavor)
        return fullname

    def mfa(self):
        return (self.modname, self.name, self.arity)

    @staticmethod
    def drop_flavor_from_full_name(fullname):
        return re.compile(r'@.*\Z').sub('', fullname, 1)

class ErlangSignatureParser:
    RE_ATOM = re.compile(r"[a-z]\w*|'[-\w.]+'")
    RE_NAME = re.compile(r"[A-Za-z_]\w*|'[-\w.]+'")
    RE_WS   = re.compile(r'\s*')

    # private constructor.
    def __init__(self, text):
        self.text  = text
        self.pos   = 0
        self.stack = []

        self.modname   = None
        self.sigil     = None
        self.name      = None
        self.flavor    = None
        self.explicit_flavor = None
        self.when_text = None
        self.arity     = None
        self.arity_max = None
        self.arg_list  = None
        self.arg_text  = None
        self.ret_ann   = None
        self.rec_decl  = None


    def to_dict(self):
        return {
                'modname'   : self.modname,
                'sigil'     : self.sigil,
                'name'      : self.name,
                'flavor'    : self.flavor,
                'explicit_flavor': self.explicit_flavor,
                'when_text' : self.when_text,
                'arity'     : self.arity,
                'arity_max' : self.arity_max,
                'arg_list'  : self.arg_list,
                'arg_text'  : self.arg_text,
                'ret_ann'   : self.ret_ann,
                'rec_decl'  : self.rec_decl,
            }


    def skip_ws(self):
        m = self.RE_WS.match(self.text, self.pos)
        if m is not None:
            self.pos = m.end(0)

    def consume(self, regexp, required=False):
        m = re.compile(regexp).match(self.text, self.pos)
        if m is not None:
            self.pos = m.end(0)
            self.skip_ws()
            return m.group(0)
        else:
            if required:
                raise ValueError
            return None

    def consume_all(self, list):
        ret = []
        for r in list:
            m = self.consume(r)
            if m is None:
                return None
            ret.append(m)
        return ret

    def consume_token(self):
        m = self.consume('\[,')
        if m is None:
            m = self.consume('[(){}\[\]]')
        if m is None:
            m = self.consume(self.RE_NAME)
        if m is None:
            m = self.consume(r'\d+')
        if m is None:
            m = self.consume(r'->|::|[.]{2,}|[-+*/#?$<>=,.:|]')
        if m is None:
            if self.pos != len(self.text):
                raise ValueError
        return m

    def consume_arg_list(self):
        if self.consume('[)]') is not None:
            self.arg_list = []
            self.arg_text = ''
            return

        self.arg_list = []
        argm     = 'mandatory'
        argstack = []
        pos0   = self.pos
        pos    = self.pos
        endpos = self.pos
        num_opts = 0
        while True:
            lastpos = self.pos
            m = self.consume_token()
            if m is None:
                raise ValueError
            if len(argstack) == 0:
                if m == ')':
                    arg = self.text[pos:endpos].strip()
                    self.arg_list.append((argm, arg))
                    break
                if m == ',':
                    arg = self.text[pos:endpos].strip()
                    self.arg_list.append((argm, arg))
                    pos    = self.pos
                    endpos = self.pos
                    continue

            if m == '[,':
                if endpos != pos0:
                    arg = self.text[pos:endpos].strip()
                    self.arg_list.append((argm, arg))
                argm = 'optional'
                pos    = self.pos
                endpos = self.pos
                argstack.append('[')
                num_opts += 1
                continue

            if len(argstack) - num_opts == 0:
                if m == ']':
                    argstack.pop()
                    num_opts -= 1
                    continue
                if m == '=':
                    endpos = self.pos
                    argm = 'optional'
                    continue

            if m in ('(', '{', '['):
                endpos = self.pos
                argstack.append(m)
                continue
            if m in (')', '}', ']'):
                endpos = self.pos
                argstack.pop()
                continue
            endpos = self.pos
        self.arg_text = self.text[pos0:lastpos]

    def consume_until(self, str):
        pos0 = self.pos
        while True:
            lastpos = self.pos
            m = self.consume_token()
            if m is None:
                return self.text[pos0:].strip()
            if m == str:
                self.pos = lastpos
                return self.text[pos0:lastpos].strip()

    def push_state(self):
        self.stack.append(self.pos)

    def accept(self):
        self.stack.pop()

    def rollback(self):
        self.pos = self.stack.pop()

    @classmethod
    def run(cls, text):
        self = cls(text)
        self.skip_ws()

        # "{modname}:"
        self.push_state()
        tmp_modname = self.consume(self.RE_ATOM)
        if tmp_modname is None:
            self.rollback()
        else:
            if self.consume(':') is None:
                self.rollback()
            else:
                self.modname = tmp_modname
                self.accept()
        del tmp_modname

        # sigil and thing name.
        self.sigil = self.consume('[#?]')
        self.name = self.consume(self.RE_NAME)
        if self.name is None:
            raise ValueError

        # special case for record.
        if self.consume('[{]') is not None:
            m = re.compile(r'(.*?)\s*[}]\s*[.]?\Z').match(self.text, self.pos)
            if m is None:
                raise ValueError
            self.rec_decl = m.groups(1)
            return self

        # fun/callback/type/macro.
        if self.consume('/') is not None:
            self.arity = int(self.consume(r'\d+', required=True))
            if self.consume('[.][.]') is not None:
                self.arity_max = int(self.consume(r'\d+', required=True))
        elif self.consume('[(]') is not None:
            self.consume_arg_list()
        else:
            pass

        # flavor.
        self.push_state()
        if self.consume('@') is not None:
            self.flavor = self.consume(self.RE_ATOM)
            self.explicit_flavor = True
            self.accept()
        else:
            m = self.consume_all([r'\[', '@', self.RE_ATOM, r'\]'])
            if m is not None:
                self.flavor = m[2]
                self.explicit_flavor = False
                self.accept()
            else:
                self.rollback()

        if self.consume(r'when\b') is not None:
            self.when_text = self.consume_until('->')
            if self.when_text == '':
                raise ValueError

        if self.consume(r'->') is not None:
            self.ret_ann = self.consume_until('.')
            if self.ret_ann == '':
                raise ValueError

        # drop a terminal period if any.
        self.consume('[.]')

        if self.pos != len(self.text):
            raise ValueError

        return self

class ErlangRaisesField(TypedField):
    def make_field(self, types: Dict[str, List[Node]], domain: str,
                   items: Tuple, env: BuildEnvironment = None,
                   inliner: Inliner = None, location: Node = None) -> nodes.field:
        def handle_item(fieldarg: str, content: str) -> nodes.paragraph:
            par = nodes.paragraph()
            if fieldarg in types:
                # NOTE: using .pop() here to prevent a single type node to be
                # inserted twice into the doctree, which leads to
                # inconsistencies later when references are resolved
                fieldtype = types.pop(fieldarg)
                if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
                    typename = fieldtype[0].astext()
                    handle_text(par, typename)
                else:
                    # already marked up.
                    par += fieldtype
            else:
                # fieldarg is always a str. markups in fieldarg are removed
                # by sphinx?
                handle_text(par, fieldarg)

            par += nodes.Text(' -- ')
            par += content
            return par

        def handle_text(par: nodes.paragraph, text: str):
            tmp = text.split(':', 1)
            if len(tmp) == 2 and tmp[0] in ('error', 'throw', 'exit'):
                err_cls = tmp[0]
                text = tmp[1]
                par += nodes.Text(err_cls + ':')

            if RE_ATOM.match(text):
                # looks like an atom.
                par.extend(make_xrefs_wrap(self, self.rolename, domain, text,
                                           literal_code, env=env))
            else:
                # resolve with typerole.
                par.extend(make_xrefs_wrap(self, self.typerolename, domain, text,
                                           addnodes.literal_emphasis, env=env,
                                           inliner=inliner, location=location))

        fieldname = nodes.field_name('', self.label)
        if len(items) == 1 and self.can_collapse:
            fieldarg, content = items[0]
            bodynode: Node = handle_item(fieldarg, content)
        else:
            bodynode = self.list_type()
            for fieldarg, content in items:
                bodynode += nodes.list_item('', handle_item(fieldarg, content))
        fieldbody = nodes.field_body('', bodynode)
        return nodes.field('', fieldname, fieldbody)

class literal_code(nodes.literal, addnodes.not_smartquotable):
    """Node that behaves like `code`, but further text processors are not
    applied (e.g. smartypants for HTML output).

    See also ``addnodes.literal_emphasis``.
    """

class ErlangBaseObject(ObjectDescription):
    """
    Description of an Erlang language object.
    """

    option_spec = {
        'noindex'   : directives.flag,
        'deprecated': directives.flag,
        'module'    : directives.unchanged,
        'flavor'    : directives.unchanged,
        'auto_importable': directives.flag,
    }

    doc_field_types = [
        TypedField('parameter', label=_('Parameters'),
                   names=('param', 'parameter'),
                   typerolename='type', typenames=('type',)),
        Field('returnvalue', label=_('Returns'), has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label=_('Return type'), has_arg=False,
              names=('rtype',), bodyrolename='type'),
        ErlangRaisesField('exceptions', label=_('Raises'),
                          names=('raises', 'raise'),
                          typerolename='type', typenames=('raisetype',),
                          can_collapse=True),
    ]

    NAMESPACE_FROM_OBJTYPE = {
        'callback': 'cb',
        'function': 'fn',
        'macro'   : 'macro',
        'record'  : 'rec',
        'opaque'  : 'ty',
        'type'    : 'ty',
    }

    NAMESPACE_FROM_ROLE = {
        'callback': 'cb',
        'func'    : 'fn',
        'macro'   : 'macro',
        'record'  : 'rec',
        'type'    : 'ty',
    }

    @staticmethod
    def namespace_of(objtype):
        return ErlangObject.NAMESPACE_FROM_OBJTYPE[objtype]

    @staticmethod
    def namespace_of_role(typ):
        return ErlangObject.NAMESPACE_FROM_ROLE[typ]

    def handle_signature(self, sig_text, signode):
        self.erl_sigdata    = None
        self.erl_env_object = None

        self._setup_data(sig_text)
        self._construct_nodes(signode)

        return self.erl_sigdata.to_full_name()

    def _setup_data(self, sig_text):
        if self.objtype == 'clause':
            env_object = _ref_context(self.env)['erl:object']
            decltype   = env_object.objtype
        else:
            env_object = None
            decltype   = self.objtype

        nsname = self.namespace_of(decltype)
        try:
            sigdata = ErlangSignature.from_text(sig_text, nsname, decltype)
        except ValueError:
            _warn(self.env,
                'invalid signature for Erlang %s description: %s',
                decltype,
                sig_text,
                location=(self.env.docname, self.lineno))
            raise

        if sigdata.modname is None:
            sigdata.modname = self.options.get(
                'module',
                _ref_context(self.env).get('erl:module', 'erlang'))
        elif 'module' not in self.options:
            pass
        elif self.options['module'] == sigdata.modname:
            pass
        else:
            _warn(self.env,
                'duplicate module specifier in signature and option',
                decltype,
                sig_text,
                location=(self.env.docname, self.lineno))

        if 'flavor' in self.options:
            self.options['flavor'] = ErlangSignature.canon_atom(self.options['flavor'])
            if sigdata.flavor is None:
                sigdata.flavor = self.options['flavor']
            elif sigdata.flavor != self.options['flavor']:
                _warn(self.env,
                    'inconsistent flavor, %s in signature and %s in option.',
                    sigdata.flavor,
                    self.options['flavor'],
                    location=(self.env.docname, self.lineno))
                raise ValueError

        if env_object is not None:
            if sigdata.mfa() != env_object.sigdata.mfa():
                _warn(self.env,
                    'inconsistent %s clause, got %s for %s.',
                    env_object.objtype,
                    '%s:%s/%d' % sigdata.mfa(),
                    '%s:%s/%d' % obj_object.sigdata.mfa(),
                    location=(self.env.docname, self.lineno))
                raise ValueError

        self.erl_sigdata    = sigdata
        self.erl_env_object = env_object

    def _construct_nodes(self, signode):
        sigdata    = self.erl_sigdata
        env_object = self.erl_env_object

        # emulate erlang directives, like '-type', '-record', etc.
        if self.objtype not in ('function', 'clause'):
            objtype_part = '-%s' % (self.objtype,)
            signode += addnodes.desc_annotation(objtype_part, objtype_part)
            signode += nodes.inline(' ', ' ')

        if 'auto_importable' not in self.options:
            # hide module name if the function can be auto-imported.
            # e.g. `is_integer/1`.
            modname_part = '%s:' % (sigdata.modname,)
            signode += addnodes.desc_addname(modname_part, modname_part)

        name_part = sigdata.to_desc_name()
        signode += addnodes.desc_name(name_part, name_part)

        if sigdata.arg_list is not None:
            paramlist_node = addnodes.desc_parameterlist()
            signode += paramlist_node
            last_node = paramlist_node
            for (req, txt) in sigdata.arg_list:
                if req == 'mandatory':
                    last_node += addnodes.desc_parameter(txt, txt)
                else:
                    opt = addnodes.desc_optional()
                    opt += addnodes.desc_parameter(txt, txt)
                    last_node += opt
                    last_node = opt

        if sigdata.explicit_flavor:
            flavor_text = ' @%s' % (sigdata.flavor,)
            signode += nodes.inline(flavor_text, flavor_text)

        if sigdata.when_text is not None:
            when_text = ' when %s' % (sigdata.when_text,)
            signode += nodes.emphasis(when_text, when_text)

        if sigdata.ret_ann:
            signode += addnodes.desc_returns(sigdata.ret_ann, sigdata.ret_ann)


    def add_target_and_index(self, fullname, sig_text, signode):
        refname = 'erl.%s.%s' % (self.erl_sigdata.nsname, fullname)
        self._add_target(refname, signode)
        self._add_index(refname, fullname)

    def _add_target(self, refname, signode):
        signode['first'] = (not self.names)
        if refname not in self.state.document.ids:
            signode['names'].append(refname)
            signode['ids'].append(refname)
            refname_2 = ErlangSignature.drop_flavor_from_full_name(refname)
            if refname_2 != refname and refname_2 not in self.state.document.ids:
                signode['names'].append(refname_2)
                signode['ids'].append(refname_2)
            self.state.document.note_explicit_target(signode)

        sigdata = self.erl_sigdata
        objname = '%s:%s' % (sigdata.modname, sigdata.name)
        if sigdata.arity_max is not None:
            arity_range = range(sigdata.arity, sigdata.arity_max + 1)
        elif sigdata.arity is not None:
            arity_range = [sigdata.arity]
        elif sigdata.is_arglist_mandatory():
            # arglist is mandatory. treat as no arguments.
            arity_range = [0]
        else:
            # no arglist portion.
            arity_range = [None]

        oinv = self.env.domaindata['erl']['objects'][sigdata.nsname]
        arities = oinv.setdefault(objname, {})

        deprecated = 'deprecated' in self.options
        for arity in arity_range:
            new_entry = ObjectEntry(self.env.docname, deprecated, sigdata, refname, self.lineno)
            arities.setdefault(arity, {})
            if sigdata.flavor not in arities[arity]:
                # ok. register entry.
                arities[arity][sigdata.flavor] = new_entry

                if None not in arities[arity]:
                    s2 = copy.copy(sigdata)
                    s2.flavor = None
                    e2 = new_entry.copy(s2)
                    e2.refname  = 'erl.%s.%s' % (s2.nsname, s2.to_full_name())
                    arities[arity][None] = e2
                continue

            # ng. warn duplicate.
            prev_entry = arities[arity][sigdata.flavor]

            if arity is None:
                name_tmp = '%s:%s'    % (sigdata.modname, sigdata.name)
            else:
                name_tmp = '%s:%s/%d' % (sigdata.modname, sigdata.name, arity)
            if sigdata.flavor:
                name_tmp += ' {flavor=%s}' % (sigdata.flavor,)
            _warn(self.env,
                'duplicate Erlang %s description of %s, '
                'other instance in %s line %d.',
                sigdata.decltype,
                name_tmp,
                self.env.doc2path(prev_entry.docname),
                prev_entry.lineno,
                location=(self.env.docname, self.lineno))
        if not arities:
            del oinv[objname]

    def _add_index(self, refname, fullname):
        indextext = self._compute_index_text(fullname)
        self.indexnode['entries'].append(_indexentry('single', indextext, refname, fullname, None))


    def _compute_index_text(self, name):
        decltype = self.erl_sigdata.decltype

        if decltype == 'callback':
            return _('%s (Erlang callback function)') % name
        elif decltype == 'function':
            return _('%s (Erlang function)') % name
        elif decltype == 'macro':
            return _('%s (Erlang macro)') % name
        elif decltype == 'opaque':
            return _('%s (Erlang opaque type)') % name
        elif decltype == 'record':
            return _('%s (Erlang record)') % name
        elif decltype == 'type':
            return _('%s (Erlang type)') % name
        else:
            raise ValueError

class ErlangObject(ErlangBaseObject):
    def handle_signature(self, sig_text, signode):
        if 'erl:object' in _ref_context(self.env):
            _warn(self.env,
                'nested directive may cause undefined behavior.',
                location=(self.env.docname, self.lineno))

        return super(ErlangObject, self).handle_signature(sig_text, signode)


    def before_content(self):
        _ref_context(self.env)['erl:object'] = ErlangObjectContext(self.objtype, self.erl_sigdata)

    def after_content(self):
        if 'erl:object' in _ref_context(self.env):
            del _ref_context(self.env)['erl:object']



class ErlangClauseObject(ErlangBaseObject):
    """
    Description of an Erlang function clause object.
    """

    def _is_valid_location(self):
        if 'erl:object' not in _ref_context(self.env):
            return False
        if _ref_context(self.env)['erl:object'].objtype not in ('function', 'callback'):
            return False

        return True

    def handle_signature(self, sig_text, signode):
        if not self._is_valid_location():
            _warn(self.env,
                'clause directive must be a descendant of function or callback.',
                location=(self.env.docname, self.lineno))
            raise ValueError

        return  super(ErlangClauseObject, self).handle_signature(sig_text, signode)


class ErlangModule(Directive):
    """
    Directive to mark description of a new module.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'platform'  : directives.unchanged,
        'synopsis'  : directives.unchanged,
        'noindex'   : directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        self.env = self.state.document.settings.env
        modname = self.arguments[0].strip()

        try:
            modname = ErlangSignature.canon_atom(modname)
            modname_error = False
        except ValueError:
            _warn(self.env,
                'invalid Erlang module name: %s',
                modname,
                location=(self.env.docname, self.lineno))
            modname = "'invalid-module-name'"
            modname_error = True

        _ref_context(self.env)['erl:module'] = modname

        if 'noindex' in self.options:
            return []

        targetnode = nodes.target('', '', ids=['module-' + modname], ismod=True)
        self.state.document.note_explicit_target(targetnode)

        if not modname_error:
            minv = self.env.domaindata['erl']['modules']
            if modname not in minv:
                minv[modname] = (
                    self.env.docname,
                    self.options.get('synopsis', ''),
                    self.options.get('platform', ''),
                    'deprecated' in self.options)
            else:
                _warn(self.env,
                    'duplicate Erlang module name of %s, other instance in %s.',
                    modname,
                    self.env.doc2path(minv[modname][0]),
                    location=(self.env.docname, self.lineno))

        # the synopsis isn't printed; in fact, it is only used in the
        # modindex currently
        indextext = _('%s (Erlang module)') % modname
        inode = addnodes.index(entries=[_indexentry('single', indextext,
                                             'module-' + modname, modname, None)])
        return [targetnode, inode]


class ErlangCurrentModule(Directive):
    """
    This directive is just to tell Sphinx that we're documenting
    stuff in module foo, but links to module foo won't lead here.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        modname = self.arguments[0].strip()
        if modname == 'None':
            _ref_context(env)['erl:module'] = None
        else:
            _ref_context(env)['erl:module'] = modname
        return []


class ErlangMarker(Directive):
    """
    Directive for <marker> of edoc.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        self.env = self.state.document.settings.env
        marker_name = self.arguments[0].strip()

        k_entry = self.register(self.env, marker_name)

        targetnode = nodes.target('', '', ids=[k_entry.refname])
        self.state.document.note_explicit_target(targetnode)

        return [targetnode]

    @staticmethod
    def register(env, marker_name):
        modname  = _ref_context(env).get('erl:module', 'erlang')
        fullname = '%s:%s' % (modname, marker_name)
        refname  = 'erl.mk.%s' % (fullname,)

        k_entry = MarkerEntry(
            fullname,
            marker_name,
            env.docname,
            refname,
        )

        k_inv = env.domaindata['erl']['markers']
        if marker_name not in k_inv:
            # seealso: ErlangDomain.get_objects
            k_inv[marker_name] = k_entry

        return k_entry


class MarkerEntry:
    def __init__(self, fullname, dispname, docname, refname):
        self.fullname = fullname
        self.dispname = dispname
        self.docname  = docname
        self.refname  = refname

    def to_intersphinx_target(self):
        return (
                self.fullname,
                self.dispname,
                'marker',
                self.docname,
                self.refname,
                1, # '1' means default search priority.
            )


class ErlangXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['erl:module'] = _ref_context(env).get('erl:module')
        if not has_explicit_title:
            title = title.lstrip(':')   # only has a meaning for the target
            target = target.lstrip('~') # only has a meaning for the title
            # if the first character is a tilde, don't display the module/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                colon = title.rfind(':')
                if colon != -1:
                    title = title[colon+1:]

        # if the first character is a colon, search more specific namespaces first
        # else search builtins first
        if target[0:1] == ':':
            target = target[1:]
            refnode['refspecific'] = True

        title = RE_DROP_IMPLICIT_FLAVOR.sub('', title)
        return title, target


class ErlangMarkerRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        k_entry = ErlangMarker.register(env, target)
        refnode['ids'].append(k_entry.refname)
        return '', target


class ErlangModuleIndex(Index):
    """
    Index subclass to provide the Erlang module index.
    """

    name = 'modindex'
    localname = _('Erlang Module Index')
    shortname = _('modules')

    def generate(self, docnames=None):
        content = {}
        # list of prefixes to ignore
        ignores = self.domain.env.config['modindex_common_prefix']
        ignores = sorted(ignores, key=len, reverse=True)
        # list of all modules, sorted by module name
        modules = sorted(_iteritems(self.domain.data['modules']),
                         key=lambda x: x[0].lower())
        # sort out collapsable modules
        prev_modname = ''
        num_toplevels = 0
        for modname, (docname, synopsis, platforms, deprecated) in modules:
            if docnames and docname not in docnames:
                continue

            for ignore in ignores:
                if modname.startswith(ignore):
                    modname = modname[len(ignore):]
                    stripped = ignore
                    break
            else:
                stripped = ''

            # we stripped the whole module name?
            if not modname:
                modname, stripped = stripped, ''

            entries = content.setdefault(modname[0].lower(), [])

            package = modname.split(':', 1)[0]
            if package != modname:
                # it's a submodule
                if prev_modname == package:
                    # first submodule - make parent a group head
                    entries[-1][1] = 1
                elif not prev_modname.startswith(package):
                    # submodule without parent in list, add dummy entry
                    entries.append([stripped + package, 1, '', '', '', '', ''])
                subtype = 2
            else:
                num_toplevels += 1
                subtype = 0

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([stripped + modname, subtype, docname,
                            'module-' + stripped + modname, platforms,
                            qualifier, synopsis])
            prev_modname = modname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel modules is larger than
        # number of submodules
        collapse = len(modules) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(_iteritems(content))

        return content, collapse

class ObjectEntry:
    def __init__(self, docname, deprecated, sigdata, refname, lineno):
        self.docname    = docname
        self.deprecated = deprecated
        self.sigdata    = sigdata
        self.refname    = refname
        self.lineno     = lineno

        self.dispname = sigdata.to_disp_name()
        if deprecated:
            self.dispname += ' (deprecated)'

        self.objtype  = sigdata.decltype

    def copy(self, sigdata):
        return ObjectEntry(
                self.docname,
                self.deprecated,
                sigdata,
                self.refname,
                self.lineno,
            )

    def intersphinx_names(self, arity, flavor):
        # Create canoninal and variation names.
        # Sphinx 1.6 does not need variations by
        # Domain.get_full_qualified_name.
        # variations are needed to be referenced by sphinx 1.5 and prior.

        if self.objtype == 'macro':
            sigil_variants = ['', '?']
        elif self.objtype == 'record':
            sigil_variants = ['', '#']
        else:
            sigil_variants = ['']

        if self.objtype == 'record':
            arg_variants = ['', '{}']
        elif arity is None:
            arg_variants = ['']
        elif arity == 0:
            arg_variants = ['/0', '()', ]
        elif self.sigdata.arg_list is None:
            arg_variants = ['/%s' % (arity, )]
        else:
            arg_names = map(lambda pair: pair[1], self.sigdata.arg_list[0:arity])
            arg_variants = [
                '/%s'  % (arity, ),
                '(%s)' % (', '.join(arg_names), ),
            ]

        if self.sigdata.flavor is None:
            flavor_variants = ['']
        else:
            flavor_variants = ['', '@%s' % (flavor, )]

        for sigil in sigil_variants:
            for arg in arg_variants:
                for flavor in flavor_variants:
                    invname = ''.join([
                        self.sigdata.modname,
                        ':',
                        sigil,
                        self.sigdata.name,
                        arg,
                        flavor
                    ])
                    yield invname

    def to_intersphinx_target(self, fullname):
        # '1' means default search priority.
        # See sphinx.domains.Domain#get_objects.
        return (fullname, fullname, self.objtype, self.docname, self.refname, 1)


class ErlangDomain(Domain):
    """Erlang language domain."""
    name = 'erl'
    label = 'Erlang'

    # object_type is used for objtype of result from get_objects.
    object_types = {
        'callback': ObjType(_('callback function'), 'callback'),
        'function': ObjType(_('function'),          'func'    ),
        'macro'   : ObjType(_('macro'),             'macro'   ),
        'opaque'  : ObjType(_('opaque type'),       'type'    ),
        'record'  : ObjType(_('record'),            'record'  ),
        'type'    : ObjType(_('type'),              'type'    ),
        'module'  : ObjType(_('module'),            'mod'     ),
        'marker'  : ObjType(_('marker'),            'seealso' ),
    }

    # directive name is used for directive#objtype.
    directives = {
        'callback'     : ErlangObject,
        'clause'       : ErlangClauseObject,
        'function'     : ErlangObject,
        'macro'        : ErlangObject,
        'opaque'       : ErlangObject,
        'record'       : ErlangObject,
        'type'         : ErlangObject,
        'module'       : ErlangModule,
        'currentmodule': ErlangCurrentModule,
        'marker'       : ErlangMarker,
    }

    roles = {
        'callback': ErlangXRefRole(warn_dangling=True),
        'func'    : ErlangXRefRole(warn_dangling=True),
        'macro'   : ErlangXRefRole(warn_dangling=True),
        'record'  : ErlangXRefRole(warn_dangling=True),
        'type'    : ErlangXRefRole(warn_dangling=True),
        'mod'     : ErlangXRefRole(warn_dangling=True),
        'marker'  : ErlangMarkerRole(),
        'seealso' : ErlangXRefRole(warn_dangling=True),
    }

    initial_data = {
        'objects'   : {
            # :: namespace -> modfuncname -> arity -> flavor -> ObjectEntry
            # arity maybe None for receords and macros.
            'cb'    : {},
            'fn'    : {},
            'macro' : {},
            'rec'   : {},
            'ty'    : {},
        },
        'modules'   : {}, # modname -> docname, synopsis, platform, deprecated
        'markers'   : {}, # marker_name  -> Marker
    }

    data_version = 3

    indices = [
        ErlangModuleIndex,
    ]

    def clear_doc(self, docname):
        rmmods = []
        for modname in self.data['modules']:
            if self.data['modules'][modname][0] == docname:
                rmmods.append(modname)
        for modname in rmmods:
            del self.data['modules'][modname]

        for nsname, oinv in _iteritems(self.data['objects']):
            rmfuncs = []
            for objname, arities in _iteritems(oinv):
                rmarities = []
                for arity, flavors in _iteritems(arities):
                    rmflavors = []
                    for flavor, entry in _iteritems(flavors):
                        if entry.docname == docname:
                            rmflavors.append(flavor)
                    for flavor in rmflavors:
                        del oinv[objname][arity][flavor]
                    if not oinv[objname][arity]:
                        rmarities.append(arity)
                for arity in rmarities:
                    del oinv[objname][arity]
                if not oinv[objname]:
                    rmarities.append(objname)
            for objname in rmfuncs:
                del oinv[objname]

    def _find_obj(self, env, env_modname, name, typ, searchorder=0):
        """
        Find an object for "name", perhaps using the given module name.

        - `searchorder` -- 0=builtins first, 1=namespaces first (refspecific)
        """

        nsname  = ErlangObject.namespace_of_role(typ)
        try:
            sigdata = ErlangSignature.from_text(name, nsname, None)
        except ValueError:
            return None

        if sigdata.modname is None:
            modname = env_modname
        else:
            modname = sigdata.modname
        objname = '%s:%s' % (modname, sigdata.name)

        oinv = self.data['objects'][nsname]
        if objname not in oinv:
            return None

        if sigdata.arity in oinv[objname]:
            flavors = oinv[objname][sigdata.arity]
        elif sigdata.arity is None:
            arity   = min(oinv[objname])
            flavors = oinv[objname][arity]
        else:
            return None

        if sigdata.flavor not in flavors:
            return None
        else:
            entry = flavors[sigdata.flavor]

        if entry.objtype == 'callback':
            title = '%s (%s)' % (entry.dispname, _('callback function'))
        elif entry.objtype == 'function':
            title = entry.dispname
        elif entry.objtype == 'macro':
            title = entry.dispname
        elif entry.objtype == 'record':
            title = entry.dispname
        elif entry.objtype == 'opaque':
            title = '%s %s' % (entry.dispname, _('opaque type'))
        elif entry.objtype == 'type':
            title = '%s %s' % (entry.dispname, _('type'))
        else:
            raise ValueError

        return title, entry.docname, entry.refname

    def resolve_xref(self, env, fromdocname, builder,
                     typ, target, node, contnode):
        if typ == 'mod':
            if target not in self.data['modules']:
                return None
            docname, synopsis, platform, deprecated = self.data['modules'][target]
            title = target
            if synopsis:
                title += ': ' + synopsis
            if deprecated:
                title += _(' (deprecated)')
            if platform:
                title += ' (' + platform + ')'
            refname = 'module-' + target
            return make_refnode(builder, fromdocname, docname, refname,
                                contnode, title)
        elif typ == 'seealso':
            if target not in self.data['markers']:
                return None
            k_entry = self.data['markers'][target]
            title   = target
            docname = k_entry.docname
            refname = k_entry.refname
            return make_refnode(builder, fromdocname, docname, refname,
                                contnode, title)
        elif typ == 'marker':
            return None
        else:
            env_modname = node.get('erl:module')
            searchorder = node.hasattr('refspecific') and 1 or 0
            found = self._find_obj(env, env_modname, target, typ, searchorder)
            if found is None:
                return None
            else:
                title, docname, refname = found
                return make_refnode(builder, fromdocname, docname, refname,
                                    contnode, title)

    # get_objects returns a tuple with 6 elements.
    # [0]: fullname to identify the object in a domain implementation.
    # [1]: dispname.
    # [2]: object_type.
    # [3]: document name.
    # [4]: anchor name in output.
    # [5]: serach priority.
    def get_objects(self):
        for modname, info in _iteritems(self.data['modules']):
            yield (modname, modname, 'module', info[0], 'module-' + modname, 0)

        for _k_name, k_entry in _iteritems(self.data['markers']):
            yield k_entry.to_intersphinx_target()

        for nsname, oinv in _iteritems(self.data['objects']):
            for objname, arities in _iteritems(oinv):
                for arity, flavors in _iteritems(arities):
                    for flavor, entry in _iteritems(flavors):
                        for objname in entry.intersphinx_names(arity, flavor):
                            yield entry.to_intersphinx_target(objname)

    # since sphinx 1.6.
    def get_full_qualified_name(self, node):
        # type: (nodes.Node) -> unicode
        role = node['reftype']

        if role == 'mod':
            target = node['reftarget']
            if target not in self.data['modules']:
                return None
            refname = 'module-' + target
            return refname

        sig_text = node['reftarget']
        nsname   = ErlangObject.namespace_of_role(node['reftype'])
        try:
            sig_data = ErlangSignature.from_text(sig_text, nsname)
        except ValueError:
            return None
        return sig_data.to_full_qualified_name()


def setup(app):
    app.add_domain(ErlangDomain)
