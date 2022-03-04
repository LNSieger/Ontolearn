### Adding axiom

from ontolearn import KnowledgeBase
from owlapy.model import OWLEquivalentClassesAxiom, OWLClass, IRI, OWLObjectIntersectionOf, \
        OWLObjectUnionOf, OWLObjectSomeValuesFrom, OWLObjectInverseOf, OWLObjectProperty, \
        OWLThing, OWLClassAxiom, OWLSubClassOfAxiom

kb = KnowledgeBase(path='Ontolearn/KGs/father.owl')
NS_f = "http://example.com/father#"  
manager = kb.ontology().get_owl_ontology_manager()


# name of new class
cls_a = OWLClass(IRI.create(NS_f, "AClass"))

# example concept
existingclass = OWLClass(IRI(NS_f, 'person'))

equivalent_classes_axiom_example = OWLEquivalentClassesAxiom(cls_a, existingclass)
manager.add_axiom(kb.ontology(), equivalent_classes_axiom_example)

#another
cls_b = OWLClass(IRI.create(NS_f, "BClass"))
cls_c = OWLClass(IRI.create(NS_f, "CClass"))
sub_class_axiom_example = OWLSubClassOfAxiom(cls_b, cls_c) #*
manager.add_axiom(kb.ontology(), sub_class_axiom_example)

# save as new rdfxml file
manager.save_ontology(kb.ontology(), IRI.create("file:/", "new_onto.owl"))

#* The super class must already exist for this to work. If it does not exist,
# only the first class will be added to the ontology, without being defined as subclass.
# However, if you add a class through this "error", you can afterwards run the code again with
# the new class as super class and it works. The subclass might already exist, but does not need to.




''' complicated example concept
concept_a = OWLObjectIntersectionOf(
    (OWLObjectUnionOf((OWLClass(IRI(NS_f, 'Lead')), OWLClass(IRI(NS_f, 'Selenium')))),
     OWLObjectSomeValuesFrom(
         property=OWLObjectInverseOf(OWLObjectProperty(IRI(NS_f, 'hasAtom'))),
         filler=OWLThing)))'''


'''
#Check singleperson:
from SingleInstanceChecker import checksingleperson, conceptfemale
data_file = "Ontolearn/KGs/father.owl"
father = manager.load_ontology(IRI.create("file://" + data_file))
checksingleperson(father, 'michelle', conceptfemale, NS_f) #check if Michelle is female 
'''