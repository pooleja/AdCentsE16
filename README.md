# ElasticsearchE16

## Overview

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

Delete index.
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
