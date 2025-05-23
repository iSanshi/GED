# Copyright 2006 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

"""Fixer for intern().

intern(s) -> sys.intern(s)"""

# Local imports
from .. import pytree
from .. import fixer_base
from ..fixer_util import Name, Attr, touch_import


class FixIntern(fixer_base.BaseFix):

    PATTERN = """
    power< 'intern'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(not argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    def transform(self, node, results):
        syms = self.syms
        obj = results["obj"].clone()
        if obj.type == syms.arglist:
            newarglist = obj.clone()
        else:
            newarglist = pytree.Node(syms.arglist, [obj.clone()])
        after = results["after"]
        if after:
            after = [n.clone() for n in after]
        new = pytree.Node(syms.power,
                          Attr(Name("sys"), Name("intern")) +
                          [pytree.Node(syms.trailer,
                                       [results["lpar"].clone(),
                                        newarglist,
                                        results["rpar"].clone()])] + after)
        new.set_prefix(node.get_prefix())
        touch_import(None, 'sys', node)
        return new
