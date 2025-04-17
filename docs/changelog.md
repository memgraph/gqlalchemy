# Changelog

## v1.7.0 - March 25, 2025

### Improvements
- Updated `to_cypher_value()` and `escape_value()` to use `json.dumps()` instead of `fstring`. This solves an issue when there is a combination of characters in a string that need to be both escaped (e.g., an apostrophe ') and not escaped (e.g. newlines, \n) and allows flexibility in how the developer instantiates their strings and whether they chose to escape their strings ahead of sending them through to Cypher or not. (https://github.com/memgraph/gqlalchemy/pull/341)
- Bumped up dependencies to allow users to use higher, more recent versions of their favorite libraries, without making breaking changes for those who have lower versions in their environments (https://github.com/memgraph/gqlalchemy/pull/334)
- Updated query modules signatures to keep them up to date (https://github.com/memgraph/gqlalchemy/pull/335)

## v1.6.0 - July 10, 2024

### Features and improvements
- Added `SIMILAR` operator to query builder (https://github.com/memgraph/gqlalchemy/pull/304)
- Better documented how to load CSV from a remote location: to load CSV from a remote location, provide a URL as a path (https://github.com/memgraph/gqlalchemy/pull/305)
- You can now add relationship properties in many-to-many mapping when importing a CSV file (https://github.com/memgraph/gqlalchemy/pull/306)
- Added getter and setter for Memgraph storage modes (https://github.com/memgraph/gqlalchemy/pull/309)
- Added `get_transactions()` and `terminate_transactions()` methods for easier transaction management (https://github.com/memgraph/gqlalchemy/pull/310)
- Added support for `ZonedDateTime` data type (https://github.com/memgraph/gqlalchemy/pull/312)

## v1.5.1 - January 8, 2024

### Updates

- Support `pydantic` versions >= 2.3.0, < 3.0.0 (https://github.com/memgraph/gqlalchemy/pull/298)
- Support `pymgclient` versions >= 1.3.1, < 2.0.0 , `neo4j` versions >= 4.4.3, < 5.0.0, `pytest-flake8` versons >= 1.0.7, < 2.0.0 (https://github.com/memgraph/gqlalchemy/pull/299)
 
## v1.5.0 - September 22, 2023

### Features and improvements

- Added `get_or_create()` metod for `Node` and `Relationship` to simplify merging nodes and relationships (https://github.com/memgraph/gqlalchemy/pull/244)
- Added spelling fixes (https://github.com/memgraph/gqlalchemy/pull/251)
- Turned `docker` into an optional dependency (https://github.com/memgraph/gqlalchemy/pull/279)

### Bug fixes

- Fixed typing for `get_triggers` method (https://github.com/memgraph/gqlalchemy/pull/260)

### Updates

- Added support for Python 3.11 on Linux (https://github.com/memgraph/gqlalchemy/pull/281)
- Added support for Python 3.10 on Windows (https://github.com/memgraph/gqlalchemy/pull/281)
- Relaxed `neo4j` dependency (https://github.com/memgraph/gqlalchemy/pull/263/files)
- Bumped `pydantic` to v2 (https://github.com/memgraph/gqlalchemy/pull/278)

**Special thanks to all our outside contributors for their efforts!** 👏

!!! note
    We are hoping to have full support for Python 3.11 soon. Please [open an issue](https://github.com/memgraph/gqlalchemy/issues) if you have any blockers with the current update.

## v1.4.1 - April 19, 2023

### Features and improvements

- Installing and testing GQLAlchemy is now easier because Apache Arrow, PyTorch Geometric and DGL dependencies have been made optional. [#235](https://github.com/memgraph/gqlalchemy/pull/235)

### Bug fixes

- Removed unnecessary extra argument in the call of the `escape_value` method and fixed a bug in query creation for the `Map` property type. [#198](https://github.com/memgraph/gqlalchemy/pull/198/files)

## v1.4 - March 10, 2023

### Features and improvements

- Data from Memgraph can now be [imported from](reference/gqlalchemy/transformations/importing/graph_importer.md) and [exported to](reference/gqlalchemy/transformations/export/graph_transporter.md) `NetworkX`, `DGL` and `PyG` graph formats. [#215](https://github.com/memgraph/gqlalchemy/pull/215)
- Now you can execute procedures from query modules on a subgraph [using the project feature](how-to-guides/query-builder/graph-projection.md). [#210](https://github.com/memgraph/gqlalchemy/pull/210)
- Now you can pass values from Python variables as parameters in Cypher queries. [#217](https://github.com/memgraph/gqlalchemy/pull/217)
- Besides BSF, DSF and WSHORTEST, now you can also run the All shortest paths algorithm with GQLAlchemy. [#200](https://github.com/memgraph/gqlalchemy/pull/200)

## v1.3.3 - Dec 15, 2022

### Bug fixes

- Added initial support for NumPy arrays (`ndarray`) and scalars (`generic`) [#208](https://github.com/memgraph/gqlalchemy/pull/208)

## v1.3.2 - Sep 15, 2022

### Bug fixes

- Fixed Unicode serialisation [#189](https://github.com/memgraph/gqlalchemy/pull/189)
- Fixed `GQLAlchemyWaitForConnectionError` and `GQLAlchemyDatabaseError` [#188](https://github.com/memgraph/gqlalchemy/pull/188)
- Fixed `Datetime` serialisation [#185](https://github.com/memgraph/gqlalchemy/pull/185)

### Updates

- Bumped `pyarrow` [#193](https://github.com/memgraph/gqlalchemy/pull/193)
- Updated `poetry` to 1.2.0 and `pymgclient` to 1.3.1 [#191](https://github.com/memgraph/gqlalchemy/pull/191)
- Updated all dependencies [#194](https://github.com/memgraph/gqlalchemy/pull/194)

## v1.3 - Jun 14, 2022

!!! warning ### Breaking Changes

    - Renamed keyword argument `edge_label` to `relationship_type` in `to()` and `from()` methods in the query builder. [#145](https://github.com/memgraph/gqlalchemy/pull/145)

### Major Features and Improvements

- Added option to suppress warning `GQLAlchemySubclassNotFoundWarning`. [#121](https://github.com/memgraph/gqlalchemy/pull/121)
- Added the possibility to import `Field` from `gqlalchemy.models`. [#122](https://github.com/memgraph/gqlalchemy/pull/122)
- Added `set_()` method to the query builder. [#128](https://github.com/memgraph/gqlalchemy/pull/128)
- Added wrapper class for query modules. [#130](https://github.com/memgraph/gqlalchemy/pull/130)
- Added `foreach()` method to the query builder. [#135](https://github.com/memgraph/gqlalchemy/pull/135)
- Added `load_csv()` and `return()` methods from the query builder to base classes list. [#139](https://github.com/memgraph/gqlalchemy/pull/139)
- Added new argument types in `return_()`, `yield_()` and `with_()` methods in the query builder. [#146](https://github.com/memgraph/gqlalchemy/pull/146)
- Added `IntegratedAlgorithm` class instance as argument in `to()` and `from()` methods in the query builder. [#141](https://github.com/memgraph/gqlalchemy/pull/141)
- Extended `IntegratedAlgorithm` class with the Breadth-first search algorithm. [#142](https://github.com/memgraph/gqlalchemy/pull/142)
- Extended `IntegratedAlgorithm` class with the Weighted shortest path algorithm. [#143](https://github.com/memgraph/gqlalchemy/pull/143)
- Extended `IntegratedAlgorithm` class with the Depth-first search algorithm. [#144](https://github.com/memgraph/gqlalchemy/pull/144)
- Removed the usage of `sudo` from the `instance_runner` module. [#148](https://github.com/memgraph/gqlalchemy/pull/148)
- Added support for Neo4j in the Object-Graph Mapper and the query builder. [#149](https://github.com/memgraph/gqlalchemy/pull/149)
- Changed string variables for Blob and S3 keyword arguments. [#151](https://github.com/memgraph/gqlalchemy/pull/151)
- Added variable support for node and relationship properties. [#154](https://github.com/memgraph/gqlalchemy/pull/154)
- Added `Tuple` as new argument type in query modules. [#155](https://github.com/memgraph/gqlalchemy/pull/155/)
- Changed `host` and `port` `Memgraph` properties to readonly. [#156](https://github.com/memgraph/gqlalchemy/pull/156)
- Changed `Memgraph.new_connection()` to be a private method. [#157](https://github.com/memgraph/gqlalchemy/pull/157)
- Added `push()` query modules for Kafka streams and Power BI. [#158](https://github.com/memgraph/gqlalchemy/pull/158)
- Added argument `lazy` for configuring lazy loading in the `Memgraph` class. [#159](https://github.com/memgraph/gqlalchemy/pull/159)
- Added `datetime` support for property types. [#161](https://github.com/memgraph/gqlalchemy/pull/161)
- Added `Operator` enum which can be used as `operator` value in `set_()` and `where()` methods in the query builder. [#165](https://github.com/memgraph/gqlalchemy/pull/165)
- Added an extension to the `QueryBuilder` class to support and autocomplete integrated and MAGE query modules. [#168](https://github.com/memgraph/gqlalchemy/pull/168)

### Bug fixes

- Fixed the unbound variable error in the return statement of the Cypher query in `memgraph.save_relationship_with_id()`. [#166](https://github.com/memgraph/gqlalchemy/pull/166)
- Fixed checking if `None` for `Optional` properties. [#167](https://github.com/memgraph/gqlalchemy/pull/167)

## v1.2 - Apr 12, 2022

!!! warning ### Breaking Changes

    - Ordering query results as in GQLAlchemy older than 1.2 will not be possible.
    - `where()`, `and_where()` and `or_where()` methods can't be used as in
      GQLAlchemy older than 1.2.
    - Setting up the `bootstrap_servers` argument when creating a stream as in
      GQLAlchemy older than 1.2 will not be possible.

### Major Features and Improvements

- Improved `where()`, `and_where()`, `or_where()` and `xor_where()` methods. [#114](https://github.com/memgraph/gqlalchemy/pull/114)
- Added `where_not()`, `and_not()`, `or_not()` and `xor_not()` methods. [#114](https://github.com/memgraph/gqlalchemy/pull/114)
- Improved `order_by()` method from query builder by changing its argument types. [#114](https://github.com/memgraph/gqlalchemy/pull/114)
- Added Docker and Binary Memgraph instance runners. [#91](https://github.com/memgraph/gqlalchemy/pull/91)
- Added methods for dropping all indexes (`drop_all_indexes()`) and dropping all triggers (`drop_all_triggers()`). [#100](https://github.com/memgraph/gqlalchemy/pull/100)
- Added table to graph importer and Amazon S3 importer. [#100](https://github.com/memgraph/gqlalchemy/pull/100)
- Added Azure Blob and local storage importers. [#104](https://github.com/memgraph/gqlalchemy/pull/104)
- Added an option to create a label index. [#113](https://github.com/memgraph/gqlalchemy/pull/113)
- Added batch save methods for saving nodes (`save_nodes()`) and saving relationships (`save_relationships()`). [#106](https://github.com/memgraph/gqlalchemy/pull/106)
- Added label filtering in `where()` method in query builder. [#103](https://github.com/memgraph/gqlalchemy/pull/103)
- Added support for creating a trigger without `ON` keyword in query builder. [#90](https://github.com/memgraph/gqlalchemy/pull/90)
- Added `execute()` option in query builder. [#92](https://github.com/memgraph/gqlalchemy/pull/92)
- Added `load_csv()` and `xor_where()` methods to query builder. [#90](https://github.com/memgraph/gqlalchemy/pull/90)

### Bug fixes

- Fixed `save_node_with_id()` signature in the `save_node()` method. [#109](https://github.com/memgraph/gqlalchemy/pull/109)
- Constraints and indexes defined in `Field` now work correctly. Before, when they were added to the `Field` of the property, they were always set to `True`, regardless of their actual value. [#90](https://github.com/memgraph/gqlalchemy/pull/90)
- Fixed label inheritance to get all labels of base class. [#105](https://github.com/memgraph/gqlalchemy/pull/105)
- Removed extra argument called `optional` from the `Merge` class. [#118](https://github.com/memgraph/gqlalchemy/pull/118)
- Removed unnecessary quotes from the `bootstraps_servers` argument when creating a stream. [#98](https://github.com/memgraph/gqlalchemy/pull/98)

## v1.1 - Jan 19, 2022

### Major Features and Improvements

- Added graph schema definition and validation.
- Added new methods to the query builder: `merge()`, `create()`,
  `unwind()`,`with_()`, `return_()`, `yield_()`, `order_by()`, `limit()`,
  `skip()`, `call()`, `delete()` and `remove()`.
- Added on-disk storage for large properties that don't need to be stored in the
  graph database.
- Added support for managing streams and database triggers.
