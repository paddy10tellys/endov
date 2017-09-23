# models.py holds classes & functions needed for the views in views.py to do their job
# where models for the application are defined
from py2neo import Graph, Node, Relationship
from py2neo.ext.calendar import GregorianCalendar
from passlib.hash import bcrypt
from datetime import datetime
import uuid
import os
from pandas import DataFrame
from subprocess import Popen


graph = Graph(user='neo4j', password='bin789MAN')
calendar = GregorianCalendar(graph)

# _init__   (nb abbrevation for initialise) is a kind of constructor, when an actual instance of a class is created (object as opp to blueprint)
# called by python after memory for the object has been allocated. Usually used to set "default" values
# defines additional behavior setting up some beginning values for that object or running a routine required on instantiation
# self shows that you are using a method or instance attribute instead of a local variable
# self refers to the current instance of the object
# self is how we refer to things in the class from within itself

class User:
    def __init__(self, username):
        self.username = username
        
    def find(self):
        user = graph.find_one("User","username", self.username)   # find (1) a usernode label (2) the property key representing a particular user, (3) an initialised instance of... the property value
        return user   # return the py2neo object specified above, or a none type if nothing found
        
    def register(self, password):   # to set username & the password properties on the user node
        if not self.find():              # if the node doesn't exist i.e., the method above returned none
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))     # create node with a User label & with name & password properties 
            graph.create(user)    # pass the user instance in here to be created in the database
            return True   # indicates registration was completed successfully
            
        return False  # user already exists in the database
        

    def verify_password(self, password):
            user = self.find()
            if not user:
                return False
            return bcrypt.verify(password, user["password"])  



    def verify_password(self, password):
        user = self.find()

        if not user:
            return False

        return bcrypt.verify(password, user["password"])
    
    
    def add_post(self, title, tags, text):
        user = self.find()
        today=datetime.now()
        
        id=str(uuid.uuid4())
        
        post = Node (
            "Post",
            id=id,
            title=title,
            text=text,
            timestamp=int(today.strftime("%s")),
            date=today.strftime("%F")
        )

        text = id + " " + text
        
        #create the text file that will be the input into ctakes runClinicalPipeline.sh & save it into the note_input directory
        with open("/home/pmy/ctakes/apache-ctakes-4.0.0/note_input/note.txt", mode='w') as f:
            f.write(text)  
            
    #     #run ctakes in a subprocess
    #     p = Popen(["sh" , "/home/pmy/ctakes/apache-ctakes-4.0.0/bin/runClinicalPipeline.sh"]) # something long running
    #     #... do other stuff while subprocess is running
    #     #os.system("sh /home/pmy/ctakes/apache-ctakes-4.0.0/bin/runClinicalPipeline.sh")    # call ctakes shell script from python code. 
        
        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)
        
        
        #today_node = calendar.date(today.year, today.month, today.day).day
        #graph.create(Relationship(post, "ON", today_node))
        
        
        today = Relationship(post, "ON", calendar.date(today.year, today.month, today.day).day)
        graph.create(today)
        
        
        

        tags = [x.strip() for x in tags.lower().split(",")]
        tags = set(tags)
        
        for tag in tags:
            t = Node("Tag", name=tag)
            graph.merge(t)
            rel=Relationship(t, "TAGGED", post)
            graph.create(rel)
            
    #     p.terminate()  # end the subprocess
            
        
    def like_post(self, post_id):
        user=self.find()
        post=graph.find_one("Post", "id", post_id)
        graph.create(Relationship(user, "LIKES", post))

    def recent_posts(self, n):
        query = '''
        MATCH(user: User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT {n}
        '''
        return graph.run(query, username=self.username, n=n)

    def similar_users(self, n):
        query = '''
        MATCH (user1: User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2: User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE user1.username = {username} AND user1 <> user2
        WITH user2, COLLECT(DISTINCT tag.name) AS tags, COUNT(DISTINCT tag.name) AS tag_count
        ORDER BY tag_count DESC LIMIT {n}
        RETURN user2.username AS similar_user, tags
        
        '''
        return graph.run(query, username=self.username, n=n)
        
    def commonality_of_user(self, user):
        query1 = '''
        MATCH (user1:User)-[:PUBLISHED]->(post:Post)<-[:LIKES]-(user2:User)
        WHERE user1.username = {username1} AND user2.username = {username2}
        RETURN COUNT(post) AS likes        
        '''
        # likes = graph.cypher.execute_one(query1, username1=self.username, username2=user.username)    
        likes = DataFrame( graph.run(query1, username1=self.username, username2=user.username).data() )
        likes = likes["likes"][0]
        likes = 0 if not likes else likes 
        
        query2 = '''
        MATCH (user1: User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (user2: User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag) 
        WHERE user1.username = {username1} AND user2.username = {username2}
        RETURN COLLECT(DISTINCT tag.name) AS tags
        '''
        # tags = graph.cypher.execute(query2, username1=self.username, username2=user.username)[0]["tags"]
        tags = DataFrame( graph.run(query2, username1=self.username, username2=user.username).data() )
        tags = tags["tags"][0]
        return {"likes":likes, "tags":tags}

def todays_recent_posts(n):
    query = '''
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags 
    ORDER BY post.timestamp DESC LIMIT {n}
    '''
    today = datetime.now().strftime("%F")
    return graph.run(query, today=today, n=n)
    #return graph.cypher.execute(query, today=today, n=n)
        