# Примеры использования API Яндекс Вики


- [1. Создать страницу и добавить контент](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#create-page)
- [2. Создать динамическую таблицу, добавить столбцы и строки](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#grid)
- [3. Создать страницу и оставить комментарии](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#comments)
- [4. Получить поддерево страниц](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#descendants)
- [5. Удалить и восстановить страницу по токену восстановления](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#delete-and-recover)
- [6. Загрузить файл и прикрепить к странице](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/examples#upload-files)

В этом разделе приведены примеры скриптов на языке Python, которые используют API Яндекс Вики для управления формами и ответами.


Во всех примерах для аутентификации используется OAuth-токен. Получение токена описано в разделе [Доступ к API](https://yandex.ru/support/wiki/ru/api-ref/ru/api-ref/access).


## 1. Создать страницу и добавить контент



Ниже продемонстрируем пример скрипта, который выполняет действия:


- Создание новой страницы
- Изменение контента страницы
- Получение атрибутов страницы по ее слагу (пути)

Текст скрипта api_example_1.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}


def create_wiki_page(
    slug: str,
    title: str,
    content: str,
) -> int:
    """
    Создать новую страницу

    Параметры:
    - slug: слаг создаваемой страницы
    - title: заголовок страницы
    - content: текст страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    body = {
        'slug': slug,
        'title': title,
        'content': content,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать страницу: {response.status_code} {response.text}')
        return None

    res = response.json()
    return res.get('id')


def change_wiki_page(
    page_id: int,
    title: str = None,
    content: str = None,
) -> bool:
    """
    Изменить существующую страницу

    Параметры:
    - page_id: код страницы
    - title: заголовок страницы
    - content: текст страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}'
    body = {}
    if title:
        body['title'] = title
    if content:
        body['content'] = content
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def append_wiki_page_content(
    page_id: int,
    content: str,
    location: str = None,
) -> bool:
    """
    Добавить контент на существующую страницу

    Параметры:
    - page_id: код страницы
    - content: текст для вставки
    - location: позиция для вставки текста,
      возможна вставка в начало страницы `top`, в конец страницы `bottom` или под якорь, например `#fragment`
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/append-content'
    body = {
        'content': content,
    }
    if location in ('top', 'bottom'):
        body['body'] = {'location': location}
    elif isinstance(location, str) and location.startswith('#'):
        body['anchor'] = {'name': location}
    else:
        body['body'] = {'location': 'bottom'}
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def get_wiki_page_attributes(slug: str) -> int:
    """
    Получить атрибуты существующей страницы по ее слагу

    Параметры:
    - slug: слаг существующей страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    params = {
        'slug': slug,
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()


def main():
    if len(sys.argv) < 2:
        return
    slug = sys.argv[1]

    # Создадим новую страницу
    new_page_id = create_wiki_page(
        slug=slug,
        title='Тестовая страница',
        content=(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
            'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n'
        ),
    )
    if new_page_id:
        print(f'Создана страница с кодом {new_page_id}')

    # Обновим контент страницы (важно, метод меняет всю страницу)
    is_changed = change_wiki_page(
        page_id=new_page_id,
        title='Обновленная тестовая страница',
        content=(
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
            'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n'
            'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris '
            'nisi ut aliquip ex ea commodo consequat.\n'
            'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum '
            'dolore eu fugiat nulla pariatur.\n'
            'Excepteur sint occaecat cupidatat non proident, '
            'sunt in culpa qui officia deserunt mollit anim id est laborum.\n'
        ),
    )
    if is_changed:
        print('Контент страницы обновлен')

    # Получим атрибуты страницы по ее слагу
    page_attributes = get_wiki_page_attributes(slug=slug)
    if not page_attributes:
        print('Вики страница не найдена')
        sys.exit(1)
    page_id = page_attributes.get('id')
    print(f'Найдена страница с кодом {page_id}')


if __name__ == '__main__':
    main()
```


        
            
            
        
    

Пример запуска скрипта (в качестве аргумента передается слаг страницы, которая будет создана):


    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_1.py 'users/test/page'
Создана страница с кодом 49497033
Контент страницы обновлен
Найдена страница с кодом 49497033
```


        
            
            
        
    

## 2. Создать динамическую таблицу, добавить столбцы и строки



Ниже продемонстрируем пример скрипта, который выполняет действия:


- Добавление новой динамической таблицы на существующую страницу
- Добавление в таблицу колонок и строк
- Изменение ячеек строки
- Публикация таблицы на странице

Текст скрипта api_example_2.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}


def get_wiki_page_attributes(slug: str) -> int:
    """
    Получить атрибуты существующей страницы по ее слагу

    Параметры:
    - slug: слаг существующей страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    params = {
        'slug': slug,
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()


def append_wiki_page_content(
    page_id: int,
    content: str,
    location: str = None,
) -> bool:
    """
    Добавить контент на существующую страницу

    Параметры:
    - page_id: код страницы
    - content: текст для вставки
    - location: позиция для вставки текста,
      возможна вставка в начало страницы `top`, в конец страницы `bottom`
      или под якорь, например `#fragment`
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/append-content'
    body = {
        'content': content,
    }
    if location in ('top', 'bottom'):
        body['body'] = {'location': location}
    elif isinstance(location, str) and location.startswith('#'):
        body['anchor'] = {'name': location}
    else:
        body['body'] = {'location': 'bottom'}
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def create_wiki_grid(page_id: int, title: str) -> int:
    """
    Создать новую таблицу

    Параметры:
    - page_id: код страницы
    - title: заголовок таблицы

    Важно, после создания таблица доступна только через интерфейс просмотра ресурсов,
    ее еще нужно добавить на страницу.
    """
    url = f'{WIKI_PUBLIC_API}/grids'
    body = {
        'page': {'id': page_id},
        'title': title,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code == 200:
        res = response.json()
        return res.get('id')


def insert_grid_columns(grid_id: str, columns: list[dict]) -> bool:
    """
    Добавить колонки в таблицу

    Параметры:
    - grid_id: код таблицы
    - columns: список колонок для добавления
    """
    url = f'{WIKI_PUBLIC_API}/grids/{grid_id}/columns'
    body = {
        'columns': columns,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def insert_grid_rows(grid_id: str, rows: list[dict]) -> bool:
    """
    Добавить строки в таблицу

    Параметры:
    - grid_id: код таблицы
    - rows: список строк для добавления
    """
    url = f'{WIKI_PUBLIC_API}/grids/{grid_id}/rows'
    body = {
        'rows': rows,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def change_grid_cells(grid_id: str, cells: list[dict]) -> bool:
    """
    Изменить ячейки в таблице

    Параметры:
    - grid_id: код таблицы
    - cells: список ячеек для изменения
    """
    url = f'{WIKI_PUBLIC_API}/grids/{grid_id}/cells'
    body = {
        'cells': cells,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    return response.status_code == 200


def main():
    if len(sys.argv) < 2:
        return
    slug = sys.argv[1]

    # Получим атрибуты страницы по ее слагу
    page_attributes = get_wiki_page_attributes(
        slug=slug,
    )
    if not page_attributes:
        print('Вики страница не найдена')
        sys.exit(1)
    page_id = page_attributes.get('id')
    print(f'Найдена страница с кодом {page_id}')

    # Создадим новую таблицу
    grid_id = create_wiki_grid(
        page_id=page_id,
        title='Новая таблица',
    )
    if grid_id:
        print(f'Создана таблица с кодом {grid_id}')

    # Добавим колонки в новую таблицу, колонки могут иметь разный тип
    is_changed = insert_grid_columns(
        grid_id=grid_id,
        columns=[
            {
                'slug': 'id',
                'title': 'ID',
                'type': 'number',
                'required': True,
            },
            {
                'slug': 'name',
                'title': 'Name',
                'type': 'string',
                'required': False,
            },
        ],
    )
    if is_changed:
        print('В таблицу добавлены новые колонки')

    # Добавим строки в новую таблицу
    is_changed = insert_grid_rows(
        grid_id=grid_id,
        rows=[
            {'id': 1, 'name': 'Один'},
            {'id': 2, 'name': 'Два'},
            {'id': 3, 'name': 'Три'},
            {'id': 4, 'name': 'Четыре'},
            {'id': 5, 'name': 'Пять'},
        ],
    )
    if is_changed:
        print('В таблицу добавлены новые строки')

    # Изменим ячейки на второй строке в таблице
    is_changed = change_grid_cells(
        grid_id=grid_id,
        cells=[
            {'row_id': 2, 'column_slug': 'id', 'value': 22},
            {'row_id': 2, 'column_slug': 'name', 'value': 'Двадцать два'},
        ],
    )
    if is_changed:
        print('В таблице изменена вторая строка')

    # Поместим новую таблицу в конец страницы
    is_changed = append_wiki_page_content(
        page_id=page_id,
        content=f'\n{{% wgrid id="{grid_id}" %}}',
    )
    if is_changed:
        print('В конец страницы добавлена созданная таблица')


if __name__ == '__main__':
    main()
```


        
            
            
        
    

    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_2.py 'users/test/page'
Найдена страница с кодом 49497033
Создана таблица с кодом 7d8f08c1-fbbf-4015-83b5-362ca2fc965c
В таблицу добавлены новые колонки
В таблицу добавлены новые строки
В таблице изменена вторая строка
В конец страницы добавлена созданная таблица
```


        
            
            
        
    

## 3. Создать страницу и оставить комментарии



Ниже продемонстрируем пример скрипта, который выполняет действия:


- Создание страницы по указанному адресу
- Добавление комментариев, включая комментарии-ответы

Текст скрипта api_example_3.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}


def create_wiki_page(slug: str, title: str, content: str) -> int | None:
    """
    Создать новую страницу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    body = {
        'slug': slug,
        'title': title,
        'content': content,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать страницу: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def get_wiki_page_id(slug: str) -> int | None:
    """
    Получить код существующей страницы по её слагу (адресу)
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    response = requests.get(url, params={'slug': slug}, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json().get('id')


def create_comment(page_id: int, body: str, parent_id: int = None, thread_id: int = None) -> int | None:
    """
    Создать комментарий на странице
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/comments'
    data = {'body': body}
    if parent_id is not None:
        data['parent_id'] = parent_id
    if thread_id is not None:
        data['thread_id'] = thread_id
    response = requests.post(url, json=data, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать комментарий: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def get_page_comments(page_id: int) -> list | None:
    """
    Получить список комментариев страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/comments'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось получить комментарии: {response.status_code} {response.text}')
        return None
    return response.json().get('results')


def main():
    if len(sys.argv) < 2:
        return
    slug = sys.argv[1]

    # Получим существующую страницу или создадим новую
    page_id = get_wiki_page_id(slug=slug)
    if page_id:
        print(f'Найдена страница с кодом {page_id}')
    else:
        page_id = create_wiki_page(
            slug=slug,
            title='Тестовая страница с комментариями',
            content='Смотрите комментарии.\n',
        )
        if not page_id:
            return
        print(f'Создана страница с кодом {page_id}')

    # Создадим два корневых комментария и три ответа:
    comment_1 = create_comment(page_id=page_id, body='Первый комментарий')
    if comment_1:
        print(f'Создан комментарий {comment_1}')

    comment_2 = create_comment(page_id=page_id, body='Второй комментарий')
    if comment_2:
        print(f'Создан комментарий {comment_2}')

    comment_3 = create_comment(page_id=page_id, body='Третий комментарий', parent_id=comment_1, thread_id=comment_1)
    if comment_3:
        print(f'Создан комментарий {comment_3}')

    comment_4 = create_comment(page_id=page_id, body='Четвёртый комментарий', parent_id=comment_1, thread_id=comment_1)
    if comment_4:
        print(f'Создан комментарий {comment_4}')

    comment_5 = create_comment(page_id=page_id, body='Пятый комментарий', parent_id=comment_2, thread_id=comment_2)
    if comment_5:
        print(f'Создан комментарий {comment_5}')


if __name__ == '__main__':
    main()
```


        
            
            
        
    

    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_3.py 'users/test/page'
Создана страница с кодом 49497133
Создан комментарий 856798
Создан комментарий 856799
Создан комментарий 856800
Создан комментарий 856801
Создан комментарий 856802
```


        
            
            
        
    

## 4. Получить поддерево страниц



Ниже продемонстрируем пример скрипта, который выполняет действия:


- Создание дерева из 10 страниц по указанному адресу
- Получение и вывод поддерева для указанной страницы

Текст скрипта api_example_4.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}



def create_wiki_page(slug: str, title: str, content: str) -> int | None:
    """
    Создать новую страницу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    body = {
        'slug': slug,
        'title': title,
        'content': content,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать страницу {slug}: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def get_wiki_page_id(slug: str) -> int | None:
    """
    Получить код существующей страницы по её слагу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    response = requests.get(url, params={'slug': slug}, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json().get('id')


def get_descendants(slug: str, include_self: bool = False) -> list | None:
    """
    Получить список потомков страницы по её слагу
    """
    url = f'{WIKI_PUBLIC_API}/pages/descendants'
    params = {
        'slug': slug,
        'include_self': include_self,
        'page_size': 100,
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json().get('results')


def main():
    if len(sys.argv) < 2:
        return
    slug = sys.argv[1]

    pages = [
        (slug, 'Тестовая страница для подстраниц'),
        (f'{slug}/page-1', 'Страница 1'),
        (f'{slug}/page-1/sub-1', 'Подстраница 1-1'),
        (f'{slug}/page-1/sub-2', 'Подстраница 1-2'),
        (f'{slug}/page-2', 'Страница 2'),
        (f'{slug}/page-2/sub-1', 'Подстраница 2-1'),
        (f'{slug}/page-2/sub-2', 'Подстраница 2-2'),
        (f'{slug}/page-3', 'Страница 3'),
        (f'{slug}/page-4', 'Страница 4'),
        (f'{slug}/page-5', 'Страница 5'),
    ]

    # Создадим дерево страниц
    for page_slug, title in pages:
        page_id = get_wiki_page_id(slug=page_slug)
        if page_id:
            print(f'Страница найдена: {page_slug} (код {page_id})')
        else:
            page_id = create_wiki_page(slug=page_slug, title=title, content=f'{title}.\n')
            if not page_id:
                return
            print(f'Страница создана: {page_slug} (код {page_id})')

    # Получим потомков от указанной страницы (включая саму страницу)
    print(f'Потомки для {slug} включительно:')
    subtree = get_descendants(slug=slug, include_self=True)
    if subtree is not None:
        for page in subtree:
            print(f'- {page.get("slug")}')
        print(f'Всего: {len(subtree)}')


if __name__ == '__main__':
    main()
```


        
            
            
        
    

    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_4.py 'users/test/descendants'
Страница создана: users/test/descendants (код 49497245)
Страница создана: users/test/descendants/page-1 (код 49497246)
Страница создана: users/test/descendants/page-1/sub-1 (код 49497247)
Страница создана: users/test/descendants/page-1/sub-2 (код 49497248)
Страница создана: users/test/descendants/page-2 (код 49497249)
Страница создана: users/test/descendants/page-2/sub-1 (код 49497250)
Страница создана: users/test/descendants/page-2/sub-2 (код 49497252)
Страница создана: users/test/descendants/page-3 (код 49497253)
Страница создана: users/test/descendants/page-4 (код 49497254)
Страница создана: users/test/descendants/page-5 (код 49497255)
Потомки для users/test/descendants включительно:
- users/test/descendants
- users/test/descendants/page-1
- users/test/descendants/page-1/sub-1
- users/test/descendants/page-1/sub-2
- users/test/descendants/page-2
- users/test/descendants/page-2/sub-1
- users/test/descendants/page-2/sub-2
- users/test/descendants/page-3
- users/test/descendants/page-4
- users/test/descendants/page-5
Всего: 10
```


        
            
            
        
    

## 5. Удалить и восстановить страницу по токену восстановления



Ниже продемонстрируем пример скрипта, который выполняет действия:


- Создание страницы по указанному адресу
- Удаление созданной страницы и получение токена восстановления
- Восстановление страницы по полученному токену

Текст скрипта api_example_5.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}


def create_wiki_page(slug: str, title: str, content: str) -> int | None:
    """
    Создать новую страницу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    body = {
        'slug': slug,
        'title': title,
        'content': content,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать страницу: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def get_wiki_page_id(slug: str) -> int | None:
    """
    Получить код существующей страницы по её слагу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    response = requests.get(url, params={'slug': slug}, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json().get('id')


def delete_wiki_page(page_id: int) -> str | None:
    """
    Удалить страницу и вернуть токен восстановления
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}'
    response = requests.delete(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось удалить страницу: {response.status_code} {response.text}')
        return None
    return response.json().get('recovery_token')


def recover_wiki_page(token: str) -> int | None:
    """
    Восстановить удалённую страницу по токену восстановления
    """
    url = f'{WIKI_PUBLIC_API}/recovery_tokens/{token}/recover'
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось восстановить страницу: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def main():
    if len(sys.argv) < 2:
        return
    slug = sys.argv[1]

    # Получим существующую страницу или создадим новую
    page_id = get_wiki_page_id(slug=slug)
    if page_id:
        print(f'Найдена страница с кодом {page_id}')
    else:
        page_id = create_wiki_page(
            slug=slug,
            title='Тестовая страница для восстановления',
            content='Тестовый контент страницы.\n',
        )
        if not page_id:
            return
        print(f'Создана страница с кодом {page_id}')

    # Удалим страницу и получим токен восстановления
    recovery_token = delete_wiki_page(page_id=page_id)
    if not recovery_token:
        return
    print(f'Страница удалена, токен восстановления: {recovery_token}')

    # Восстановим страницу по токену
    restored_id = recover_wiki_page(token=recovery_token)
    if not restored_id:
        return
    print(f'Страница восстановлена с кодом {restored_id}')


if __name__ == '__main__':
    main()
```


        
            
            
        
    

    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_5.py 'users/test/page-recover'
Создана страница с кодом 49497351
Страница удалена, токен восстановления: b5807bca-4a69-4148-bb43-fab64fd20942
Страница восстановлена с кодом 49497351
```


        
            
            
        
    

## 6. Загрузить файл и прикрепить к странице



Загрузка файлов выполняется через сессии загрузки по частям (каждая часть до 5 МБ).


Ниже продемонстрируем пример скрипта, который выполняет действия:


- Создание страницы
- Загрузка файла
- Прикрепление файла к странице
- Вывод всех ресурсов и вложений страницы

Текст скрипта api_example_6.py
    
        
```
import os
import requests
import sys

WIKI_PUBLIC_API = 'https://api.wiki.yandex.net/v1'
WIKI_TOKEN = os.environ.get('WIKI_TOKEN')
ORG_ID = os.environ.get('ORG_ID')

CHUNK_SIZE = 5 * 1024 * 1024  # 5 МБ — минимальный размер части для multipart upload

HEADERS = {
    'Authorization': f'OAuth {WIKI_TOKEN}',
    'X-Org-Id': ORG_ID,
}


def get_file_pattern(file_url: str, file_name: str) -> str:
    return f'{{% file src="{file_url}" name="{file_name}" %}}'


def create_wiki_page(slug: str, title: str, content: str) -> int | None:
    """
    Создать новую страницу
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    body = {
        'slug': slug,
        'title': title,
        'content': content,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать страницу: {response.status_code} {response.text}')
        return None
    return response.json().get('id')


def get_wiki_page_id(slug: str) -> int | None:
    """
    Получить код существующей страницы по её слагу (адресу)
    """
    url = f'{WIKI_PUBLIC_API}/pages'
    response = requests.get(url, params={'slug': slug}, headers=HEADERS)
    if response.status_code != 200:
        return None
    return response.json().get('id')


def create_upload_session(file_name: str, file_size: int) -> str | None:
    """
    Создать сессию загрузки файла
    """
    url = f'{WIKI_PUBLIC_API}/upload_sessions'
    body = {
        'file_name': file_name,
        'file_size': file_size,
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось создать сессию загрузки: {response.status_code} {response.text}')
        return None
    return response.json().get('session_id')


def upload_file_part(session_id: str, part_number: int, data: bytes) -> bool:
    """
    Загрузить часть файла в рамках сессии
    """
    url = f'{WIKI_PUBLIC_API}/upload_sessions/{session_id}/upload_part'
    headers = {**HEADERS, 'Content-Type': 'application/octet-stream'}
    response = requests.put(
        url,
        params={'part_number': part_number},
        data=data,
        headers=headers,
        stream=True,
    )
    return response.status_code == 200


def finish_upload_session(session_id: str) -> bool:
    """
    Завершить сессию загрузки файла
    """
    url = f'{WIKI_PUBLIC_API}/upload_sessions/{session_id}/finish'
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось завершить сессию загрузки: {response.status_code} {response.text}')
        return False
    return True


def attach_file_to_page(page_id: int, session_id: str) -> list | None:
    """
    Прикрепить загруженный файл к странице
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/attachments'
    body = {
        'upload_sessions': [session_id],
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось прикрепить файл к странице: {response.status_code} {response.text}')
        return None
    return response.json().get('results')


def append_wiki_page_content(page_id: int, content: str) -> bool:
    """
    Добавить контент в конец страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/append-content'
    body = {
        'content': content,
        'body': {'location': 'bottom'},
    }
    response = requests.post(url, json=body, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось добавить контент на страницу: {response.status_code} {response.text}')
        return False
    return True


def get_page_resources(page_id: int) -> list | None:
    """
    Получить список ресурсов страницы (вложения, таблицы)
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/resources'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось получить ресурсы страницы: {response.status_code} {response.text}')
        return None
    return response.json().get('results')


def get_page_attachments(page_id: int) -> list | None:
    """
    Получить список вложений страницы
    """
    url = f'{WIKI_PUBLIC_API}/pages/{page_id}/attachments'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Не удалось получить вложения страницы: {response.status_code} {response.text}')
        return None
    return response.json().get('results')


def main():
    if len(sys.argv) < 3:
        return
    slug = sys.argv[1]
    file_path = sys.argv[2]

    # Получим существующую страницу или создадим новую
    page_id = get_wiki_page_id(slug=slug)
    if page_id:
        print(f'Найдена страница с кодом {page_id}')
    else:
        page_id = create_wiki_page(
            slug=slug,
            title='Тестовая страница с вложениями',
            content='Какой-то текст.\n',
        )
        if not page_id:
            return
        print(f'Создана страница с кодом {page_id}')

    # Прочитаем файл для загрузки
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    # Создадим сессию загрузки
    session_id = create_upload_session(
        file_name=file_name,
        file_size=file_size,
    )
    if not session_id:
        return
    print(f'Создана сессия загрузки {session_id}')

    # Загрузим файл по частям (каждая часть — не менее 5 МБ, кроме последней)
    with open(file_path, 'rb') as f:
        part_number = 1
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            if not upload_file_part(session_id=session_id, part_number=part_number, data=chunk):
                return
            print(f'Загружена часть {part_number}')
            part_number += 1

    # Завершим сессию загрузки
    if not finish_upload_session(session_id=session_id):
        return
    print('Сессия загрузки завершена')

    # Прикрепим файл к странице
    attached = attach_file_to_page(page_id=page_id, session_id=session_id)
    if not attached:
        return
    print('Файл прикреплён к странице')

    # Вставим упоминание файла в конец страницы
    file_url = attached[0].get('download_url')
    file_name = attached[0].get('name')
    text = f'Прикреплённый файл: {get_file_pattern(file_url, file_name)}'
    if append_wiki_page_content(page_id=page_id, content=text):
        print(f'Упоминание файла {file_name} добавлено на страницу')

    # Получим список ресурсов страницы
    resources = get_page_resources(page_id=page_id)
    if resources is not None:
        print(f'\nРесурсы страницы ({len(resources)}):')
        for resource in resources:
            resource_type = resource.get('type')
            item = resource.get('item', {})
            print(f'- Тип: {resource_type}, имя: {item.get('name')}')

    # Получим список вложений страницы
    attachments = get_page_attachments(page_id=page_id)
    if attachments is not None:
        print(f'\nВложения страницы ({len(attachments)}):')
        for attachment in attachments:
            print(
                f'- Код: {attachment.get('id')}, '
                f'имя: {attachment.get('name')}, '
                f'размер: {attachment.get('size')} МБ, '
                f'тип: {attachment.get('mimetype')}'
            )


if __name__ == '__main__':
    main()
```


        
            
            
        
    

    
        
```
$ WIKI_TOKEN=$(cat .wiki-token) ORG_ID=$(cat .org-id) python api_example_6.py 'users/test/upload' 'file.zip'
Создана страница с кодом 49497369
Создана сессия загрузки e127b2a1-e183-4abd-b6c7-3131ea637f14
Загружена часть 1
Сессия загрузки завершена
Файл прикреплён к странице
Упоминание файла file.zip добавлено на страницу

Ресурсы страницы (1):
- Тип: attachment, имя: file.zip

Вложения страницы (1):
- Код: 23066834, имя: file.zip, размер: 2.04 МБ, тип: application/zip
```

---

