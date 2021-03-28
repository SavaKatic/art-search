from elasticsearch import Elasticsearch

class ElasticConnector:
    def __init__(self, ip=None, port=None):
        self.connection = None
        if not ip or not port:
            return

        # Connect to an elasticsearch node with the given ip and port
        self.connection = Elasticsearch([{"host": ip, "port": port}])
        print(f"HOST: {ip}")
        if self.connection.ping():
            print("Connected to elasticsearch...")
        else:
            print("Elasticsearch connection error...")



    def create_artwork_index(self):
        # Define the index mapping
        index_body = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text"
                    },
                    "description": {
                        "type": "text"
                    },
                    "img_vec": {
                        "type": "dense_vector",
                        "dims": 512
                    },
                    "artwork_id": {
                        "type": "long"
                    }
                }
            }
        }
        try:
            # Create the index if not exists
            if not self.connection.indices.exists("artworks"):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.connection.indices.create(
                    index="artworks", body=index_body  # ignore=[400, 404]
                )
                print("Created Index -> artworks")
            else:
                print("Index artworks exists...")
        except Exception as ex:
            print(str(ex))


    def insert_artwork(self, body):
        if not self.connection.indices.exists("artworks"):
            self.create_artwork_index()
        # Insert a record into the es index
        self.connection.index(index="artworks", body=body)


    def semantic_search(self, query_vec, thresh=1.2, top_n=10):
        # Retrieve top_n semantically similar records for the given query vector
        if not self.connection.indices.exists("artworks"):
            return "No records found"
        s_body = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'img_vec') + 1.0",
                        "params": {"query_vector": query_vec}
                    }
                }
            }
        }

        # Semantic vector search with cosine similarity
        result = self.connection.search(index="artworks", body=s_body)
        total_match = len(result["hits"]["hits"])
        print("Total Matches: ", str(total_match))

        data = []
        if total_match > 0:
            artwork_ids = []
            for hit in result["hits"]["hits"]:
                if hit['_score'] > thresh and hit['_source']['artwork_id'] not in artwork_ids and len(data) <= top_n:
                    print("--\nscore: {} \n title: {} \n description: {}\n--".format(hit["_score"], hit["_source"]['title'], hit["_source"]['description']))
                    artwork_ids.append(hit['_source']['artwork_id'])
                    data.append({'title': hit["_source"]['title'], 'description': hit["_source"]['description']})
        return data


    def keyword_search(self, query, thresh=1.2, top_n=10):
        # Retrieve top_n records using TF-IDF scoring for the given query vector
        if not self.connection.indices.exists("artworks"):
            return "No records found"
        k_body = {
            "query": {
                "match": {
                    "title": query
                }
            }
        }

        # Keyword search
        result = self.connection.search(index="artworks", body=k_body)
        total_match = len(result["hits"]["hits"])
        print("Total Matches: ", str(total_match))
        # print(result)

        data = []
        if total_match > 0:
            artwork_ids = []
            for hit in result["hits"]["hits"]:
                if hit['_score'] > thresh and hit['_source']['artwork_id'] not in artwork_ids and len(data) <= top_n:
                    print("--\nscore: {} \n title: {} \n description: {}\n--".format(hit["_score"], hit["_source"]['title'], hit["_source"]['description']))
                    artwork_ids.append(hit['_source']['q_id'])
                    data.append({'title': hit["_source"]['title'], 'description': hit["_source"]['description']})
        return data
