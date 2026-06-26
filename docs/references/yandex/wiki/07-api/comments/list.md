# Получить комментарии




## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/comments
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| cursor | Type: string Example: `` |
| order_by | Type: string Если указано, отсортировать выдачу по полю в направлении direction Const: created_at Example: `` |
| order_direction | All of: OrderDirection OrderDirection Type: string An enumeration. Enum: asc, desc Если указано поле order_by, направление сортировки Default: asc Example: `` |
| page_size | Type: integer Число результатов на странице выдачи. Default: 50 Min value: 1 Max value: 100 |
| status_filter | All of: CommentResolveStatus CommentResolveStatus Type: string An enumeration. Enum: resolved, unresolved Фильтрация по статусу комментария, принимает CommentResolveStatus (resolved, unresolved) Example: `` |


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
      ],
      "thread_info": {
        "total_posts": 0,
        "last_comment": {
          "id": 0,
          "body": "example",
          "inline_text": "example",
          "parent_id": 0,
          "author": null,
          "thread_id": 0,
          "created_at": "2025-01-01T00:00:00Z",
          "is_deleted": true,
          "resolve_status": null,
          "reactions": [
            null
          ]
        }
      }
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| results | Type: CommentSchemaExt[] Example [ { "id": 0, "body": "example", "inline_text": "example", "parent_id": 0, "author": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "thread_id": 0, "created_at": "2025-01-01T00:00:00Z", "is_deleted": true, "resolve_status": "resolved", "reactions": [ { "type": "like", "author": null, "created_at": "2025-01-01T00:00:00Z" } ], "thread_info": { "total_posts": 0, "last_comment": { "id": 0, "body": "example", "inline_text": "example", "parent_id": 0, "author": null, "thread_id": 0, "created_at": "2025-01-01T00:00:00Z", "is_deleted": true, "resolve_status": null, "reactions": [ null ] } } } ] |
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


        
            
            
        
    



### ThreadSchema



| Name | Description |
| --- | --- |
| last_comment | Type: CommentSchema Example { "id": 0, "body": "example", "inline_text": "example", "parent_id": 0, "author": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "thread_id": 0, "created_at": "2025-01-01T00:00:00Z", "is_deleted": true, "resolve_status": "resolved", "reactions": [ { "type": "like", "author": null, "created_at": "2025-01-01T00:00:00Z" } ] } |
| total_posts | Type: integer |

**Example**
    
        
```
{
  "total_posts": 0,
  "last_comment": {
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
}
```


        
            
            
        
    



### CommentSchemaExt



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
| thread_info | Type: ThreadSchema Example { "total_posts": 0, "last_comment": { "id": 0, "body": "example", "inline_text": "example", "parent_id": 0, "author": { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" }, "thread_id": 0, "created_at": "2025-01-01T00:00:00Z", "is_deleted": true, "resolve_status": "resolved", "reactions": [ { "type": "like", "author": null, "created_at": "2025-01-01T00:00:00Z" } ] } } |

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
  ],
  "thread_info": {
    "total_posts": 0,
    "last_comment": {
      "id": 0,
      "body": "example",
      "inline_text": "example",
      "parent_id": 0,
      "author": null,
      "thread_id": 0,
      "created_at": "2025-01-01T00:00:00Z",
      "is_deleted": true,
      "resolve_status": null,
      "reactions": [
        null
      ]
    }
  }
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#body1)
  - [UserIdentity](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#entity-UserIdentity)
  - [UserSchema](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#entity-UserSchema)
  - [CommentResolveStatus](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#entity-CommentResolveStatus)
  - [ReactionType](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#entity-ReactionType)
  - [CommentReactionSchema](https://yandex.ru/support/wiki/ru/api-ref/comments/ru/api-ref/comments/pagescomments__create_comment#entity-CommentReactionSchema)


