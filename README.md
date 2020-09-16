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
**This project not following [SOLID](https://github.com/Alenstoir/DOCVAULT/blob/master/OOP/RU/SOLID.md) yet**

## Usage
___WARNING___ : _watch carefull about your recursion depth; nodes and edges also counted as recursion level;_

Example of basic usage bellow:
```python
# Create a GQLA class instance with name 'graphql-service'
helper = GQLA('graphql-service')  # noqa
# Define url of service as localhost
helper.url = 'localhost'  
# Define port of service 
helper.port = '8086'  
# Create a list of ignored fields (recommended values)
ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor']  
# Set list to class
helper.set_ignore(ignore)
# Request introspection
await helper.introspection()
# Request query with argument useSomeArgs='false' and specify that we don't use folder to save result
result = await helper.query_one('cerviceTestData', to_file=False, useSomeArgs='false')
# Print result
print(result)
```

Notice that you can use folders to save infrastructure and results:
```python
# Create a list of ignored fields (recommended values)
ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor']  
# Create a GQLA class instance with provided settings
helper = GQLA('graphql-service', url='localhost', port=8086, ignore=ignore, usefolder=True)  # noqa
# Request introspection (saved to "gqla/graphql-service" folder)
await helper.introspection()
# Request query with argument useSomeArgs='false' and specify that we use folder to save result
result = await helper.query_one('cerviceTestData', to_file=True, useSomeArgs='false')
# Print result (can still gather result as json named _cerviceTestData from "gqla/graphql-service" folder)
print(result)
```

## Installation
#### Requirements:
- aiohttp
- r/w access if using folder to save infrastucture
- python >= 3.5 

## Structure
##### Classes
- `GQBase` - base class of `GraphQL` data
- `GQEnum` - ENUM type of `GraphQL` data
- `GQScalar` - Scalar type of `GraphQL` data
- `GQObject` - Object type of `GraphQL` data
- `GQModel` - model of `GraphQL` service
- `GQLA` - main class
##### Parameters:
- `_subpid` - number of subtask running; No actual usage besides logging
- `_model` - model of `GraphQL` service; Conains full accessible service structure; `DO NOT TOUCH`
- `_queries` - full querries in `dict` format
- `_ignore` - list of statements to ignore during querries generation
- `name` - name used to define service; required to create folders if `usefolder` is set
- `url` - url of `GraphQL` service
- `port` - port of `GraphQL` service
- `usefolder` - directive to use folder to store data such as service model, querries and returned data
- `recursive_depth` - recursion depth limitation;

##### Methods
Notice that `async` meant to execute in execution loop;
- `set_ignore` - set `_ignore` field of main class;
- `_can_query` - service method to define ability to query;`DO NOT TOUCH`
- `fetch_async` - method to fetch querry;`async`
- `query_one` - method to generate and execute querries;`async`
- `introspection` - method to gather information about service;`async`
- `create data` - method to create model from gathered information;
- `generate_querries` - method to generate querries from model;
- `subquery` - recursive method to unwrap Objects into querries;
