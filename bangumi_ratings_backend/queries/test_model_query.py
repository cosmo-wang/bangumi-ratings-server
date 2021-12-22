from graphene import ObjectType, Field, List
from graphene_django import DjangoObjectType
from bangumi_ratings_backend.models import TestModel

class TestModelNode(DjangoObjectType):
  class Meta:
    model = TestModel

class Query(ObjectType):
  get_name = List(TestModelNode)

  def resolve_get_name(self, info, **kwargs):
    return TestModel.objects.all()
