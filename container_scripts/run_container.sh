docker run \
    --name my_neo4j_2 \
    --volume neo4j_data:/data \
    --volume neo4j_logs:/logs \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --env NEO4JLABS_PLUGINS='["apoc", "graph-data-science"]' \
    --env NEO4J_AUTH=neo4j/testpassword \
    --publish=7474:7474 --publish=7687:7687 \
    neo4j:5.26.10-community