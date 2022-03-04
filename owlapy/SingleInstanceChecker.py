import os
from owlapy.fast_instance_checker import OWLReasoner_FastInstanceChecker
from owlapy.model import IRI, OWLNamedIndividual
from owlapy.owlready2 import OWLOntologyManager_Owlready2, OWLReasoner_Owlready2
from owlapy.render import ManchesterOWLSyntaxOWLObjectRenderer, DLSyntaxObjectRenderer  # noqa: F401
from owlapy.model import OWLObjectComplementOf, OWLClass
from typing import DefaultDict, Iterable, Dict, Mapping, Set, Type, TypeVar, Union, Optional, FrozenSet
from owlapy.model import OWLEquivalentClassesAxiom, OWLObjectIntersectionOf, OWLObjectUnionOf, OWLObjectSomeValuesFrom, OWLObjectInverseOf, OWLObjectProperty, OWLThing

#function that will be feeded the ontology, name of person, concept and namespace
def checksingleperson(onto, name, concept, NS):
    person = OWLNamedIndividual(IRI(NS, name))
    #create reasoner that has the ability to examine instances
    base_reasoner = OWLReasoner_Owlready2(onto)
    reasoner = OWLReasoner_FastInstanceChecker(onto, base_reasoner, negation_default=True)
    conceptiri= OWLClass(IRI.create(NS, concept))
    conceptlist = frozenset(reasoner.instances(conceptiri))
    print(frozenset(reasoner.instances(conceptiri)))
    if person in conceptlist:
        print(name + " belongs to the concept.")
    else:
        print(name + " does not belong to the concept.")


conceptfemale = 'female'
conceptmale = 'male'
conceptdiverse = 'diverse'
    

if __name__ == "__main__":

    os.chdir("/home/leo")
    #loading Ontology manager
    
    #define concept supposed to be checked

    
    
    #load dataset supposed to be checked and its namespace
    mgr_f = OWLOntologyManager_Owlready2()
    data_file = "Ontolearn/KGs/father.owl"
    father = mgr_f.load_ontology(IRI.create("file://" + data_file))
    NS_f = "http://example.com/father#"  
    
    #check concepts
    checksingleperson(father, 'michelle', conceptfemale, NS_f) #check if Michelle is female 
    checksingleperson(father, 'michelle', conceptmale, NS_f) #check if Michelle is male
    
    checksingleperson(father, 'martin', conceptfemale, NS_f) #check if Martin is female 
    checksingleperson(father, 'martin', conceptmale, NS_f) #check if Martin is male
    
    
    ################## Introduce new person #########
    
    mgr_e = OWLOntologyManager_Owlready2()
    data_file2 = "ebru.owl"
    ebru = mgr_e.load_ontology(IRI.create("file://" + data_file2))
    NS_e = "http://example.com/ebru#"
    
    checksingleperson(ebru, 'ebru', conceptmale, NS_e) #is ebru male?
    checksingleperson(ebru, 'ebru', conceptfemale, NS_e) #is ebru female?
    
    
    ### Introduce another person ####
    mgr_l = OWLOntologyManager_Owlready2()
    laura = mgr_l.load_ontology(IRI.create("file://laura.owl"))
    NS_l = "http://example.com/laura#"
    
    #is laura male?
    checksingleperson(laura, 'laura', conceptfemale, NS_l)
    checksingleperson(laura, 'laura', conceptmale, NS_l)
    checksingleperson(laura, 'laura', conceptdiverse, NS_l)
    
    
    
    #### Manipulating ebru
    
    # Find concept parts in ebru's file and change parts to Complement
    
    with open('ebru.owl', 'r') as file :
        filedata = file.read()
    
    # Replace the target string
    filedata = filedata.replace('<rdf:type rdf:resource="http://example.com/ebru#female"/>',
                                '<rdf:type rdf:resource="http://example.com/ebru#male"/>')
    #Es wäre interessanter, female zu ComplementOf(female) ändern zu können
    
    # Write the file out again
    with open('ebrucount.owl', 'w') as file:
      file.write(filedata)
    
    mgr_ec = OWLOntologyManager_Owlready2()
    data_file3 = "ebrucount.owl"
    ebrucount = mgr_ec.load_ontology(IRI.create("file://" + data_file3))
    NS_e = "http://example.com/ebru#"
    
    checksingleperson(ebru, 'ebru', conceptmale, NS_e) #is ebrucount male?
    checksingleperson(ebru, 'ebru', conceptfemale, NS_e) #is ebrucount female?
    
    checksingleperson(ebrucount, 'ebru', conceptmale, NS_e) #is ebrucount male?
    checksingleperson(ebrucount, 'ebru', conceptfemale, NS_e) #is ebrucount female?
    
    # Hier wird es erst interessant, wenn der concept learner ein Konzept lernen kann, das
    # zB lautet "(A) ODER (B)", sodass man zu dem Ergebnis kommen könnte, dass A zu ändern nicht reicht, sondern
    # auch B geändert werden muss
    


'''Ignore the following


base_reasonert = OWLReasoner_Owlready2(ebrucount)
reasonert = OWLReasoner_FastInstanceChecker(ebrucount, base_reasonert, negation_default=True)
conceptirit1= OWLClass(IRI.create(NS_e, 'female'))
conceptirit2= OWLClass(IRI.create(NS_e, 'male'))
conceptlistt1 = frozenset(reasonert.instances(conceptirit1))
conceptlistt2 = frozenset(reasonert.instances(conceptirit2))


print(set(reasonert.instances(conceptirit1)))
print(set(reasonert.instances(conceptirit2)))


base_reasonerf = OWLReasoner_Owlready2(ebru)
reasonerf = OWLReasoner_FastInstanceChecker(ebru, base_reasonerf, negation_default=True)
conceptirif1= OWLClass(IRI.create(NS_e, 'female'))
conceptirif2= OWLClass(IRI.create(NS_e, 'male'))
conceptlistf1 = frozenset(reasonerf.instances(conceptirif1))
conceptlistf2 = frozenset(reasonerf.instances(conceptirif2))

print(set(reasonerf.instances(conceptirif1)))
print(set(reasonerf.instances(conceptirif2)))
'''



'''
Some tests, might not work anymore 

print(frozenset(father.individuals_in_signature()))
print(father.get_ontology_id())


##
print(father.instances())

from owlready2 import *

onto2 = get_ontology("file://KGs/father.owl").load()
print(father.classes()) #doesn't work
print(onto2.individuals()) #doesn't work
print(onto2.base.iri) #doesn't work
print(onto2["hasChild"])
list(onto2.classes())
onto2.search(iri = "*a")

with onto2:
    class diverse(person):
        pass
    
newperson = diverse("laura")

print(newperson.name)
print(newperson.iri)
print(onto2.laura)
print(onto2.notexistent) #outputs None, which is fine

onto2.search(iri = "*a")

onto3 = mgr.load_ontology(onto2)

'''