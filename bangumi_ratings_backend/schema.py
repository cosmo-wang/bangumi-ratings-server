from graphene import ObjectType
from graphene_federation import build_schema
from bangumi_ratings_backend.queries.queries import Query as queries
from bangumi_ratings_backend.queries.mutations import Mutation as mutations

class Query(queries, ObjectType):
  pass

class Mutation(mutations, ObjectType):
  pass

schema = build_schema(query=Query, mutation=Mutation)
introspection_dict = schema.introspect()
