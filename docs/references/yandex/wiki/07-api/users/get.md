# Получить пользователя




Возвращает информацию о текущем пользователе.


## Request






GET


    
        
```
https://api.wiki.yandex.net/v1/users/me
```


        
            
            
        
    




## Responses




## 200 OK



OK



### Body


application/json
    
        
```
{
  "username": "example",
  "home_cluster": "example",
  "identity": {
    "uid": "example",
    "cloud_uid": "example"
  },
  "org": {
    "dir_id": "example",
    "collab_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```


        
            
            
        
    

| Name | Description |
| --- | --- |
| identity | Type: UserIdentity Example { "uid": "example", "cloud_uid": "example" } |
| org | Type: OrganizationIdentity Example { "dir_id": "example", "collab_id": "123e4567-e89b-12d3-a456-426614174000" } |
| username | Type: string Example: example |
| home_cluster | Type: string Example: example |




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


        
            
            
        
    



### OrganizationIdentity



| Name | Description |
| --- | --- |
| collab_id | Type: string<uuid> Example: 123e4567-e89b-12d3-a456-426614174000 |
| dir_id | Type: string Example: example |

**Example**
    
        
```
{
  "dir_id": "example",
  "collab_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

