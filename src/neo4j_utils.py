# From https://github.com/cj2001/neo4j_streamlit/edit/main/src/neo4j_utils.py
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    # def query(self, query, **kwparameters):
    #     assert self.__driver is not None, "Driver not initialized!"
    #     session = None
    #     response = None
    #     try:
    #         session = self.__driver.session()
    #         response = list(session.run(query, kwparameters))
    #     except Exception as e:
    #         print("Query failed:", e)
    #     finally:
    #         if session is not None:
    #             session.close()
    #     return response

    def read(self, query, **kwargs):
        def execute(tx):
            result = tx.run(execute, kwargs)
            return result
        try:
            with self.__driver.session() as session:
                return session.read_transaction(execute)
        except Exception as e:
            print("write failed:", e)

    def write(self, query, **kwargs):
        def execute(tx):
            result = tx.run(query, kwargs)
            return result
        try:
            with self.__driver.session() as session:
                return session.write_transaction(execute)
        except Exception as e:
            print("write failed:", e)

    def set_user_language(self, user_id, language_code):
        query = """
            MATCH (u:User {name: $userId})
            MATCH (l:Language {name:$languageCode})
            MERGE (u)-[:SPEAKS]->(l)
        """
        try:
            result = self.write(query, userId=user_id, languageCode=language_code)
        except Exception as e:
            print(e)

    def set_new_language(self, user_id, language_code):
        query = """
            MATCH (u:User {name: $userId})
            MATCH (l:Language {name: $languageCode})
            MERGE (u)-[:LEARNING]->(l)
        """
        try:
            return self.write(query, userId=user_id, languageCode=language_code)
        except Exception as e:
            print(e)

    def read_languages(self):
        def get_language(tx):
            query = """
                MATCH (l:Language)
                RETURN l { .* } AS language
            """
            result = tx.run(query)
            return [record['language']['name'] for record in result]
        try:
            with self.__driver.session() as session:
                return session.read_transaction(get_language)
        except Exception as e:
            print("set_language failed:", e)

    def create_user(self, user_id):
        def create(tx):
            query = """
                MERGE (u:User {name:$userId})
                RETURN u
            """
            result = tx.run(query, userId=user_id).single()
            # print(f'create_user: result: {result}')
            return result['u']['name']
        try:
            with self.__driver.session() as session:
                return session.write_transaction(create)
        except Exception as e:
            print("create_user failed:", e)

    def get_all_phrases(self, user_language_code, target_language_code):
        def get(tx):
            query = f"""
                MATCH (l:Language{{name:$targetLanguage}})-[:USED_IN]-(p:Phrase)
                RETURN p LIMIT 24
                """
            result = tx.run(query, targetLanguage=target_language_code)
            return [record['p']['name'] for record in result]
        try:
            with self.__driver.session() as session:
                return session.read_transaction(get)
        except Exception as e:
            print("get_root_phrases failed:", e)

    def get_root_phrases(self, user_language_code, target_language_code):
        def get(tx):
            query = f"""
                MATCH (l:Language{{name:$targetLanguage}})-[:USED_IN]-(p:Phrase)
                WHERE NOT (:Phrase)-[:PRECEDES]-(p)
                RETURN p LIMIT 12
                """
            result = tx.run(query, targetLanguage=target_language_code)
            return [record['p']['name'] for record in result]
        try:
            with self.__driver.session() as session:
                return session.read_transaction(get)
        except Exception as e:
            print("get_root_phrases failed:", e)

    def get_phrases(self, phrase, user_language_code, target_language_code):
        # If no phrases, then search for all inital phrases
        if phrase == None or phrase == '':
            return self.get_root_phrases(user_language_code, target_language_code)
        
        def get(tx):
            print(f'get_phrases: get: phrase: {phrase}')
            query = """
                MATCH (p2:Phrase{name:$phrase})-[:PRECEDES]->(p)
                MATCH (l:Language{name:$targetLanguage})
                WHERE (l)-[:USED_IN]-(p)
                RETURN p LIMIT 12
                """
            result = tx.run(query, phrase=phrase, targetLanguage=target_language_code)
            return [record['p']['name'] for record in result]
        try:
            with self.__driver.session() as session:
                return session.read_transaction(get)
        except Exception as e:
            print("get_phrases failed:", e)

    def add_priorless_phrase(self, user_phrase, user_language, new_phrase, new_language):
        def add(tx, user_phrase, user_language, new_phrase, new_language):
            print(f'user_phrase: {user_phrase}, user_language: {user_language}, new_phrase: {new_phrase}, new_language:{new_language}')
            query = """
                MERGE (p1:Phrase {name:$userPhrase})
                MERGE (l1:Language {name:$userLanguage})
                MERGE (p1)-[:USED_IN]->(l1)
                MERGE (p2:Phrase {name:$newPhrase})
                MERGE (l2:Language {name:$newLanguage})
                MERGE (p2)-[:USED_IN]->(l2)
                MERGE (p1)-[:EQUALS]->(p2)
            """
            return tx.run(query, userPhrase=user_phrase, userLanguage=user_language, newPhrase=new_phrase, newLanguage=new_language)
        try:
            with self.__driver.session() as session:
                session.write_transaction(add, user_phrase=user_phrase, user_language=user_language, new_phrase=new_phrase, new_language=new_language)
        except Exception as e:
            print(f'neo4j.py: add_priorless_phrase: ERROR: {e}')
            return None

    def add_phrase_with_prior(self, **kwargs):
        def add(tx):
            query = """
                MATCH (p1:Phrase{name:$priorPhrase})
                MERGE (p2:Phrase{name:$newPhrase})
                MERGE (l2:Language{name:$newLanguage})
                MERGE (p2)-[:USED_IN]->(l2)
                MERGE (p3:Phrase{name:$userPhrase})
                MERGE (l3:Language{name:$userLanguage})
                MERGE (p3)-[:USED_IN]->(l3)
                MERGE (p2)-[:EQUALS]->(p3)
                MERGE (p1)-[:PRECEDES]->(p2)
            """
            return tx.run(query, kwargs)
        try:
            with self.__driver.session() as session:
                session.write_transaction(add)
        except Exception as e:
            print(f'neo4j.py: add_phrase_with_prior: ERROR: {e}')
            return None   

    def add_phrase(self, user_phrase, user_language, new_phrase, new_language, prior_phrase=None):
        if prior_phrase == None or prior_phrase == '':
            return self.add_priorless_phrase(user_phrase, user_language, new_phrase, new_language)
        else:
            return self.add_phrase_with_prior(userPhrase=user_phrase, userLanguage=user_language, newPhrase=new_phrase, newLanguage=new_language, priorPhrase=prior_phrase)