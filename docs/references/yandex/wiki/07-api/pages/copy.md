# Скопировать страницу




Копирование страницы на новый адрес.


Отложенная операция. Если все проверки пройдены, вернет информацию о том, как проверять статус.


Коды ошибок валидации (error_code)


- `IS_CLOUD_PAGE`: нельзя клонировать облачные страницы
- `SLUG_OCCUPIED`: после клонирования страница пересекается с уже существующей
- `SLUG_RESERVED`: нельзя клонировать в зарезервированные страницы
- `FORBIDDEN`: Нет доступа к исходной странице или к кластеру, в который клонируется страница
- `QUOTA_EXCEEDED`: Достигнут лимит на создание страниц в текущей организации
- `CLUSTER_BLOCKED`: Кластер временно заблокирован для переноса.


## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}/clone
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |



### Body


application/json
    
        
```
{
  "target": "example",
  "title": "example",
  "subscribe_me": false
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| target | Type: string slug страницы после копирования Example: example |
| subscribe_me | Type: boolean Подписатьcя на изменения Default: false |
| title | Type: string Если передан, название страницы после копирования Min length: 1 Max length: 255 Example: example |



## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "operation": {
    "type": "clone",
    "id": "example"
  },
  "dry_run": false,
  "status_url": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| operation | Type: B2BOperationIdentity Example { "type": "clone", "id": "example" } |
| status_url | Type: string URL, по которому вернется прогресс операции Example: example |
| dry_run | Type: boolean Default: false |




### B2BOperationType



An enumeration.


**Type**: string


*Enum:* `clone`, `clone_inline_grid`




### B2BOperationIdentity



| Name | Description |
| --- | --- |
| id | Type: string Example: example |
| type | Type: B2BOperationType An enumeration. Enum: clone, clone_inline_grid |

**Example**
    
        
```
{
  "type": "clone",
  "id": "example"
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#path-parameters)
  - [Query parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#query-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#body)
  - [PageGridsSchema](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__page_grids#entity-PageGridsSchema)


