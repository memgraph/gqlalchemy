# How to import table data to a graph database

This guide will show you how to use `loaders.py` to translate table data from a
file to graph data and import it to **Memgraph**. Currently, we support reading
of CSV, Parquet, ORC and IPC/Feather/Arrow file formats via the **PyArrow** package.

> Make sure you have a running Memgraph instance. If you're not sure how to run
> Memgraph, check out the Memgraph [Quick start](https://memgraph.com/docs/getting-started).

The `loaders.py` module implements loading data from the local file system, as
well as Azure Blob and Amazon S3 remote file systems. Depending on where your
data is located, here are two guides on how to import it to Memgraph:

- [Loading a CSV file from the local file
  system](#loading-a-csv-file-from-the-local-file-system)
- [Using a cloud storage solution](#using-a-cloud-storage-solution)

!!! info
    You can also use this feature with Neo4j:

    ```python
    db = Neo4j(host="localhost", port="7687", username="neo4j", password="test")
    ```

!!! info
    The features below aren’t included in the default GQLAlchemy installation. To use them, make sure to [install GQLAlchemy](../../installation.md) with the relevant extras.

## Loading a CSV file from the local file system

Let's say you have a simple dataset stored in CSV files:

`/home/user/table_data/individual.csv`:
```csv
ind_id, name, surname, add_id
1, Ivan,  Horvat, 2
2, Marko, Andric, 2
3, Luka,  Lukic,  1
```

`/home/user/table_data/address.csv`:
```csv
add_id, street, num, city
1, Ilica,    2,  Zagreb
2, Broadway, 12, New York
```

To create a translation from table to graph data, you need to define a **data
configuration object**. This can be done inside your code by defining a
dictionary, but it is recommended to use a YAML file structured like this:

```yaml
indices:    # indices to be created for each table
  individuals:    # name of table containing individuals with ind_id
  - ind_id
  address:
  - add_id


name_mappings:    # how we want to name node labels
  individuals:
    label: INDIVIDUAL    # nodes made from individuals table will have INDIVIDUAL label
  address:
    label: ADDRESS
    column_names_mapping: {"current_column_name": "mapped_name"}    # (optional) map column names


one_to_many_relations:
  address: []        # currently needed, leave [] if no relations to define
  individuals:
    - foreign_key: # foreign key used for mapping;
        column_name: add_id         # specifies its column
        reference_table: address    # name of table from which the foreign key is taken
        reference_key: add_id       # column name in reference table from which the foreign key is taken
      label: LIVES_IN        # label applied to relationship created
        from_entity: False     # (optional) define direction of relationship created


many_to_many_relations:       # intended to be used in case of associative tables
  example:
    foreign_key_from:        # describes the source of the relationship
      column_name:
      reference_table:
      reference_key:
    foreign_key_to:          # describes the destination of the relationship
      column_name:
      reference_table:
      reference_key:
    label:                   # relationship's label
    properties:              # list of properties to add to the relationship

```

### One to many

For this example, you don't need all of those fields. You only need to define
`indices` and `one_to_many_relations`. Hence, you have the following YAML file:

```yaml
indices:
  address:
    - add_id
  individual:
    - ind_id

name_mappings:
  individual:
    label: INDIVIDUAL
  address:
    label: ADDRESS

one_to_many_relations:
  address: []
  individual:
    - foreign_key:
        column_name: add_id
        reference_table: address
        reference_key: add_id
      label: LIVES_IN
```

In order to read the data configuration from the YAML file, run:

```python
with open("./example.yaml", "r") as stream:
    try:
        parsed_yaml = yaml.load(stream, Loader=SafeLoader)
    except yaml.YAMLError as exc:
        print(exc)
```

Having defined the data configuration for the translation, all you need to do is
make an instance of an `Importer` and call `translate()`.

```python
importer = CSVLocalFileSystemImporter(
    data_configuration=parsed_yaml,
    path="/home/user/table_data/",
)

importer.translate(drop_database_on_start=True)
```

### Many to many

Relationships can also be defined using a third, associative table.

`/home/user/table_data/tenant.csv`:
```csv
ind_id, add_id, duration
1, 2, 21
2, 2, 3
3, 1, 5
```

We need to extend our data configuration YAML file to include the `many_to_many_relations`, like so:

```
indices:
  address:
    - add_id
  individual:
    - ind_id

name_mappings:
  individual:
    label: INDIVIDUAL
  address:
    label: ADDRESS
  tenant:
    column_names_mapping:
      duration: years

one_to_many_relations:
  address: []
  individual: []

many_to_many_relations:
  tenant:
    foreign_key_from:
      column_name: ind_id
      reference_table: individual
      reference_key: ind_id
    foreign_key_to:
      column_name: add_id
      reference_table: address
      reference_key: add_id
    label: LIVES_IN
    properties:
      - duration
```

From here the procedure is the same as before.
In addition to having imported nodes and connected individuals and their addresses, we have also added an edge property.
This property is read from the associative table and is named in accordance with the `name_mappings`.

## Using a cloud storage solution

To connect to Azure Blob, simply change the Importer object you are using. Like
above, first, define a data configuration object and then simply call:

```python
importer = ParquetAzureBlobFileSystemImporter(
    container_name="test",
    data_configuration=parsed_yaml,
    account_name="your_account_name",
    account_key="your_account_key",
)
```

Hopefully, this guide has taught you how to import table data into Memgraph. If
you have any more questions, join our community and ping us on
[Discord](https://discord.gg/memgraph).
