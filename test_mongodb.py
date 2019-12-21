import ssl
import pymongo
import passwords


connection_str = f'mongodb+srv://KirillKras:{passwords.MONGO_PASS}' + \
                 '@testcluster-hcpdp.mongodb.net/test?retryWrites=true&w=majority'

client = pymongo.MongoClient(connection_str, ssl_cert_reqs=ssl.CERT_NONE)
db = client.sample_geospatial

print(client.stats())
