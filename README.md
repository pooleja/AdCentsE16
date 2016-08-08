# ElasticsearchE16

## Overview
ElasticsearchE16 is a bitcoin payable web app designed for the 21 Marketplace to provide Elasticsearch as a service. Instead of signing up
for an expensive monthly offering, you can use as little or as much of the service as you need and pay as you go.

To get started, you need to 'create' an index.  All indexes are created with a random name like 'tm8gnm6bshpujmeeejff'.  This value needs to be
protected like a secret key, since anyone can run requests against any index if they know the name.  Also, every index is created with an expire
date that is 30 days in the future.  You can push this further into the future by calling the 'renew' function against that index at any time to add 30 more days.  When the expire date is reached, you will no longer be able to run any action against that index.

Once you have created an index, you can write documents into it using the 'index' function.  This will take the json document that is sent to the
API and load it into Elasticsearch.  From there, you can run the 'search' function to look through all the documents and run keyword searches against them
and return the records that match.

## Installation

### Run the setup script
To get things up and running:
```
$ git clone https://github.com/pooleja/ElasticsearchE16.git
$ cd ElasticsearchE16
$ ./setup.sh
```

Next, start up the server:
```
$ python3 transcodeE16-server.py -d
Connecting to DB.
Checking to see if any files need to be cleaned up in 'server-data' folder.
Sleeping for an hour befor cleaning up folder again.
Server running...
```

## Usage
The following shows how to set up and use an index against the service using the 21 CLI.

Create an index.
```
$ 21 buy url 'http://0.0.0.0:11016/indexes' --request POST
{
    "expired": false,
    "indexExpireDisplay": "Tue Sep  6 18:04:49 2016",
    "indexExpireTime": 1473199489.5632718,
    "indexId": "tm8gnm6bshpujmeeejff",
    "success": true
}
```
See the 'indexId' that is returned.  This will be used on subsequent calls.

Check index status.
```
$ 21 buy url 'http://0.0.0.0:11016/tm8gnm6bshpujmeeejff'
{
    "expired": false,
    "indexExpireDisplay": "Tue Sep  6 18:04:49 2016",
    "indexExpireTime": 1473199489.5632718,
    "indexId": "tm8gnm6bshpujmeeejff",
    "success": true
}
```
See that it is not yet expired and it shows you the expire date in the future.

Renew for 30 extra days.
```
$ 21 buy url 'http://0.0.0.0:11016/tm8gnm6bshpujmeeejff' --request PUT
{
    "expired": false,
    "indexExpireDisplay": "Thu Oct  6 18:04:49 2016",
    "indexExpireTime": 1475791489.5632718,
    "indexId": "tm8gnm6bshpujmeeejff",
    "success": true
}
```
See that the expire date went from Sept to Oct.

Delete the index.
```
$ 21 buy url 'http://0.0.0.0:11016/tm8gnm6bshpujmeeejff' --request DELETE
{
    "indexId": "tm8gnm6bshpujmeeejff",
    "message": "Index tm8gnm6bshpujmeeejff deleted.",
    "success": true
}
```

Verify it is deleted.
```
$ 21 buy url 'http://0.0.0.0:11016/tm8gnm6bshpujmeeejff'
{
    "error": "Index was previously deleted.",
    "success": false
}
```

Index a document on a different index.
```
$ 21 buy url 'http://0.0.0.0:11016/or48wn8hobbjkyu0j47r/tweet' -d '{ "user" : "kimchy", "post_date" : "2009-11-15T14:12:12", "message" : "trying out Elasticsearch"}' --request POST
{
    "result": {
        "_index": "or48wn8hobbjkyu0j47r",
        "_version": 1,
        "_id": "AVZnjEepJSnindBw5DD9",
        "_shards": {
            "total": 2,
            "failed": 0,
            "successful": 1
        },
        "created": true,
        "_type": "tweet"
    },
    "success": true
}
```
See that the document ID is returned.

Search for that document.
```
$ 21 buy url 'http://0.0.0.0:11016/or48wn8hobbjkyu0j47r/tweet/_search' -d '{"query" : { "term" : { "user" : "kimchy" } }}' --request POST
{
    "result": {
        "_shards": {
            "failed": 0,
            "total": 5,
            "successful": 5
        },
        "hits": {
            "max_score": 1.0,
            "total": 1,
            "hits": [
                {
                    "_score": 1.0,
                    "_type": "tweet",
                    "_id": "AVZnjEepJSnindBw5DD9",
                    "_source": {
                        "message": "trying out Elasticsearch",
                        "user": "kimchy",
                        "post_date": "2009-11-15T14:12:12"
                    },
                    "_index": "or48wn8hobbjkyu0j47r"
                }
            ]
        },
        "timed_out": false,
        "took": 2
    },
    "success": true
}
```
See that the document ID matches the one previously indexed.
