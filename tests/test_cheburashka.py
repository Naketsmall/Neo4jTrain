from neo4j import GraphDatabase


class Neo4jTest:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def test_connection(self):
        with self.driver.session() as session:
            greeting = session.execute_write(self._create_and_return_greeting)
            print("Результат тестового запроса:", greeting)

    @staticmethod
    def _create_and_return_greeting(tx):
        result = tx.run("""
            CREATE (a:Greeting) 
            SET a.message = $message
            RETURN a.message + ', от узла ' + id(a)
            """, message="Привет, Neo4j!")
        return result.single()[0]

    def get_friends_of(self, name):
        with self.driver.session() as session:
            return session.execute_read(self._get_friends, name)

    @staticmethod
    def _get_friends(tx, name):
        query = """
            MATCH (p:Person)-[:FRIEND_OF]->(friend) 
            WHERE p.name = $name
            RETURN friend.name AS name
        """
        result = tx.run(query, name=name)
        return [record["name"] for record in result]

    def clean_database(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                DETACH DELETE n
                RETURN count(n) AS deletedNodes
            """)
            deleted_count = result.single()["deletedNodes"]
            print(f"\nУдалено {deleted_count} узлов и всех их связей")
            return deleted_count


if __name__ == "__main__":
    neo = Neo4jTest("bolt://localhost:7687", "neo4j", "testpassword")

    try:
        neo.test_connection()

        with neo.driver.session() as session:
            session.run("""
                CREATE (alice:Person {name: 'Алиса', age: 30})
                CREATE (bob:Person {name: 'Боб', age: 25})
                CREATE (charlie:Person {name: 'Чарли', age: 35})
                CREATE (Cheburashka:Person {name: 'Чебурашка', age: 99})
                CREATE (alice)-[:FRIEND_OF]->(bob)
                CREATE (alice)-[:FRIEND_OF]->(charlie)
            """)
            print("\nТестовые данные созданы")

        friends = neo.get_friends_of("Алиса")
        print("\nДрузья Алисы:", friends)
        print("\nДрузья Чебурашки:", neo.get_friends_of("Чебурашка"))

        with neo.driver.session() as session:
            result = session.run("""
                MATCH (p:Person)
                RETURN p.name AS name, p.age AS age
                ORDER BY age DESC
            """)
            print("\nВсе люди по возрасту:")
            for record in result:
                print(f"- {record['name']}: {record['age']} лет")

    finally:
        neo.clean_database()
        neo.close()
        print("\nСоединение закрыто")