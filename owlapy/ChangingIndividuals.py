import os
from ontolearn import KnowledgeBase
from owlapy.model import OWLEquivalentClassesAxiom, OWLClass, IRI, OWLObjectIntersectionOf, \
        OWLObjectUnionOf, OWLObjectSomeValuesFrom, OWLObjectInverseOf, OWLObjectProperty, \
        OWLThing, OWLClassAxiom, OWLSubClassOfAxiom, OWLIndividualAxiom
from owlapy.model.__init__ import OWLClassAssertionAxiom
from owlapy.owlready2 import _base
from owlapy.owlready2._base import OWLOntologyManager_Owlready2
import importlib

    
os.chdir("//home/leo/")
   
kb = KnowledgeBase(path='Working/Ontolearn/KGs/father.owl')
NS_f = "http://example.com/father#"  
manager = kb.ontology().get_owl_ontology_manager()
    
# Add Equivalent classes axiom
cls_a = OWLClass(IRI.create(NS_f, "AClass"))
existingclass = OWLClass(IRI(NS_f, 'person'))
equivalent_classes_axiom_example = OWLEquivalentClassesAxiom(cls_a, existingclass)
manager.add_axiom(kb.ontology(), equivalent_classes_axiom_example)
manager.save_ontology(kb.ontology(), IRI.create("file:/", "new_onto.owl"))
# AClass is now in the KB and a subclass of person
    
#Check result
mgr = OWLOntologyManager_Owlready2()
onto = mgr.load_ontology(IRI.create("file://new_onto.owl" )) 
for ind in onto.classes_in_signature():
    print(ind)
    
# Add SubClass Axiom
sub_class_axiom_example = OWLSubClassOfAxiom(cls_a, existingclass)#*
manager.add_axiom(kb.ontology(), sub_class_axiom_example)
manager.save_ontology(kb.ontology(), IRI.create("file:/", "new_onto.owl"))
#* The super class must already exist for this to work. If it does not exist,
# only the first class will be added to the ontology, without being defined as subclass.

# Remove SubClass Axiom
sub_class_axiom_example = OWLSubClassOfAxiom(cls_a, existingclass)#**
manager.remove_axiom(kb.ontology(), sub_class_axiom_example)
manager.save_ontology(kb.ontology(), IRI.create("file:/", "new_onto2.owl"))

#Checking which classes exist now
mgr = OWLOntologyManager_Owlready2()
onto = mgr.load_ontology(IRI.create("file://new_onto2.owl" )) 
for ind in onto.classes_in_signature():
    print(ind)

'''The following does not work yet

indi = OWLIndividualAxiom(IRI.create(NS_f, "anna"))
iclass = OWLClass(IRI(NS_f, 'female'))
unclass = OWLClassAssertionAxiom(indi, iclass)
manager.remove_axiom(kb.ontology(), unclass)
manager.save_ontology(kb.ontology(), IRI.create("file:/", "new_onto2.owl"))
'''

'''
#Check if an individual belongs to a concept:
from SingleInstanceChecker import checksingleperson, conceptfemale
data_file = "Ontolearn/KGs/father.owl"
father = manager.load_ontology(IRI.create("file://" + data_file))
checksingleperson(father, 'michelle', conceptfemale, NS_f) #check if Michelle is female 
'''