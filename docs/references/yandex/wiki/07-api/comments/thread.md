# Получить ветку комментариев




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/comments/{comment_id}/thread
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| comment_id | Type: integer |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| cursor | Type: string Example: `` |
| page_size | Type: integer Число результатов на странице выдачи. Default: 25 Min value: 1 Max value: 50 |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "results": [
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
  ],
  "next_cursor": "example",
  "prev_cursor": "example",
  "page_id": 0
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| page_id | Type: integer Для обратной совместимости, если задан курсор — всегда равен 1 |
| results | Type: CommentSchema[] Example [ { "id": 0, "body": "example", "inline_text": "example", "parent_id": 0, "author": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "thread_id": 0, "created_at": "2025-01-01T00:00:00Z", "is_deleted": true, "resolve_status": "resolved", "reactions": [ { "type": "like", "author": null, "created_at": "2025-01-01T00:00:00Z" } ] } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




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


        
            
            
        
    



### CommentSchema



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

**Example**
    
        
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

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__delete_comment#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__delete_comment#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__delete_comment#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__delete_comment#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__delete_comment#body)


