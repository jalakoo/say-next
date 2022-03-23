# From https://github.com/cj2001/neo4j_streamlit/edit/main/src/neo4j_utils.py
from neo4j import GraphDatabase

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

    # def query(self, query, parameters):
    #     assert self.__driver is not None, "Driver not initialized!"
    #     session = None
    #     response = None
    #     try:
    #         session = self.__driver.session()
    #         response = list(session.run(query, parameters))
    #     except Exception as e:
    #         print("Query failed:", e)
    #     finally:
    #         if session is not None:
    #             session.close()
    #     return response

    # This does not work as expected
    def read(self, query, **kwargs):
        assert self.__driver is not None, "Driver not initialized!"
        def execute(tx):
            result = tx.run(query, kwargs)
            return result
        try:
            with self.__driver.session() as session:
                return session.write_transaction(execute)
        except Exception as e:
            print("read failed:", e)

    def write(self, query, **kwargs):
        assert self.__driver is not None, "Driver not initialized!"
        def execute(tx):
            result = tx.run(query, kwargs)
            return result
        try:
            with self.__driver.session() as session:
                return session.write_transaction(execute)
        except Exception as e:
            print("write failed:", e)

    def get_user_preferences(self, user_id):
        def first(the_iterable, condition = lambda x: True):
            for i in the_iterable:
                if condition(i):
                    return i
        def get(tx):
            query = """
                    MATCH (u:User {name: $userId})-[r:LEARNING|SPEAKS]->(l:Language)
                    RETURN u,r,l
                """
            result = tx.run(query, userId=user_id)
            return [record['l'] for record in result]
        try:
            with self.__driver.session() as session:
                result = session.read_transaction(get)
                print(result)
                print([record['name'] for record in result])
                usr_lang = first(result, lambda x: x['type'] == 'SPEAKS' )['name']
                lang = first(result, lambda x: x['type'] == 'LEARNING' )['name']
                return (usr_lang, lang)
        except Exception as e:
            print("get_user_preferences failed:", e)


    # NONE of these reads work in an abstracted form
    # The result parsing needs to be done in the 
    # nested function and not from the session.read result
    def get_all_phrases(self, target_language_code):
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


    def get_translation(self, phrase, user_language):
        # TODO: This is not working? Works find when
        # Cypher is ran directly in db
        def execute(tx):
            query = """
                MATCH (l:Language {name: $userLanguage})
                MATCH (p:Phrase {name: $phrase})
                MATCH (p2:Phrase)
                MATCH (p)-[:EQUALS]-(p2)-[:USED_IN]->(l)
                RETURN p2
            """
            result = tx.run(query, userLanguage=user_language, phrase=phrase)
            return [record['p2']['name'] for record in result]
        try:
            with self.__driver.session() as session:
                return session.read_transaction(execute)
        except Exception as e:
            print(f'get_translation: ERROR: {e}')

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
            # print(f'get_phrases: get: phrase: {phrase}')
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
