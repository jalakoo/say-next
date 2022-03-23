from neo4j_utils import Neo4jConnection

class Neo4jRepository():
    
    def __init__(self, uri, user, pwd):
        try:
            self.conn = Neo4jConnection(uri, user, pwd)
        except Exception as e:
            print("Failed to create Neo4jFunctions:", e)

    def create_user(self, user_id):
        query = """
            MERGE (u:User {name:$userId})
            RETURN u
        """
        self.conn.write(query, userId=user_id)

    def get_all_phrases(self, target_language_code):
        query = """
            MATCH (l:Language{name:$targetLanguage})-[:USED_IN]-(p:Phrase)
            RETURN p LIMIT 40
            """
        result = self.conn.read(query, targetLanguage=target_language_code)
        print(result)
        print(result.keys())
        return [record['p']['name'] for record in result]

    def get_root_phrases(self, target_language):
        query = """
            MATCH (l:Language{name:$targetLanguage})-[:USED_IN]-(p:Phrase)
            WHERE NOT (:Phrase)-[:PRECEDES]-(p)
            RETURN p LIMIT 40
            """
        self.conn.read(query, targetLanguage=target_language)

    def get_phrases(self, phrase, user_language_code, target_language_code):
        # If no phrases, then search for all inital phrases
        if phrase == None or phrase == '':
            return self.get_root_phrases(target_language_code)

        query = """
            MATCH (p2:Phrase{name:$phrase})-[:PRECEDES]->(p)
            MATCH (l:Language{name:$targetLanguage})
            WHERE (l)-[:USED_IN]-(p)
            RETURN p LIMIT 40
            """
        result = self.conn.read(query, phrase=phrase, targetLanguage=target_language_code)
        return [record['p']['name'] for record in result]

    def get_user_preferences(self, user_id):
        def first(the_iterable, condition = lambda x: True):
            for i in the_iterable:
                if condition(i):
                    return i
        query = """
                MATCH (u:User {name: $userId})-[r:LEARNING|SPEAKS]->(l:Language)
                RETURN u,r,l
            """
        result = self.conn.read(query, userId=user_id)
        print(result)
        print([record['l'] for record in result])
        usr_lang = first(result, lambda x: x['type'] == 'SPEAKS' )['l']['name']
        lang = first(result, lambda x: x['type'] == 'LEARNING' )['l']['name']
        return (usr_lang, lang)

    def set_user_language(self, user_id, language_code, language_type):
        # Clear any different existing relationship
        clear_query = f"""
            MATCH (u:User {{name: $userId}})-[r:{language_type}]->(l)
            DELETE r
        """
        # Set the current relationship
        set_query = f"""
            MATCH (u:User {{name: $userId}})
            MERGE (l:Language {{name:$languageCode}})
            MERGE (u)-[:{language_type}]->(l)
        """
        self.conn.write(clear_query, userId=user_id, languageType=language_type)
        self.conn.write(set_query, userId=user_id, languageCode=language_code, languageType=language_type)


    def add_priorless_phrase(self, user_phrase, user_language, new_phrase, new_language):
        query = """
            MERGE (p1:Phrase {name:$userPhrase})
            MERGE (l1:Language {name:$userLanguage})
            MERGE (p1)-[:USED_IN]->(l1)
            MERGE (p2:Phrase {name:$newPhrase})
            MERGE (l2:Language {name:$newLanguage})
            MERGE (p2)-[:USED_IN]->(l2)
            MERGE (p1)-[:EQUALS]->(p2)
        """
        self.conn.write(query, userPhrase=user_phrase, userLanguage=user_language, newPhrase=new_phrase, newLanguage=new_language)

    def add_phrase_with_prior(self, user_phrase, user_language, new_phrase, new_language, prior_phrase):
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
        self.conn.write(query, userPhrase=user_phrase, userLanguage=user_language, newPhrase=new_phrase, newLanguage=new_language, priorPhrase=prior_phrase) 

    def add_phrase(self, user_phrase, user_language, new_phrase, new_language, prior_phrase=None):
        if prior_phrase == None or prior_phrase == '':
            return self.add_priorless_phrase(user_phrase, user_language, new_phrase, new_language)
        else:
            return self.add_phrase_with_prior(user_phrase, user_language, new_phrase, new_language, prior_phrase)