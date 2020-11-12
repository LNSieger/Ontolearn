from collections import defaultdict
from owlready2 import Ontology, World
import owlready2
from .concept_generator import ConceptGenerator
from .concept import Concept
from typing import Dict, Tuple, Set, Generator, Iterable, AnyStr, List
from .util import parametrized_performance_debugger, get_full_iri
from .abstracts import AbstractKnowledgeBase
from .data_struct import PropertyHierarchy
import warnings

warnings.filterwarnings("ignore")


class KnowledgeBase(AbstractKnowledgeBase):
    """Knowledge Base Class representing Tbox and Abox along with concept hierarchies"""

    def __init__(self, path, min_size_of_concept=1):
        super().__init__()
        self.path = path
        self.onto = World().get_ontology(self.path).load(reload=True)
        self.property_hierarchy = PropertyHierarchy(self.onto)
        self.name = self.onto.name
        self.parse()
        # @todo str_to_instance_obj and obj_to_str_iri_instances used? if so where and better namings?
        self.str_to_instance_obj = dict(zip([get_full_iri(i) for i in self.thing.instances], self.thing.instances))
        self.obj_to_str_iri_instances = dict(
            zip(self.str_to_instance_obj.values(), self.str_to_instance_obj.keys()))
        self.idx_of_instances = dict(zip(self.thing.instances, range(len(self.str_to_instance_obj))))
        self.min_size_of_concept = min_size_of_concept
        self.max_size_of_concept = len(self.thing.instances) * 1
        self.concept_generator = ConceptGenerator(concepts=self.concepts,
                                                  thing=self.thing,
                                                  nothing=self.nothing,
                                                  onto=self.onto,
                                                  min_size_of_concept=self.min_size_of_concept,
                                                  max_size_of_concept=self.max_size_of_concept)

    def clean(self):
        self.thing.embeddings = None
        self.nothing.embeddings = None
        self.concept_generator.clean()

    def __build_hierarchy(self, onto: Ontology) -> None:
        """
        Builds concept sub and super classes hierarchies.

        1) self.top_down_concept_hierarchy is a mapping from Concept objects to a set of Concept objects that are
        direct subclasses of given Concept object.

        2) self.down_top_concept_hierarchy is a mapping from Concept objects to set of Concept objects that are
        direct superclasses of given Concept object.
        """

        self.concepts, self.thing, self.nothing = self.build_concepts_mapping(onto)
        self.individuals = self.thing.instances
        self.down_top_concept_hierarchy[self.thing] = set()
        # T should not subsume itself.
        self.top_down_concept_hierarchy[self.thing] = {_ for _ in self.concepts.values() if _ is not self.thing}

        for str_, concept_A in self.concepts.items():  # second loop over concepts in the execution,

            for desc in concept_A.owl.descendants(include_self=False, world=onto.world):

                wrapped_desc = self.concepts[desc.namespace.base_iri + desc.name]

                # Include all sub class that are wrapped with AtomicConcept class into hierarchy.
                self.top_down_concept_hierarchy[concept_A].add(wrapped_desc)
                if len(wrapped_desc.owl.descendants(
                        include_self=False, world=onto.world)) == 0:  # if no descendant, then it is a leaf concept.
                    self.concepts_to_leafs.setdefault(concept_A, set()).add(wrapped_desc)

            for ans in concept_A.owl.ancestors(include_self=False):
                wrapped_ans = self.concepts[ans.namespace.base_iri + ans.name]
                # Include all superclasses into down top hierarchy
                self.down_top_concept_hierarchy[concept_A].add(wrapped_ans)

            for subs in concept_A.owl.subclasses(world=onto.world):  # returns direct subclasses
                if concept_A.owl == subs:
                    continue
                wrapped_subs = self.concepts[subs.namespace.base_iri + subs.name]

                self.top_down_direct_concept_hierarchy[concept_A].add(wrapped_subs)
                self.down_top_direct_concept_hierarchy[wrapped_subs].add(concept_A)

    def parse(self):
        """
        Top-down and bottom up hierarchies are constructed from from owlready2.Ontology
        """
        self.__build_hierarchy(self.onto)

    @staticmethod
    def build_concepts_mapping(onto: Ontology) -> Tuple[Dict, Concept, Concept]:
        """
        Construct a mapping from full_iri to corresponding Concept objects.

        concept.namespace.base_iri + concept.name
        mappings from concepts uri to concept objects
            1) full_iri:= owlready2.ThingClass.namespace.base_iri + owlready2.ThingClass.name
            2) Concept:
        """
        concepts = dict()
        individuals = set()
        T = Concept(owlready2.Thing, kwargs={'form': 'Class'}, world=onto.world)
        bottom = Concept(owlready2.Nothing, kwargs={'form': 'Class'}, world=onto.world)
        # TODO: Think about removing owlready2 instances and use string representation.
        for i in onto.classes():
            temp_concept = Concept(i, kwargs={'form': 'Class'}, world=onto.world)
            concepts[temp_concept.full_iri] = temp_concept
            individuals.update(temp_concept.instances)
        try:
            assert T.instances  # if empty throw error.
            assert individuals.issubset(T.instances)
        except AssertionError:
            print(
                'Sanity checking failed: owlready2.Thing does not contain any individual. To allivate this issue, we explicitly assign all individuals/instances to concept T.')
            T.instances = individuals

        concepts[T.full_iri] = T
        concepts[bottom.full_iri] = bottom
        return concepts, T, bottom

    @staticmethod
    def apply_type_enrichment_from_iterable(concepts: Iterable[Concept], world):
        """
        Extend ABOX by
        (1) Obtaining all instances of selected concepts.
        (2) For all instances in (1) include type information into ABOX.
        @param concepts:
        @return:
        """
        for c in concepts:
            for ind in c.owl.instances(world=world):
                ind.is_a.append(c.owl)

    @staticmethod
    def apply_type_enrichment(concept: Concept):
        for ind in concept.instances:
            ind.is_a.append(concept.owl)

    def convert_uri_instance_to_obj(self, str_ind: str):
        """
        str_ind indicates string representation of an individual.
        """
        try:
            assert isinstance(str_ind, str)
        except AssertionError:
            AssertionError('{0} is expected to be a string but it is  ****{1}****'.format(str_ind, type(str_ind)))
        try:
            return self.str_to_instance_obj[str_ind]
        except KeyError:
            KeyError('{0} is not found in vocabulary of URI instances'.format(str_ind))

    def convert_uri_instance_to_obj_from_iterable(self, str_individuals: Iterable[AnyStr]) -> List:
        return [self.convert_uri_instance_to_obj(i) for i in str_individuals]

    def convert_owlready2_individuals_to_uri(self, instance):
        return self.obj_to_str_iri_instances[instance]

    def convert_owlready2_individuals_to_uri_from_iterable(self, l: Iterable) -> List:
        return [self.convert_owlready2_individuals_to_uri(i) for i in l]

    def set_min_size_of_concept(self, n):
        self.min_size_of_concept = n

    def max_size_of_concept(self, n):
        self.max_size_of_concept = n

    @staticmethod
    def is_atomic(c: owlready2.entity.ThingClass):
        assert isinstance(c, owlready2.entity.ThingClass)
        if '¬' in c.name and not (' ' in c.name):
            return False
        elif ' ' in c.name or '∃' in c.name or '∀' in c.name:
            return False
        else:
            return True

    def get_leaf_concepts(self, concept: Concept):
        """ Return : { x | (x subClassOf concept) AND not exist y: y subClassOf x )} """
        for leaf in self.concepts_to_leafs[concept]:
            yield leaf

    def negation(self, concept: Concept):
        """ Return a Concept object that is a negation of given concept."""
        yield self.concept_generator.negation(concept)

    @parametrized_performance_debugger()
    def negation_from_iterables(self, s: Generator):
        """ Return : { x | ( x \equv not s} """
        for item in s:
            yield self.concept_generator.negation(item)

    @parametrized_performance_debugger()
    def get_direct_sub_concepts(self, concept: Concept):
        """ Return : { x | ( x subClassOf concept )} """
        for v in self.top_down_direct_concept_hierarchy[concept]:
            yield v

    def get_all_sub_concepts(self, concept: Concept):
        """ Return : { x | ( x subClassOf concept ) OR ..."""
        for v in self.top_down_concept_hierarchy[concept]:
            yield v

    def get_direct_parents(self, concept: Concept):
        """ Return : { x | (concept subClassOf x)} """
        for direct_parent in self.down_top_direct_concept_hierarchy[concept]:
            yield direct_parent

    def most_general_existential_restrictions(self, concept: Concept):

        for prob in self.property_hierarchy.get_most_general_property():
            yield self.concept_generator.existential_restriction(concept, prob)

    def most_general_universal_restriction(self, concept: Concept) -> Concept:
        assert isinstance(concept, Concept)
        for prob in self.property_hierarchy.get_most_general_property():
            yield self.concept_generator.universal_restriction(concept, prob)

    def union(self, conceptA: Concept, conceptB: Concept) -> Concept:
        """Return a concept c == (conceptA OR conceptA)"""
        assert isinstance(conceptA, Concept)
        assert isinstance(conceptB, Concept)
        return self.concept_generator.union(conceptA, conceptB)

    def intersection(self, conceptA: Concept, conceptB: Concept) -> Concept:
        """Return a concept c == (conceptA AND conceptA)"""
        assert isinstance(conceptA, Concept)
        assert isinstance(conceptB, Concept)
        return self.concept_generator.intersection(conceptA, conceptB)

    def existential_restriction(self, concept: Concept, property_) -> Concept:
        """Return a concept c == (Exist R.C)"""
        assert isinstance(concept, Concept)
        return self.concept_generator.existential_restriction(concept, property_)

    def universal_restriction(self, concept: Concept, property_) -> Concept:
        """Return a concept c == (Forall R.C)"""
        assert isinstance(concept, Concept)
        return self.concept_generator.universal_restriction(concept, property_)

    def num_concepts_generated(self):

        return len(self.concept_generator.log_of_universal_restriction) + len(
            self.concept_generator.log_of_existential_restriction) + \
               len(self.concept_generator.log_of_intersections) + len(self.concept_generator.log_of_unions) + \
               len(self.concept_generator.log_of_negations) + len(self.concepts)

    def get_all_concepts(self):
        return self.concepts.values()
