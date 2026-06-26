---
source: https://yandex.ru/support/forms/en/api-ref/examples
title: "Yandex Forms API usage examples |"
word_count: 3038
token_estimate: 8172
extracted: "2026-05-22T18:06:51Z"
mode: quality
---

This page describes examples of Python scripts that use the Yandex Forms API to manage forms and responses.

All examples use an OAuth token for authentication. To learn how to get a token, see [Accessing the Yandex Forms API](https://yandex.ru/support/forms/en/api-ref/access).

# 1\. Publishing and unpublishing an existing form

The ability to publish a form via the API is useful when you need to implement more complex logic than the default options available in Forms, such as scheduling publication at a specific time or unpublishing after reaching a certain number of responses.

See the method descriptions:

-   [Publish form](https://yandex.ru/support/forms/en/api-ref/surveys/events_v1_views_surveys_publish_survey_view)
-   [Unpublish form](https://yandex.ru/support/forms/en/api-ref/surveys/events_v1_views_surveys_unpublish_survey_view)

Text of the api\_example\_1.py script

```
import os
import sys

import requests

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def publish_survey(survey_id: str) -> bool:
    """
    Publish a form.
    The form will not be published in the following cases:
    - The form is blocked.
    - The form has already reached its maximum number of responses.
    - The form has automatic publishing enabled and the scheduled publication time has not yet arrived.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/publish'
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to publish the form: {response.status_code} {response.text}')
        return False
    return True

def unpublish_survey(survey_id: str) -> bool:
    """
    You can unpublish any published form,
    including those with automatic publishing enabled if the scheduled unpublish time has not yet arrived.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/unpublish'
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to unpublish the form: {response.status_code} {response.text}')
        return False
    return True

def main():
    if len(sys.argv) < 2:
        return

    survey_id = sys.argv[1]
    # To publish
    if publish_survey(survey_id):
        print(f'Form {survey_id} published')

    # To unpublish
    # if unpublish_survey(survey_id):
    #     print(f'Form {survey_id} unpublished')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_1.py 6800cd9202848f10b272a9cc
Form 6800cd9202848f10b272a9cc published
```

# 2\. Filling out a form using a script

The Yandex Forms API allows forms to be filled out anonymously (without an OAuth token), unless this option has been explicitly disabled (the **Show form only to authorized users** option in the form settings).

To submit a form response on behalf of a specific user, make a request using an OAuth token.

A form's field values (answers to questions) are passed in JSON format as question ID-value pairs.

See the [Submit form response](https://yandex.ru/support/forms/en/api-ref/filling/events_v1_views_frontend_submit_form_view) method description.

Text of the api\_example\_2.py script

```
import json
import os
import requests
import sys

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
}

def submit_survey(survey_id: str, **fields) -> int:
    """
    The function submits a form response.
    It accepts a JSON object containing the completed fields as input.
    See the example script for the correct field format.
    Important: Form filling via the public API is only available for forms within an organization.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/form'
    response = requests.post(url, json=fields, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to submit the form response: {response.status_code} {response.text}')
        return None

    result = response.json()
    return result.get('answer_id')

def main():
    if len(sys.argv) < 3:
        return

    survey_id = sys.argv[1]
    fields = json.loads(sys.argv[2])
    answer_id = submit_survey(survey_id, **fields)
    if answer_id:
        print(f'Form {survey_id} completed, response {answer_id} created')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) python api_example_2.py 6800cd9202848f10b272a9cc '
{
  "id-text": "test it",
  "id-bool": true,
  "id-integer": 42,
  "id-enum": ["id-second", "id-third"],
  "id-file": [{"path": "/s3-bucket/321/abc123_test.txt"}]
}
'
Form 6800cd9202848f10b272a9cc completed, response 2037950340 created
```

# 3\. Retrieving a form response

Let's look at an example of retrieving a form response by its ID.

See the [Get answer data](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view) method description.

The response data is returned in JSON format. You can process it in Python or using the jq command-line utility, and convert it to CSV format if needed.

Text of the api\_example\_3.py script

```
import json
import os
import requests
import sys

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def get_one_answer(answer_id: int):
    """
    Retrieve a single response by its ID.
    """
    url = f'{FORMS_PUBLIC_API}/answers'
    fields = {'answer_id': answer_id}
    response = requests.get(url, fields, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to retrieve the form response: {response.status_code} {response.text}')
        return None
    return response.json()

def main():
    if len(sys.argv) < 2:
        return

    answer_id = int(sys.argv[1])
    answer_data = get_one_answer(answer_id)
    if answer_data:
        survey_id = answer_data['survey']['id']
        print(f'Content of response {answer_id} for form {survey_id} received', file=sys.stderr)
        print(json.dumps(answer_data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

Example of running the script using the jq utility:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_3.py 51875 \
  | jq '.data[] | [.id, .value | if type == "array" then [.[].label] | join(", ") else . end] | @csv'
Content of response 51875 for form 69c28042bcc069001756d13c received
"\"id-text\",\"Строка\""
"\"id-number\",123"
"\"id_bool\",true"
```

The Yandex Forms API allows you to retrieve form responses in JSON format with paginated access to results.

See the [Get answer data](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_get_answer_view) method description.

In the example below, the script processes the responses to produce a CSV-compatible output.

Text of the api\_example\_4.py script

```
import csv
import os
import requests
import sys

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def get_value(item):
    value = item.get('value')
    if value is None:
        return ''
    if isinstance(value, list):
        return ', '.join(value)
    return value

def fetch_answers(survey_id: str, *, page_size: int = 50):
    """
    Retrieve form responses.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/answers?page_size={page_size}'
    columns = None
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            break

        result = response.json()
        if columns is None:
            columns = result.get('columns') or []
            yield ['ID', 'Created'] + [
                column.get('text')
                for column in columns
            ]

        for answer in result.get('answers') or []:
            yield [answer.get('id'), answer.get('created')] + [
                get_value(item)
                for item in answer.get('data') or []
            ]

        next_page = result.get('next')
        if not next_page:
            break

        next_path = next_page.get('next_url')
        if not next_path:
            break

        url = FORMS_PUBLIC_API + next_path.removeprefix('/v1')

def main():
    if len(sys.argv) < 2:
        return

    survey_id = sys.argv[1]
    print(f'Responses to form {survey_id}', file=sys.stderr)
    csvwriter = csv.writer(sys.stdout, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for answer in fetch_answers(survey_id):
        csvwriter.writerow(answer)

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_4.py 6800cd9202848f10b272a9cc
Responses to form 6800cd9202848f10b272a9cc
"ID","Created","Short Text","Boolean","Integer","Enumeration"
"2037950340","2025-04-17T11:30:17Z","test it","True","42","Second, Third"
"2037859858","2025-04-17T10:14:01Z","test it","True","42","Second"
```

# 5\. Exporting all form responses to a file

To export responses to a file, we'll use several Yandex Forms API calls:

-   The first call runs a background task that downloads the responses and generates the output file. See [Export answers](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_view).
-   Since the export task may take some time, the second API call checks its status. See [Get operation result](https://yandex.ru/support/forms/en/api-ref/operations/events_v1_views_operations_get_operation_view).
-   Once the task is complete, the third call downloads the result. See [Get the result of answer export](https://yandex.ru/support/forms/en/api-ref/answers/events_v1_views_answers_export_answers_results_view).

Text of the api\_example\_5.py script

```
import os
import requests
import sys
import time

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def start_export(survey_id: str) -> str:
    """
    Starts a background process to export responses.
    Returns the ID of the started operation.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/answers/export'
    params = {'format': 'xlsx'}
    response = requests.post(url, json=params, headers=HEADERS)
    if response.status_code == 202:
        result = response.json()
        operation_id = result.get('id')
        return operation_id
    print(response.status_code, response.json())

def check_finished(operation_id: str) -> bool:
    url = f'{FORMS_PUBLIC_API}/operations/{operation_id}'
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        result = response.json()
        return result.get('status') == 'ok'

def download_result(survey_id: str, operation_id: str) -> bytes:
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/answers/export-results'
    params = {'task_id': operation_id}
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.content

def main():
    if len(sys.argv) < 2:
        return

    survey_id = sys.argv[1]
    operation_id = start_export(survey_id)
    if operation_id:
        print(f'Operation {operation_id} started')

        while not check_finished(operation_id):
            print('...')
            time.sleep(5)

        content = download_result(survey_id, operation_id)
        if content:
            filename = f'{survey_id}.xlsx'
            with open(filename, 'wb') as f:
                f.write(content)

            print(f'Responses exported to file {filename}')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_5.py 6800cd9202848f10b272a9cc
Operation 0946779c-6a57-4070-b062-5d7ebdb65142 started
Responses exported to file 6800cd9202848f10b272a9cc.xlsx
```

# 6\. Uploading and retrieving files

In the example below, the script uploads a file to the form and returns a link that can be used to fill in **File** fields, as shown in the [2\. Filling out a form using a script](https://yandex.ru/support/forms/en/api-ref/examples#autofill) example.

See the [Upload file to populate form](https://yandex.ru/support/forms/en/api-ref/files/events_v1_views_files_save_survey_file_view) method description.

Text of the api\_example\_6.py script

```
import os
import requests
import sys
from pathlib import Path

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def upload_file(survey_id: str, filename: Path) -> str:
    """
    The function uploads a file and returns a link that can be used to fill in a File field in the form.
    Important: You can only upload a file if personal file storage is enabled in the form settings.
How to enable storage is described in the documentation https://yandex.ru/support/forms/storage-for-attached-files#s3-ext

    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/files'
    with open(filename, 'rb') as f:
        files = [
            ('file', (filename.name, f.read(), 'application/octet-stream')),
        ]
    response = requests.post(url, files=files, headers=HEADERS)
    if response.status_code == 201:
        result = response.json()
        return result.get('path')

def download_file(filepath: str) -> bytes:
    """
    Download the uploaded file.
    """
    url = f'{FORMS_PUBLIC_API}/files'
    params = {'path': filepath}
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.content

def main():
    if len(sys.argv) < 3:
        return

    survey_id = sys.argv[1]
    filename = Path(sys.argv[2])
    uploaded_path = upload_file(survey_id, filename.expanduser())
    print(f'Path to the uploaded file: {uploaded_path}')

    content = download_file(uploaded_path)
    print(content)

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ echo 'Hello world' > hello.txt

$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_6.py 6800cd9202848f10b272a9cc hello.txt
Path to the uploaded file: /25871573/6800cd9202848f10b272a9cc/68061a8e381ea60011e104b3_hello.txt
b'Hello world\n'
```

# 7\. Creating a form, adding a question, and publishing

In the example below, the script creates a form, adds a question, and publishes it.

Text of the api\_example\_7.py script

```
import os
import requests

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def create_survey() -> str:
    """
    Creates a new form.
    Returns the ID of the created form.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/'
    payload = {
        'name': 'Test form',
        'texts': {
            'submit': 'Submit',
            'title': 'Thank you for your responses!',
            'subtitle': 'Your responses have been received.',
        },
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to create the form: {response.status_code} {response.text}')
        return None

    result = response.json()
    survey_id = result['id']
    return survey_id

def add_question(survey_id: str, payload: dict) -> int:
    """
    Adds a question to the form.
    Returns the ID of the created question.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/questions/'
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to add the question: {response.status_code} {response.text}')
        return None

    result = response.json()
    question_id = result['id']
    return question_id

def publish_survey(survey_id: str) -> None:
    """
    Publishes the form.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/publish/'
    response = requests.post(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to publish the form: {response.status_code} {response.text}')

def main():
    survey_id = create_survey()
    print(f'Form {survey_id} created')

    text_question = {
        'type': 'string',
        'label': 'What is your name?',
        'placeholder': 'Enter your name',
        'multiline': False,
    }
    question_id = add_question(survey_id, text_question)
    print(f'Text question {question_id} added')

    choice_question = {
        'type': 'enum',
        'label': 'How do you rate our product?',
        'widget': 'radio',
        'items': [
            {'label': 'Excellent'},
            {'label': 'Good'},
            {'label': 'Satisfactory'},
            {'label': 'Poor'},
        ],
    }
    question_id = add_question(survey_id, choice_question)
    print(f'Choice question {question_id} added')

    publish_survey(survey_id)
    print(f'Form {survey_id} published')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_7.py
Form 69c28935084164000de6f9b5 created
Text question 72885 added
Choice question 72886 added
Form 69c28935084164000de6f9b5 published
```

# 8\. Creating questions of various types and moving them

In the example below, the script creates questions of various types, distributes them across form pages, and creates a series of questions.

Text of the api\_example\_8.py script

```
import os
import requests

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def create_survey() -> str:
    """
    Creates a new form.
    Returns the ID of the created form.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/'
    payload = {
        'name': 'Test form',
        'texts': {
            'submit': 'Submit',
            'title': 'Thank you for your responses!',
            'subtitle': 'Your responses have been received.',
        },
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to create the form: {response.status_code} {response.text}')
        return None

    result = response.json()
    survey_id = result['id']
    return survey_id

def add_question(survey_id: str, payload: dict) -> int:
    """
    Adds a question to the form.
    Returns the ID of the created question.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/questions/'
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to add the question: {response.status_code} {response.text}')
        return None

    result = response.json()
    question_id = result['id']
    return question_id

def move_question(survey_id: str, question_id: int, payload: dict) -> None:
    """
    Moves a question.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/questions/{question_id}/move/'
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to move question {question_id}: {response.status_code} {response.text}')

def main():
    survey_id = create_survey()
    print(f'Form {survey_id} created')

    questions = [
        # Page 1
        # Text question
        {
            'type': 'string',
            'label': 'What is your name?',
            'placeholder': 'Enter your name',
        },
        # Boolean question
        {
            'type': 'boolean',
            'label': 'Do you agree to the terms of use?',
        },
        # Numeric question
        {
            'type': 'integer',
            'label': 'How many years have you been using our product?',
            'placeholder': 'Enter a number',
        },
        # Choice question
        {
            'type': 'enum',
            'label': 'How do you rate our product?',
            'widget': 'radio',
            'items': [
                {'label': 'Excellent'},
                {'label': 'Good'},
                {'label': 'Satisfactory'},
                {'label': 'Poor'},
            ],
        },
        # Page 2
        # Date selection
        {
            'type': 'date',
            'label': 'Enter your date of birth',
        },
        # Date range selection
        {
            'type': 'daterange',
            'label': 'Enter your vacation period',
        },
        # File upload
        {
            'type': 'file',
            'label': 'Attach your resume',
        },
        # Text
        {
            'type': 'comment',
            'label': 'Section: Additional information',
            'header': True,
        },
        # Page 3
        # Rating scale
        {
            'type': 'matrix',
            'label': 'Rate the product by criteria',
            'rows': [
                {'label': 'Usability'},
                {'label': 'Reliability'},
            ],
            'columns': [
                {'label': 'Poor'},
                {'label': 'Average'},
                {'label': 'Excellent'},
            ],
        },
        # City selection from a list
        {
            'type': 'suggest',
            'label': 'Select a city',
            'data_source': {'name': 'city'},  # Or "country" for countries
        },
        # Series of questions
        {
            'type': 'series',
            'label': 'Block of questions about work',
        },
        # Child questions for the series
        {
            'type': 'string',
            'label': 'Your job title',
            'placeholder': 'For example: developer',
        },
        {
            'type': 'string',
            'label': 'Company name',
            'placeholder': 'Enter the name',
        },
    ]

    ids = []
    for question in questions:
        question_id = add_question(survey_id, question)
        print(f'Question {question["type"]} {question_id} added')
        ids.append(question_id)

    # Page 2: questions 5–8
    move_question(survey_id, ids[4], {'create_page': True, 'page': 2})
    move_question(survey_id, ids[5], {'page': 2, 'position': 2})
    move_question(survey_id, ids[6], {'page': 2, 'position': 3})
    move_question(survey_id, ids[7], {'page': 2, 'position': 4})

    # Page 3: questions 9–11
    move_question(survey_id, ids[8],  {'create_page': True, 'page': 3})
    move_question(survey_id, ids[9],  {'page': 3, 'position': 2})
    move_question(survey_id, ids[10], {'page': 3, 'position': 3})

    print('Questions distributed across pages')

    # Questions 12 and 13 are moved inside the series
    series_id = ids[10]
    move_question(survey_id, ids[11], {'question': series_id})
    move_question(survey_id, ids[12], {'question': series_id, "position": 2})

    print(f'Questions added to series {series_id}')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_8.py
Form 69c28ee0b5d30f000f54025a created
Question string 73016 added
Question boolean 73017 added
Question integer 73018 added
Question enum 73019 added
Question date 73020 added
Question daterange 73021 added
Question file 73022 added
Question comment 73023 added
Question matrix 73024 added
Question suggest 73025 added
Question series 73026 added
Question string 73027 added
Question string 73028 added
Questions distributed across pages
Questions added to series 73026
```

# 9\. Generating and downloading a keyset (personal links)

In the example below, the script creates a keyset (personal links) for a form and saves them to an `xlsx` file.

Text of the api\_example\_9.py script

```
import os
import requests
import sys

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def create_keyset(survey_id: str, total: int) -> int:
    """
    Creates a keyset for the form.
    Returns the ID of the created keyset.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/keysets/'
    payload = {
        'name': 'Test keyset',
        'total': total,
        'is_enabled': True,
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to create the keyset: {response.status_code} {response.text}')
        return None

    result = response.json()
    keyset_id = result['id']
    return keyset_id

def download_keyset(survey_id: str, keyset_id: int) -> bytes:
    """
    Downloads the keyset in XLSX format.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/keysets/{keyset_id}/download/'
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to download the keys: {response.status_code} {response.text}')
        return None

    return response.content

def main():
    if len(sys.argv) < 3:
        return

    survey_id = sys.argv[1]
    total = int(sys.argv[2])
    keyset_id = create_keyset(survey_id, total=total)
    print(f'Keyset {keyset_id} created')

    content = download_keyset(survey_id, keyset_id)
    filename = f'keys_{keyset_id}.xlsx'
    with open(filename, 'wb') as f:
        f.write(content)

    print(f'Keys saved to file {filename}')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_9.py 28ee0b5d30f000f54025a 10
Keyset 4734 created
Keys saved to file keys_4734.xlsx
```

# 10\. Uploading an image and attaching it to a question

In the example below, the script uploads a specified image, creates a question, and attaches the image to it.

Text of the api\_example\_10.py script

```
import os
import requests
import sys

FORMS_PUBLIC_API = 'https://api.forms.yandex.net/v1'
FORMS_TOKEN = os.environ.get('FORMS_TOKEN')
ORG_ID = os.environ.get('ORG_ID')
HEADERS = {
    'Authorization': f'OAuth {FORMS_TOKEN}',
    'X-Org-Id': ORG_ID,
}

def add_question(survey_id: str) -> int:
    """
    Adds a text question to the form.
    Returns the ID of the created question.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/questions/'
    payload = {
        'type': 'string',
        'label': 'Comment with image',
        'placeholder': 'Enter text',
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to add the question: {response.status_code} {response.text}')
        return None

    result = response.json()
    question_id = result['id']
    return question_id

def upload_image(survey_id: str, image_path: str) -> dict:
    """
    Uploads an image to the form.
    Returns an object with the fields id, links, name.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/images/'
    with open(image_path, 'rb') as f:
        response = requests.post(url, files={'image': f}, headers=HEADERS)
    if response.status_code != 201:
        print(f'Failed to upload the image: {response.status_code} {response.text}')
        return None

    return response.json()

def attach_image(survey_id: str, question_id: int, image: dict) -> bool:
    """
    Attaches the uploaded image to a question.
    """
    url = f'{FORMS_PUBLIC_API}/surveys/{survey_id}/questions/{question_id}/'
    payload = {
        'image': {
            'id': image['id'],
            'links': image['links'],
            'name': image['name'],
        },
    }
    response = requests.patch(url, json=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f'Failed to attach the image: {response.status_code} {response.text}')
        return False
    return True

def main():
    if len(sys.argv) < 3:
        return

    survey_id = sys.argv[1]
    image_path = sys.argv[2]
    question_id = add_question(survey_id)
    if question_id:
        print(f'Question {question_id} added')

    image = upload_image(survey_id, image_path)
    if image:
        print(f'Image {image["id"]} uploaded')

    if attach_image(survey_id, question_id, image):
        print(f'Image attached to question {question_id}')

if __name__ == '__main__':
    main()
```

Example of running the script:

```
$ FORMS_TOKEN=$(cat .forms-token) ORG_ID=$(cat .org-id) python api_example_10.py 69c28ee0b5d30f000f54025a image.png
Question 73038 added
Image 7639 uploaded
Image attached to question 73038
```