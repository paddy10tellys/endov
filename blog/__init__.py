from .views import app  # nb the . means relative import from the blog package
from .models import graph
import os


graph.run("CREATE CONSTRAINT ON (n:User) ASSERT n.username IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (n:Tag) ASSERT n.name IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (n:Post) ASSERT n.id IS UNIQUE")
graph.run("CREATE INDEX ON :Post(date)")