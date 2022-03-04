# -*- coding: utf-8 -*-

import types
from functools import singledispatchmethod
from typing import List, Callable
from owlapy import namespaces
from owlapy.io import OWLObjectRenderer
from owlapy.model import OWLLiteral, OWLNaryDataRange, OWLObject, OWLClass, OWLObjectSomeValuesFrom, \
    OWLObjectAllValuesFrom, OWLObjectUnionOf, OWLBooleanClassExpression, OWLNaryBooleanClassExpression, \
    OWLObjectIntersectionOf, OWLObjectComplementOf, OWLObjectInverseOf, OWLClassExpression, OWLRestriction, \
    OWLObjectMinCardinality, OWLObjectExactCardinality, OWLObjectMaxCardinality, OWLObjectHasSelf, OWLObjectHasValue, \
    OWLObjectOneOf, OWLNamedIndividual, OWLEntity, IRI, OWLPropertyExpression, OWLDataSomeValuesFrom, \
    OWLFacetRestriction, OWLDatatypeRestriction, OWLDatatype, OWLDataAllValuesFrom, OWLDataComplementOf, \
    OWLDataUnionOf, OWLDataIntersectionOf, OWLDataHasValue, OWLDataOneOf, OWLDataMaxCardinality, \
    OWLDataMinCardinality, OWLDataExactCardinality

def _simple_short_form_provider(e: OWLEntity) -> str:
    iri: IRI = e.get_iri()
    sf = iri.get_short_form()
    for ns in [namespaces.XSD, namespaces.OWL, namespaces.RDFS, namespaces.RDF]:
        if iri.get_namespace() == ns:
            return "%s:%s" % (ns.prefix, sf)
    else:
        return sf

class Intersection_splitter(OWLObjectRenderer):
    """Manchester Syntax renderer for OWL Objects"""
    __slots__ = '_sfp', '_no_render_thing'

    _sfp: Callable[[OWLEntity], str]

    def __init__(self, short_form_provider: Callable[[OWLEntity], str] = _simple_short_form_provider,
                 no_render_thing=False):
        """Create a new Manchester Syntax renderer
        Args:
            short_form_provider: custom short form provider
            no_render_thing: disable manchester rendering for Thing and Nothing
        """
        self._sfp = short_form_provider
        self._no_render_thing = no_render_thing

    def set_short_form_provider(self, short_form_provider: Callable[[OWLEntity], str]) -> None:
        self._sfp = short_form_provider

    @singledispatchmethod
    def render(self, o: OWLObject) -> str:
        assert isinstance(o, OWLNaryBooleanClassExpression), f"Tried to render non-OWLIntersection-Object {o} of {type(o)}"
            
    
    def _split_intersection(self, c: OWLNaryBooleanClassExpression) -> List[str]:
        print("splitting starts")
        global splitlist
        splitlist = []
        for i in c.operands():
            splitlist.append(i)
        return splitlist

### gegeben sei Konjunktive Normalform
    @render.register
    def _(self, c: OWLObjectIntersectionOf) -> str:
        if True:
            print("splitting will start")
            self._split_intersection(c)
        else: print("No Intersection")
      
        
###    
if __name__ == "__main__":
    
    rendy = CounterfactualOWLSyntaxOWLObjectRenderer()

    #Intersection_splitter
    
    k = 1
    for j in listy:
        print(k)
        k = k+1
        print(j)
    
    for j in listy:
        print(rendy.render(j))
