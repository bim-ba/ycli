---
source: https://yandex.ru/support/forms/en/send-to-database
title: "Delivering responses to a database using Cloud Functions |"
word_count: 934
token_estimate: 1857
extracted: "2026-05-22T17:59:59Z"
mode: quality
---

You can send form responses to a PostgreSQL database created in Yandex Cloud and store them there.

# Step 1. Create a database

1.  Go to the [Yandex Cloud management console](https://console.cloud.yandex.com/) and select the folder where you want to create a database.
2.  In the left-hand panel, click and select Managed Service for PostgreSQL.
3.  In the top-right corner, click **Create cluster**.
4.  Configure the cluster:
    1.  Under **Basic parameters**, fill in the **Cluster name** field. The name may contain uppercase and lowercase Latin letters, numbers, underscores, and hyphens.
    2.  Under **Database**, fill in the **DB name** and **Username** fields. The names may contain uppercase and lowercase Latin letters, numbers, underscores, and hyphens.
    3.  Under **Database**, fill in the **Password** field.
    4.  Under **Database**, set the **Locale for sorting (LC\_COLLATE)** and **Charset locale (LC\_CTYPE)** fields to **en\_US.UTF8**. Once you create a database, you cannot change these parameters.
    5.  Under **Additional settings**, enable **Access from the management console** and **Serverless access**.
    6.  Configure other parameters if needed. For more information, see [{#T}](https://yandex.cloud/en/docs/managed-postgresql/operations/cluster-create).
5.  Click **Create cluster**.
6.  Wait until the new cluster's **Availability** field changes to **Alive**.

# Step 2. Create a table

1.  Go to the page of the created cluster.
2.  In the left-hand panel, click **SQL**.
3.  Select the appropriate username and database, enter the password, and click **Connect**.
4.  Select the **public** schema.
5.  Run the following query in the SQL editor:

    ```
    create table answers(
    	id serial primary key,
    	answer jsonb,
    	created timestamp with time zone default now()
    );
    ```

# Step 3. Create a connection to the database

1.  In the [management console](https://console.cloud.yandex.com/), return to the folder with the new cluster.
2.  In the left-hand panel, click and select Cloud Functions.
3.  In the left-hand panel, click .
4.  In the top-right corner, click **Create connection**.
5.  Set up a connection:
    1.  Fill in the **Name** field. The name may only contain lowercase Latin letters, numbers, and hyphens.
    2.  In the **Type** field, select **PostgreSQL**.
    3.  Fill in the **Cluster**, **Database**, **User**, and **Password** fields. Enter the same field values as you set when creating your cluster in step 1.
6.  Tap **Create**.
7.  Go to the connection page and copy the **Entry point** field value.

# Step 4. Create a service account

1.  In the [management console](https://console.cloud.yandex.com/), return to the folder with the new cluster.
2.  In the top-right corner, click → **Create service account**.
3.  In the service account creation window, fill in the following fields:
    1.  **Name**; it may only contain lowercase Latin letters, numbers, and hyphens.
    2.  **Description**; it may contain any characters.
    3.  In the **Roles in folder** field, add the following roles:
        -   `serverless.functions.invoker`
        -   `serverless.mdbProxies.user`
4.  Tap **Create**.

# Step 5. Create a service account key

1.  In the [management console](https://console.cloud.yandex.com/), return to the folder with the new cluster.
2.  Go to the **Service accounts** tab.
3.  Select the account you need.
4.  In the top panel on the account page, click **Create new key** → **Create API key**.
5.  Provide a brief description for the key.
6.  Tap **Create**.
7.  This will open a window with the key ID and the secret key. Store them in a secure place. You will not be able to access them after you close the window.

# Step 6. Create a cloud function

1.  In the [management console](https://console.cloud.yandex.com/), return to the folder with the new cluster.

2.  In the left-hand panel, click and select Cloud Functions.

3.  In the top-right corner, click **Create function**.

4.  On the function creation page, fill in the following fields:

    1.  **Name**; it may only contain lowercase Latin letters, numbers, and hyphens.
    2.  **Description**; it may contain any characters.
5.  Select the Python programming language.

6.  Create a file named `requirements.txt` and add the following line to it:

    ```
    psycopg2
    ```

7.  Create or edit a file named `index.py`:

    ```
    import json
    import psycopg2

    def run_function(connection, answer, **params) -> int:
    	data ={
    		'answer': answer,
    		'params': params,
    	}
    	args = (json.dumps(data), )
    	with connection.cursor() as c:
    		c.execute('insert into answers(answer) values(%s) returning id', args)
    		rs = c.fetchone()

    	connection.commit()
    	return rs[0]

    def get_connection(context):
    	return psycopg2.connect(
    		database="<connection_ID>",
    		user="<username>",
    		password=context.token["access_token"],
    		host="<entry_point>",
    		port=6432,
    		sslmode="require",
    	)

    def handler(event, context):
    	body = json.loads(event.get('body'))
    	params ={
    		name: value
    		for name, value in body.items()
    		if name != 'answer'
    	}
    	connection = get_connection(context)
    	result ={
    		'id': run_function(connection, body.get('answer'), **params),
    	}

    	return{
    		'statusCode': 200,
    		'body': result,
    		'headers':{
    			'Content-Type': 'application/json',
    		}
    	}
    ```

    Substitute the following values in this function:

    -   `<connection_ID>`: Value of the **ID** field of the database connection you created in step 3. You can copy it on the connection page.
    -   `<username>`: Database user name that you specified in the cluster settings in step 1. You can find it in the **Users** tab on the cluster page.
    -   `<entry_point>`: Value of the **Entry point** field of the database connection you created in step 3. You can copy it on the connection page.
8.  Click **Save changes**.

9.  On the function page, copy the value from the **ID** field.

# Step 7. Set up integration

1.  Go to the form whose responses you want to deliver to the database and select the **Integrations** tab.
2.  Select a group of actions to set up issue creation in and click Cloud Functions at the bottom of the group.
3.  In the **Function code** field, paste the function ID that you copied in the previous step.
4.  Under **Parameters**, you can optionally select additional parameters to be transferred to the function.
5.  Click **Save**.

From now on, all responses from this form will be additionally saved to your database in the **answers** table.