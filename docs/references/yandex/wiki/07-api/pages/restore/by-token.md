# Восстановить страницу по токену




Позволяет восстановить страницу, удаленную с помощью метода [Удалить страницу](https://yandex.ru/support/wiki/ru/api-ref/recovery_tokens/ru/api-ref/pages/pages__delete_page).


## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/recovery_tokens/{idx}/recover
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: string<uuid4> Значение параметра recovery_token, полученного в ответ на запрос удаления страницы. Example: `` |


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "id": 0,
  "slug": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| id | Type: integer |
| slug | Type: string Example: example |

---

