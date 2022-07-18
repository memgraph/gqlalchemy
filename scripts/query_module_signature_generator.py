from gqlalchemy import Memgraph
from gqlalchemy.graph_algorithms.query_modules import QM_KEY_NAME, QM_KEY_TYPE

QUERIES_DEST = "queries.txt"


if __name__ == "__main__":
    mg = Memgraph()

    modules = mg.get_procedures()

    with open(QUERIES_DEST, "w") as f:
        for query_module in modules:
            arguments_upper = [f"{x[QM_KEY_NAME]}: {x[QM_KEY_TYPE]}" for x in query_module.arguments]
            arguments_upper_str = "" if len(arguments_upper) == 0 else f", {', '.join(arguments_upper)}"

            arguments_lower = [f"{x[QM_KEY_NAME]}" for x in query_module.arguments]
            arguments_lower_str = "" if len(arguments_lower) == 0 else f", ({', '.join(arguments_lower)})"

            f.write(f"def {query_module.name.replace('.', '_')}(self{arguments_upper_str}) -> DeclarativeBase:\n")

            f.write(f'\treturn self.call("{query_module.name}"{arguments_lower_str})\n\n')


# arguments - type, name, default
# name
