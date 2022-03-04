
""" 
This is an adaptable example script for running a concept learning algorithm using Ontolearn.
You do this by providing an owl data file and positive and negative examples for supervised learning.
The algorithm outputs possible concept descriptions,
different measures of how well each fits the positive and negative examples provided and additional information about the search.
""" 

from ontolearn import KnowledgeBase
from ontolearn.concept_learner import CELOE
from ontolearn.learning_problem import PosNegLPStandard
from ontolearn.metrics import Accuracy, F1
from ontolearn.utils import setup_logging, read_individuals_file
from owlapy.fast_instance_checker import OWLReasoner_FastInstanceChecker
from owlapy.model import IRI
from owlapy.owlready2 import OWLOntologyManager_Owlready2, OWLReasoner_Owlready2
from owlapy.render import ManchesterOWLSyntaxOWLObjectRenderer, DLSyntaxObjectRenderer  # noqa: F401 #Both are imported, either one can be used
from owlapy.namespaces import Namespaces
from owlapy.model import OWLNamedIndividual
import os
import sys

os.chdir("//home/leo/")


def run(data_file, positive_examples, negative_examples):               
    mgr = OWLOntologyManager_Owlready2()                                
    onto = mgr.load_ontology(IRI.create("file://" + data_file))         
    base_reasoner = OWLReasoner_Owlready2(onto)                         
    reasoner = OWLReasoner_FastInstanceChecker(onto, base_reasoner,     
                                               negation_default=True)

    kb = KnowledgeBase(ontology=onto, reasoner=reasoner)                
    pos = positive_examples                                             
    neg = negative_examples                                             # The examples will be added beneath

    lp = PosNegLPStandard(pos, neg)                                     # Catches the pos. and neg. examples

    pred_acc = Accuracy()                                               # The Accuracy function will be used for the output
    f1 = F1()                                                           # Will be needed for the output
    alg = CELOE(kb,                                                     # We chose the algorithm we want to use, in the example CELOE.
                max_runtime=600,
                max_num_of_concepts_tested=1_000_000)                   # We limit the calculation duration
    alg.fit(lp)                                                         # We fit the algorithm
    render = ManchesterOWLSyntaxOWLObjectRenderer()
    # render = DLSyntaxObjectRenderer()                                 # The renderer translates the concept to description logic
    i = 1
    for h in alg.best_hypotheses(1):                                    # Prints out best result
        pred_acc_score = kb.evaluate_concept(h.concept, pred_acc, lp.encode_kb(kb)).q
        f1_score = kb.evaluate_concept(h.concept, f1, lp.encode_kb(kb)).q
        global bestconcept
        bestconcept = h.concept
        print(f'{render.render(h.concept)} is the concept description with the highest accuracy.')
        i += 1                                                          

data_file = "Ontolearn/KGs/father.owl" # Provide the owl file



NS = Namespaces('ex', 'http://example.com/father#')                    

positive_examples = {OWLNamedIndividual(IRI.create(NS, 'stefan')),
                     OWLNamedIndividual(IRI.create(NS, 'markus')),
                     OWLNamedIndividual(IRI.create(NS, 'martin'))}     # Pos. examples (in this example: People in the KB who are fathers)
negative_examples = {OWLNamedIndividual(IRI.create(NS, 'heinz')),
                     OWLNamedIndividual(IRI.create(NS, 'anna')),
                     OWLNamedIndividual(IRI.create(NS, 'michelle'))}   # Neg. examples (in this example: People in the KB who are NOT fathers)


run(data_file, positive_examples, negative_examples)                   # run


###


