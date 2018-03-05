from spotify import Client, OAuth

auth = OAuth('0dc7e64f5ab6485e9aef1bba1c0f2d96', 'a37dea127ff34ca6a3a94c5072188a8f')
auth.request_client_credentials()

client = Client(auth)

albums = client.api.search('artist:frank zappa', type='artist')