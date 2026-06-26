# Обновить параметры страницы




## Request






POST


    
        
```
https://api.wiki.yandex.net/v1/pages/{idx}
```


        
            
            
        
    




### Path parameters



| Name | Description |
| --- | --- |
| idx | Type: integer |


### Query parameters



| Name | Description |
| --- | --- |
| allow_merge | Type: boolean Если True, то одновременные правки мёрджатся алгоритмом 3-way-merge, иначе — конфликт Default: false |
| fields | Type: string Желаемые дополнительные блоки, которые должны вернуться в ответе. См. описание формата ответа. Example: `` |
| is_silent | Type: boolean Не отправлять уведомление об обновлении страницы подписчикам Default: false |



### Body


application/json
    
        
```
{
  "title": "example",
  "content": "example",
  "redirect": {
    "page": {
      "id": 0,
      "slug": "example"
    }
  }
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| content | Type: string Example: example |
| redirect | Type: RedirectUpdateSchema Example { "page": { "id": 0, "slug": "example" } } |
| title | Type: string Min length: 1 Max length: 255 Example: example |




### PageIdentity



| Name | Description |
| --- | --- |
| id | Type: integer Обязателен id либо slug, при передаче обоих id имеет приоритет и slug игнорируется. |
| slug | Type: string Example: example |

**Example**
    
        
```
{
  "id": 0,
  "slug": "example"
}
```


        
            
            
        
    



### RedirectUpdateSchema



| Name | Description |
| --- | --- |
| page | All of 1 type PageIdentity Type: PageIdentity Example { "id": 0, "slug": "example" } Страница, куда должен быть совершен редирект. null для снятия редиректа. Example { "id": 0, "slug": "example" } |

**Example**
    
        
```
{
  "page": {
    "id": 0,
    "slug": "example"
  }
}
```


        
            
            
        
    


## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "id": 0,
  "slug": "example",
  "title": "example",
  "page_type": "page",
  "redirect": {
    "page_id": 0,
    "redirect_target": {
      "id": 0,
      "slug": "example",
      "title": "example",
      "page_type": "page"
    }
  },
  "breadcrumbs": [
    {
      "id": 0,
      "title": "example",
      "slug": "example",
      "page_exists": true
    }
  ],
  "attributes": {
    "created_at": "2025-01-01T00:00:00Z",
    "modified_at": "2025-01-01T00:00:00Z",
    "lang": "example",
    "is_readonly": true,
    "comments_count": 0,
    "comments_enabled": true,
    "keywords": [
      "example"
    ],
    "is_collaborative": true,
    "is_draft": true
  },
  "content": "example"
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| id | Type: integer |
| page_type | Type: string Enum: page, grid, wysiwyg, template |
| slug | Type: string Example: example |
| title | Type: string Example: example |
| attributes | All of 1 type PageAttributesSchema Type: PageAttributesSchema Example { "created_at": "2025-01-01T00:00:00Z", "modified_at": "2025-01-01T00:00:00Z", "lang": "example", "is_readonly": true, "comments_count": 0, "comments_enabled": true, "keywords": [ "example" ], "is_collaborative": true, "is_draft": true } По умолчанию поле не возвращается Укажите attributes в списке ?fields=attributes, ... для получения в ответе. Example { "created_at": "2025-01-01T00:00:00Z", "modified_at": "2025-01-01T00:00:00Z", "lang": "example", "is_readonly": true, "comments_count": 0, "comments_enabled": true, "keywords": [ "example" ], "is_collaborative": true, "is_draft": true } |
| breadcrumbs | Type: BreadcrumbSchema[] По умолчанию поле не возвращается Укажите breadcrumbs в списке ?fields=breadcrumbs, ... для получения в ответе. Example [ { "id": 0, "title": "example", "slug": "example", "page_exists": true } ] |
| content | Type: string По умолчанию поле не возвращается Укажите content в списке ?fields=content, ... для получения в ответе. Контент страницы в виде строки. Example: example |
| redirect | All of 1 type RedirectSchema Type: RedirectSchema Example { "page_id": 0, "redirect_target": { "id": 0, "slug": "example", "title": "example", "page_type": "page" } } По умолчанию поле не возвращается Укажите redirect в списке ?fields=redirect, ... для получения в ответе. Если редиректа нет, вернется null Example { "page_id": 0, "redirect_target": { "id": 0, "slug": "example", "title": "example", "page_type": "page" } } |




### PageType



An enumeration.


**Type**: string


*Enum:* `page`, `grid`, `cloud_page`, `wysiwyg`, `template`




### PageDetailsSchema



| Name | Description |
| --- | --- |
| id | Type: integer |
| page_type | Type: PageType An enumeration. Enum: page, grid, cloud_page, wysiwyg, template |
| slug | Type: string Example: example |
| title | Type: string Example: example |

**Example**
    
        
```
{
  "id": 0,
  "slug": "example",
  "title": "example",
  "page_type": "page"
}
```


        
            
            
        
    



### RedirectSchema



| Name | Description |
| --- | --- |
| page_id | Type: integer ID страницы, на которую перенаправляет текущая страница. |
| redirect_target | All of 1 type PageDetailsSchema Type: PageDetailsSchema Example { "id": 0, "slug": "example", "title": "example", "page_type": "page" } Например, если задана цепочка редиректов A->B->C->D, для A,B и С, это будет страница D Example { "id": 0, "slug": "example", "title": "example", "page_type": "page" } |

**Example**
    
        
```
{
  "page_id": 0,
  "redirect_target": {
    "id": 0,
    "slug": "example",
    "title": "example",
    "page_type": "page"
  }
}
```


        
            
            
        
    



### BreadcrumbSchema



| Name | Description |
| --- | --- |
| page_exists | Type: boolean |
| slug | Type: string Example: example |
| title | Type: string Example: example |
| id | Type: integer |

**Example**
    
        
```
{
  "id": 0,
  "title": "example",
  "slug": "example",
  "page_exists": true
}
```


        
            
            
        
    



### PageAttributesSchema



| Name | Description |
| --- | --- |
| comments_count | Type: integer |
| comments_enabled | Type: boolean |
| created_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| is_readonly | Type: boolean |
| lang | Type: string Example: example |
| modified_at | Type: string<date-time> Example: 2025-01-01T00:00:00Z |
| is_collaborative | Type: boolean |
| is_draft | Type: boolean |
| keywords | Type: string[] Example [ "example" ] |

**Example**
    
        
```
{
  "created_at": "2025-01-01T00:00:00Z",
  "modified_at": "2025-01-01T00:00:00Z",
  "lang": "example",
  "is_readonly": true,
  "comments_count": 0,
  "comments_enabled": true,
  "keywords": [
    "example"
  ],
  "is_collaborative": true,
  "is_draft": true
}
```

---

- [Request](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__delete_page#request)
  - [Path parameters](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__delete_page#path-parameters)
- [Responses](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__delete_page#responses)
- [200 OK](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__delete_page#200-ok)
  - [Body](https://yandex.ru/support/wiki/ru/api-ref/pages/ru/api-ref/pages/pages__delete_page#body)


