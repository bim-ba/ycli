# Добавить строки




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/grids/{idx}/rows
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: string<uuid4> Example: `` |



### Body


application/json
    
        
```
{
  "revision": "example",
  "position": 0,
  "after_row_id": "example",
  "rows": [
    {}
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| rows | Type: object[] [additional] Any of 6 types Type: integer Type: number Type: boolean Type: string Example: example Type: string[] Example [ "example" ] Type: UserIdentityExtended[] Example [ { "uid": "example", "cloud_uid": "example", "username": "example" } ] Example: 0 Example [ {} ] | [additional] | Any of 6 types Type: integer Type: number Type: boolean Type: string Example: example Type: string[] Example [ "example" ] Type: UserIdentityExtended[] Example [ { "uid": "example", "cloud_uid": "example", "username": "example" } ] Example: 0 |
| [additional] | Any of 6 types Type: integer Type: number Type: boolean Type: string Example: example Type: string[] Example [ "example" ] Type: UserIdentityExtended[] Example [ { "uid": "example", "cloud_uid": "example", "username": "example" } ] Example: 0 |
| after_row_id | Type: string Example: example |
| position | Type: integer |
| revision | Type: string Example: example |




### UserIdentityExtended



| Name | Description |
| --- | --- |
| cloud_uid | Type: string Example: example |
| uid | Type: string Example: example |
| username | Type: string Example: example |

**Example**
    
        
```
{
  "uid": "example",
  "cloud_uid": "example",
  "username": "example"
}
```


        
            
            
        
    


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "revision": "example",
  "results": [
    {
      "id": "example",
      "row": [
        0
      ],
      "pinned": true,
      "color": "blue"
    }
  ]
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| revision | Type: string Example: example |
| results | Type: GridRowSchema[] Example [ { "id": "example", "row": [ 0 ], "pinned": true, "color": "blue" } ] |




### TicketSchema



| Name | Description |
| --- | --- |
| key | Type: string Example: example |
| resolved | Type: boolean |

**Example**
    
        
```
{
  "key": "example",
  "resolved": true
}
```


        
            
            
        
    



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


        
            
            
        
    



### UnresolvedUserSchema



| Name | Description |
| --- | --- |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |
| username | Type: string Example: example |

**Example**
    
        
```
{
  "username": "example",
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  }
}
```


        
            
            
        
    



### TrackerEnumField



| Name | Description |
| --- | --- |
| display | Type: string Example: example |
| key | Type: string Example: example |

**Example**
    
        
```
{
  "display": "example",
  "key": "example"
}
```


        
            
            
        
    



### BGColor



An enumeration.


**Type**: string


*Enum:* `blue`, `yellow`, `pink`, `red`, `green`, `mint`, `grey`, `orange`, `magenta`, `purple`, `copper`, `ocean`




### GridRowSchema



| Name | Description |
| --- | --- |
| id | Type: string Example: example |
| row | Type: arrayAny of 10 types Type: integer Type: number Type: boolean Type: string Example: example TicketSchema Type: TicketSchema Example { "key": "example", "resolved": true } Type: string[] Example [ "example" ] Type: arrayAny of 2 types UserSchema Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } UnresolvedUserSchema Type: UnresolvedUserSchema Example { "username": "example", "identity": { "uid": "example", "cloud_uid": "example" } } Example [ { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } ] UserSchema Type: UserSchema Example { "id": 0, "identity": { "uid": "example", "cloud_uid": "example" }, "username": "example", "display_name": "example", "is_dismissed": true, "affiliation": "example" } UnresolvedUserSchema Type: UnresolvedUserSchema Example { "username": "example", "identity": { "uid": "example", "cloud_uid": "example" } } TrackerEnumField Type: TrackerEnumField Example { "display": "example", "key": "example" } Example [ 0 ] |
| color | Type: BGColor An enumeration. Enum: blue, yellow, pink, red, green, mint, grey, orange, magenta, purple, copper, ocean |
| pinned | Type: boolean |

**Example**
    
        
```
{
  "id": "example",
  "row": [
    0
  ],
  "pinned": true,
  "color": "blue"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#path-parameters)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#body)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/grids/ru/api-ref/grids/grids__remove_rows#body1)


