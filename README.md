# agraph
The ***agraph*** library lets you define your testing model in visibly accessible form - an ASCII graph. For example:
```
    Employee   Employee
           \   /
Employee--Company--Employee
           /   \
    Employee   Employee
```
## tl;tr example
```python
class TestCompany(TestCase):
    def setUp(self):
        self.agraph = AGraph()
        self.agraph.register_relation_builder(Company, Employee, lambda company, employee:
            company.add_employee(employee)
        )
        
    def test_employee(self):
        self.agraph.set_representation(r'''
                Employee   Employee
                       \   /
            Employee--Company--Employee
                       /   \
                Employee   Employee
        ''')
        test_model = self.agraph.build()
        self.assertEqual(len(test_model), 6)
```
## ASCII graph representation
The graph representation consists of nodes and edges. Nodes can be explicitly registered but it is also possible to use type identifier in graph representation string.
### Nodes
#### Explicit nodes registration
Use `register_node` method to bind node id with particular object.
```python
agraph.register_node('company1', Company(id=1))
agraph.register_node('employee1', Employee(id=1, name='John Doe'))
agraph.set_representation(r'company1-employee1')
```
#### Registration of node types
Use `register_node_builder` to define a way of construction certain type of nodes.
```python
agraph.register_node_builder(Company, lambda: Company(id=1))
agraph.register_node_builder(Employee, lambda: Employee(id=1, name='John Doe'))
agraph.set_representation(r'Company-Employee')
```
#### Automatic nodes generation
When node and type is not registered, the agraph compiler would try to find matching type in program's modules. If match is found, the compiler would try to construct an instance of found type.
```python
class Company:
    def __init__(self):
        self.id=1

class Employee:
    def __init__(self):
        self.id=1
        self.name='John Doe'

agraph.set_representation(r'Company-Employee')
```
#### Nodes' ids
When a node is represented by a type in graph's representation string, the id of a created node instace can be defined as a suffix of the representation.
```
agraph.register_node_builder(Company, lambda id: Company(id=id))
agraph.register_node_builder(Employee, lambda id: Employee(id=id, name='John Doe'))
agraph.set_representation(r'Company12-Employee45')
```
The above would result in creation of `Company` object with id of `12` and `Employee` object with id of `45`.
#### Nodes separation
Two nodes must be divided by a white character or edge character if are in the same line: `Company Company` or `Company/Company`. The `CompanyCompany` can be interpreted as `Company` object with `Company` id.
However, there is no restriction in placing nodes in different neighbouring lines:
```
Company-Employee
    Company-Employee
```
### Edges
In graph's representation string edges can be represented by: `|`, `-`, `\`, `/` and the special character is `*`. None can be used in nodes identifiers.
#### Basic usages
```
    node1-node2   node1
                    |
    node1         node2   node2
         \               /
          node2     node1
```
Warning! The following is not a legal connection.
```
    node1
      \node2
```
#### Multisegment edges
Edges can be build out of multiple characters.
```
    node1---node2   node1
                      |      node2
                      |     /
    node1           node2  /
         \                /
          \          node1
            node2

```
Be careful when connecting different characters to build a complex edge. The edge bending can be done only with the use of `*` character. Therefore, the following is not legal:
```
    node1    node1-
         \          \
          |        node2
        node2

```
...and must be done with `*` connectiong different edge characters:
```
    node1    node1-*
         \          \
          *        node2
          |
        node2

```
The compiler is able to verify if an edge character is connected to a `*` connector. As a result it is possible to build complex edges very close to each other:
```
node1    node2
     \  /
      **
      ||
      |node3
     node4
```
## Instalation
The library can be installed with pip:
```
$ pip install agraph
```
