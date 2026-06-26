# Добавить комментарий




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/comments
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |



### Body


application/json
    
        
```
{
  "body": "example",
  "inline_text": "example",
  "parent_id": 0,
  "thread_id": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| body | Type: string Example: example |
| inline_text | Type: string Example: example |
| parent_id | Type: integer |
| thread_id | Type: integer |



## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "id": 0,
  "body": "example",
  "inline_text": "example",
  "parent_id": 0,
  "author": {
    "id": 0,
    "identity": {
      "uid": "example",
      "cloud_uid": "example"
    },
    "username": "example",
    "display_name": "example",
    "is_dismissed": true,
    "affiliation": "example"
  },
  "thread_id": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "is_deleted": true,
  "resolve_status": "resolved",
  "reactions": [
    {
      "type": "like",
      "author": null,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| author | Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } |
| body | Type: string Example: example |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| id | Type: integer |
| is_deleted | Type: boolean |
| reactions | Type: CommentReactionSchema[] Example [ { "type": "like", "author": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "created_at": "2025-01-01T00:00:00Z" } ] |
| resolve_status | Type: CommentResolveStatus An enumeration. Enum: resolved, unresolved |
| inline_text | Type: string Example: example |
| parent_id | Type: integer |
| thread_id | Type: integer |




### UserIdentity



| Name | Description |
| --- | --- |
| cloud_uid | Type: string Example: example |
| uid | Type: string Example: example |

**Example**
    
        
```
{
  "uid": "example",
  "cloud_uid": "example"
}
```


        
            
            
        
    



### UserSchema



| Name | Description |
| --- | --- |
| affiliation | Type: string Example: example |
| display_name | Type: string Example: example |
| id | Type: integer |
| is_dismissed | Type: boolean |
| username | Type: string Example: example |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |

**Example**
    
        
```
{
  "id": 0,
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  },
  "username": "example",
  "display_name": "example",
  "is_dismissed": true,
  "affiliation": "example"
}
```


        
            
            
        
    



### CommentResolveStatus



An enumeration.


**Type**: string


*Enum:* `resolved`, `unresolved`




### ReactionType



An enumeration.


**Type**: string


*Enum:* `like`, `hooray`, `confused`, `heart`, `rocket`, `eyes`, `fire`, `ok`, `facepalm`, `check`, `laugh`, `dislike`




### CommentReactionSchema



| Name | Description |
| --- | --- |
| author | Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| type | Type: ReactionType An enumeration. Enum: like, hooray, confused, heart, rocket, eyes, fire, ok, facepalm, check, laugh, dislike |

**Example**
    
        
```
{
  "type": "like",
  "author": {
    "id": 0,
    "identity": {
      "uid": "example",
      "cloud_uid": "example"
    },
    "username": "example",
    "display_name": "example",
    "is_dismissed": true,
    "affiliation": "example"
  },
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#path-parameters)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#query-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#body)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-UserSchema)
  - [CommentResolveStatus](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-CommentResolveStatus)
  - [ReactionType](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-ReactionType)
  - [CommentReactionSchema](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-CommentReactionSchema)
  - [CommentSchema](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__thread_comments#entity-CommentSchema)


