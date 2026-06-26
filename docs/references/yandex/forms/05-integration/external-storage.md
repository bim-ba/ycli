---
source: https://yandex.ru/support/forms/en/storage-for-attached-files
title: "Saving files from responses to the storage |"
word_count: 652
token_estimate: 1129
extracted: "2026-05-22T18:00:51Z"
mode: quality
---

If your form allows users to attach [files](https://yandex.ru/support/forms/en/blocks-ref/file), you can set up import to an external storage and store these files, for example, in Object Storage [buckets](https://yandex.cloud/en/docs/storage/concepts/bucket) or on Yandex Disk. This way, you can:

-   Manage files in your storage and set up automations for them.
-   Choose conditions for file storage and deletion. If you do not use your storage, the files will be stored for a year, after which they will be deleted without the possibility of recovery.
-   Attach multiple files with a total size of more than 20 MB to a single response. The size of each file may not exceed 20 MB.

After you connect an external storage, the attached files from new responses will be saved to it. Although Forms only stores metadata about these files, you'll be able to download them via a link in the form settings, in the **Answers** tab. Files received before you enabled this setting will continue to be stored in Forms for a [limited time](https://yandex.ru/support/forms/en/answers#files).

Maintain enough space in the external storage to download new files. If you run out of space, users will not be able to fill out the form and will be getting the error: Attaching files is temporarily suspended.

# Connect the form to Yandex Disk

To save attached files from responses to Yandex Disk, open the form, navigate to **Settings** → **Advanced**, and enable the option **Save attached files from responses to Yandex Disk**.

This will create the `Yandex.Forms` folder on the form owner's Yandex Disk, where files from new user responses will be saved. Files received before you enabled this setting will continue to be stored in Forms for a [limited time](https://yandex.ru/support/forms/en/answers#files).

# Connect the form to Object Storage

This option is only available to Yandex Forms for Business users.

1.  Make sure you have a Yandex Cloud organization with a [cloud](https://yandex.cloud/en/docs/organization/concepts/manage-services#cloud). To find out the organization, click on **For organization** in the top panel: the linked organization will be highlighted in the list. You can check if there is a cloud in the Yandex Cloud [management console](https://console.cloud.yandex.com/). If there is no cloud, create one by following the [guide](https://yandex.cloud/en/docs/resource-manager/operations/cloud/create).

2.  The cloud must have a [service account](https://yandex.cloud/en/docs/iam/concepts/users/service-accounts). If there is no service account, create one by following the [guide](https://yandex.cloud/en/docs/iam/operations/sa/create).

3.  [Assign](https://yandex.cloud/en/docs/iam/operations/sa/assign-role-for-sa) the `storage.editor` [role](https://yandex.cloud/en/docs/storage/security/index#storage-editor) to the service account for writing and reading files in the buckets.

4.  Create a static access key for the service account by following the [guide](https://yandex.cloud/en/docs/iam/operations/sa/create-access-key). Save the created key: you will need it to configure the form.

5.  In the Yandex Forms interface, open the form you want to connect Object Storage to and, under **Save in custom storage** in the settings, specify the static key you created in the previous step. The added key will be effective for all forms of this organization.

6.  In the Yandex Cloud [management console](https://console.cloud.yandex.com/), go to Object Storage and remember the path to the bucket where you want to save the attached files. If you do not have a bucket, create one by following the [guide](https://yandex.cloud/en/docs/storage/operations/buckets/create).

    The bucket must have encryption disabled. Otherwise, Yandex Forms will not be able to write files to it.

7.  In the Yandex Forms interface, go to the **Advanced** section of the form settings. In the **Save attached files from responses to specified S3** field, specify the `path` to the bucket in the `s3://path` format. When saving the settings, the bucket will be checked for availability. If the bucket is unavailable, you will get an error.

If the bucket is available, files from new user responses will be saved to it. Files received before you specified the bucket, will continue to be stored in Yandex Forms for a [limited time](https://yandex.ru/support/forms/en/answers#files).

To stop saving files to the bucket: in the Yandex Forms interface, go to the form settings, **Settings** → **Advanced**, and delete the contents of the **Save attached files from responses to the specified S3** field.