import graphene
from crm.schema import Query as CRMQuery

class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query)