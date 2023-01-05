from gqlalchemy import Match
from translators.dgl_translator import DGLTranslator


query_results = Match().node(variable='n').to(variable='r').node(variable='m').return_().execute()
# for query in query_results:
#     print(f"Query results: {query}")

translator = DGLTranslator()
translator.get_instance(query_results)