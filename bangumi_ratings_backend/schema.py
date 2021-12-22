from graphene import ObjectType
from graphene_federation import build_schema
from bangumi_ratings_backend.queries.test_model_query import Query as test_model_query

class Query(test_model_query, ObjectType):
  pass


schema = build_schema(query=Query)
introspection_dict = schema.introspect()