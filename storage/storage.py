from firebase_admin import db, storage


def save_data(url, payload):
    ref = db.reference(url)
    ref.set(payload)


def get_data(url, order_by=None, limit=None):
    ref = db.reference(url)
    if order_by:
        ref = ref.order_by_child(order_by)
    if limit:
        ref = ref.limit_to_last(limit)
    
    return ref.get()


def update_data(url, payload):
    ref = db.reference(url)
    ref.update(payload)


def delete_data(url):
    ref = db.reference(url)
    ref.delete()


def upload_file(data, file_path):
    bucket = storage.bucket()
    blob = bucket.blob(file_path)
    blob.upload_from_string(data)
    return f'{file_path}'


def download_file(file_path):
    bucket = storage.bucket()
    blob = bucket.blob(file_path)
    return blob.download_as_bytes()
