# Получить список подстраниц по слагу




Возвращает список подстраниц по слагу страницы.


## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/pages/descendants
```


        
            
            
        
    




### Query parameters



| Name | Description |
| --- | --- |
| slug | Type: string Example: `` |
| actuality | Type: string An enumeration. Enum: actual, obsolete |
| cursor | Type: string Example: `` |
| include_self | Type: boolean Default: false |
| page_size | Type: integer Число результатов на странице выдачи. Default: 50 Min value: 1 Max value: 100 |


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
      "slug": "example"
    }
  ],
  "next_cursor": "example",
  "prev_cursor": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| results | Type: PageSchema[] Example [ { "id": 0, "slug": "example" } ] |
| next_cursor | Type: string Example: example |
| prev_cursor | Type: string Example: example |




### PageSchema



| Name | Description |
| --- | --- |
| id | Type: integer |
| slug | Type: string Example: example |

**Example**
    
        
```
{
  "id": 0,
  "slug": "example"
}
```

---

