# GQLA - GraphQL Assistant

GQLA provides an easy way to fetch data from GraphQL api on server side.

#### Navigation:
- [Intro](#Intro)
- [Usage](#Usage)
- [Installation](#Installation)
- [Structure](#Structure)

## Intro
GQLA is published under MIT license and doesn't provide any warranty. It is single person developed package.    
`No roadmap`
`No warranty`
`No consistency`
`No active and fast responces to dev`   

## Usage
___WARNING___ : _watch carefull about your recursion depth; nodes and edges also counted as recursion level;_

Example of basic usage bellow:
```python
from gqla import GQLA

# Create a list of ignored fields (recommended values)
ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor', 'parent1', 'id']

# Create a list of fields you only want to retrieve
only = ['edges', 'node', 'code', 'name', 'StarObject', 'PlanetObject', 'orbitals']

# Create a GQLA class instance with provided settings
helper = GQLA('solar', url='localhost', port='8080', usefolder=True, only=only, ignore=ignore, recursive_depth=5)

# Set output visualization to "pretty" json
helper._pretty = True

# Gather service structure
await helper.introspection()

# Request 'allStellar' query with arguments (filters:{not: {objectType: planet}}, first: 5) and save to json file
await helper.query_one('allStellar', usefolder=True, filters={'not': {'objectType': 'planet'}}, first='5')

# Request 'allStellar' query with fields in 'only' list and arguments (first: 1) without saving to file
result = await helper.query_one('allStellar', usefolder=False, only_fields=True, first='1')

# Print result of execution
print(result)
```

## Installation
#### PIP
- pip install gqla

#### SETUP
- python setup.py install

#### Requirements:
- r/w access if using folder to save infrastucture
- python >= 3.5 
- aiohttp

## Structure
##### Classes
- `statics` - static data like intrispection query and url/query templates
- `GQLStorage` - Storage package to contain and parse GraphQL data types
- `VerticalStorage` - package to share data between vertical structures
- `Generator` - Generator package used to create queries from model
- `GQLModel` - Model package containing GraphQL service data
- `abstracts` - package containing abstracts of all classes
- `GQQStorage` - Queries storage package
- `Executor` - Executor package 
- `GQQuery` - Queries package
- `GQLA` - main class
##### Parameters:
- `usefolder` - directive to use folder to store data such as service model, querries and returned data
- `name` - name used to define service; required to create folders if `usefolder` is set
- `_subpid` - number of subtask running; No actual usage besides logging
- `ignore` - list of statements to ignore during querries generation
- `only` - list of statements to keep during querries generation
- `recursive_depth` - recursion depth limitation;
- `port` - port of `GraphQL` service
- `url` - url of `GraphQL` service

##### Methods
Notice that `async` meant to execute in execution loop;
- `introspection` - method to gather information about service;`async`
- `query_one` - method to generate and execute querries;`async`
