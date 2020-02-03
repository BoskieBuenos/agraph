import unittest
from typing import List

from agraph.agraph_compiler import AGraphCompiler
from agraph.agraph_model import AGraphModel


class ModelType1:
    def __init__(self, id:int = 0):
        self.id = int(id)

class ModelType2:
    def __init__(self, id:int = 0):
        self.id = int(id)
        self.model_type_1_instances = []
    
    def add_mode_1_instance(self, model_type_1_instance: ModelType1) -> None:
        self.model_type_1_instances.append(model_type_1_instance)

class ModelTypeComplexConstructor:
    def __init__(self, attributes:dict):
        self.id:int = attributes['id']
        self.property:str = attributes['property']

class ModelTypeComplexConstructorAuto:
    def __init__(self):
        self.id:int = 1
        self.property:str = 'auto_property_value'

class Person:
    def __init__(self, id:int):
        self.id = id

class Organization:
    def __init__(self, id:int):
        self.id = id

# Powinno się definiować sposób konstrukcji powiązania pomiędzy konkretnymi
# typami np. Person-Organization
#
# Powinna być możliwość definicji wielu sposobów tworzenia powiązań dla tej
# samej pary typów (mogą być powiązane na różne sposoby)
#
# Jak taka definicja powinna wyglądać? - Opracować dobre API
#
# Identyfikatory na grafie mogą być też nazwami klas:
#   1. Najpierw sprawdzam czy id jest zarejestrowane
#   2. Jeśli niezarejestrowane to szukam klas o nazwie z początku (z uwzględnieniem całości)
#
# Nody na grafie nie powinny musieć mieć id
#


# Nie powinno się bezpośrenio wykorzystywać kompilatora tylko budować obiekt klasy AGraph:
# agraph = AGraph()
# agraph.add_node('id', object)
# agraph.add_relation_builder_func(Person, Organization, lambda n1, n2: expr) // nazwa jest z dupy
# agraph.add_relation_builder_func(person1, org2, lambda n1, n2: expr) // custom func dla konkretnej pary
# How to create Orgaznization-Person relation? (podaję przepisa na stworzenie/zareprezentowanie relacji)

# How to create Person-Person relation?


# self.agraph_representation = r'''
#   N0
#     \ N1--N2    N9
#      N3--N4 \  /
#     /  \ N5--N6--N10
#   N7    N8  /  \
#            N11 N12
# '''


class TestAGraphModel(unittest.TestCase):
# TODO
# 1. Define a node instance with an ID
# 2. Define a recipe for relation (between node instances) -> run recipe to construct a relation
#   - 1-1
#   - 1->1
#   - 1-*  
#   - 1->*  
#   - 1<-*
#   - *-*
#   - *->* (czy to nie *-* ?)
# 3. Define a node type with an TYPE_ID (PREFIX)
# 4. Define a recipe for relation (between generic node instances) -> run recipe to construct node instances and a relation
# 5. Define type/class object instance construction (handle different constructors parameters and id types) + try to construct default way (but safely)

    def test_should_associate_node_id_with_registered_instance(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        node_instance = ModelType1(1)
        self.agraph_model.register_node('N1', node_instance)

        self.agraph_representation = r'N1-N1'

        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertTrue(node_instance in self.graph[0])

    def test_should_use_recipe_for_relation_build(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        node_1 = ModelType1(1)
        node_2 = ModelType2(1)
        self.agraph_model.register_node('N1', node_1)
        self.agraph_model.register_node('N2', node_2)

        self.agraph_representation = r'N1-N2'

        self.agraph_compiler.register_relation_builder(ModelType1, ModelType2, lambda model_type_1_instance, model_type_2_instance: model_type_2_instance.add_mode_1_instance(model_type_1_instance))

        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertTrue(node_1 in self.graph[0] and node_2 in self.graph[0])
        self.assertTrue(node_1 in node_2.model_type_1_instances)

    def test_should_use_correct_recipe_for_relation_build(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        node_1 = ModelType1(1)
        node_2 = ModelType2(1)
        list_node = ['this_node_is_']
        self.agraph_model.register_node('N1', node_1)
        self.agraph_model.register_node('N2', node_2)
        self.agraph_model.register_node('N3', list_node)

        self.agraph_representation = r'N3-N1'

        self.agraph_compiler.register_relation_builder(ModelType1, list, lambda model_type_1_instance, list_node_instance: list_node_instance.append('beautiful'))
        self.agraph_compiler.register_relation_builder(ModelType2, list, lambda model_type_2_instance, list_node_instance: list_node_instance.append('hideous'))

        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(list_node), 2)
        self.assertEqual(list_node[0] + list_node[1], 'this_node_is_beautiful')

    # 3. Define a node type with an TYPE_ID (PREFIX)
    def test_should_be_able_to_construct_object_on_type_in_node_id_if_id_not_registered(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        self.agraph_representation = r'ModelType2-ModelType1'

        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertIn(type(self.graph[0][0]), [ModelType1, ModelType2])
        self.assertIn(type(self.graph[0][1]), [ModelType1, ModelType2])

        
    def test_should_be_able_to_construct_object_from_recipe_on_type_in_node_id_if_recipe_provided(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        self.agraph_representation = r'ModelType1-ModelTypeComplexConstructor'

        self.agraph_compiler.register_node_builder(ModelTypeComplexConstructor, lambda: ModelTypeComplexConstructor({'id': 1, 'property': 'value'}))
        
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertIn(type(self.graph[0][0]), [ModelType1, ModelTypeComplexConstructor])
        self.assertIn(type(self.graph[0][1]), [ModelType1, ModelTypeComplexConstructor])


        complex_object = next(filter(lambda node: isinstance(node, ModelTypeComplexConstructor), self.graph[0]))
        self.assertEqual(complex_object.property, 'value')
        
    def test_should_be_able_to_construct_object_from_recipe_on_type_in_node_id_with_id_suffix(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        self.agraph_representation = r'ModelType1-ModelTypeComplexConstructor60'

        self.agraph_compiler.register_node_builder(ModelTypeComplexConstructor, lambda id: ModelTypeComplexConstructor({'id': int(id), 'property': 'value'}))
        
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertIn(type(self.graph[0][0]), [ModelType1, ModelTypeComplexConstructor])
        self.assertIn(type(self.graph[0][1]), [ModelType1, ModelTypeComplexConstructor])

        complex_object = next(filter(lambda node: isinstance(node, ModelTypeComplexConstructor), self.graph[0]))
        self.assertEqual(complex_object.id, 60)
        self.assertEqual(complex_object.property, 'value')

    def test_should_construct_object_with_recipe_over_auto_detected_class(self): #TODO Consider the desired behavior!
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        self.agraph_representation = r'ModelType1-ModelTypeComplexConstructorAuto'

        self.agraph_compiler.register_node_builder(ModelTypeComplexConstructor, lambda id: ModelTypeComplexConstructor({'id': id, 'property': 'value'}))
        
        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertIn(type(self.graph[0][0]), [ModelType1, ModelTypeComplexConstructor])
        self.assertIn(type(self.graph[0][1]), [ModelType1, ModelTypeComplexConstructor])
        complex_object = next(filter(lambda node: isinstance(node, ModelTypeComplexConstructor), self.graph[0]))
        self.assertEqual(complex_object.id, 'Auto')
        self.assertEqual(complex_object.property, 'value')

    def test_should_be_able_to_construct_object_on_type_in_node_id_with_id_suffix(self):
        self.agraph_model = AGraphModel()
        self.agraph_compiler = AGraphCompiler(self.agraph_model)

        self.agraph_representation = r'ModelType260-ModelType111' # Type2 obj(id: 60) - Type1 obj(id: 11)

        self.agraph_compiler.set_representation(self.agraph_representation)
        self.graph = self.agraph_compiler.compile()

        self.assertEqual(len(self.graph), 1)
        self.assertIn(type(self.graph[0][0]), [ModelType1, ModelType2])
        self.assertIn(type(self.graph[0][1]), [ModelType1, ModelType2])
        self.assertIn(self.graph[0][0].id, [60, 11])
        self.assertIn(self.graph[0][1].id, [60, 11])

    def test_should_be_able_to_register_model_type(self):
        pass

    def test_should_be_able_to_construct_many_to_many_relation(self):
        pass
