import firebase_admin
from firebase_admin import credentials

def init_firebase():
    key = {
        'type': 'service_account',
        'project_id': 'colegios-tutor',
        'private_key_id': 'b857638e88fc1e047472a90e99d4fb18ea3a8234',
        'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCqMPJ8DJ7xUazI\nW1mysCdaY5IVeKjyJDPV1L1fwX4SFAPdrJSU7VTdrz5tAmNzN6QmE05tvcCO3v6/\niSH9SRKWrUaH0YoiLB9zp03izDwKjyD0g5Tup93JLFV5akNdmaObcU96KXczQl24\nvtBEEKx6Y94zB9uFASsVs4KgMQ8af9LatLFaTmNKYGhAAwGt0LjFbsUj9gTyaHIo\nr5f8KpG9W482LOHatmoBoXvTCUCwkaqpFJcrKYRdRKdKPzzHY7rj01CsXnZRGQSd\nCjWITR1ZdLDAFcxg7sw6+8WcCgcSkI5LsvK+0Atb6GzXwj/CJzzoq/iF9+0PtO9p\n9UgU2m+rAgMBAAECggEATsNcVWCZ5mDAL/Fm77VqYQCXyOwQdA+hFaLhCYHI0KEG\nsP5/vPShQ/8oStbCI75qb1yb/VnF1dkJ2KakXk4FFkqWy6CD5xC4dZPGDeIrH0/i\nFocW0+RIViP4Yrp09sp11yh3ebfa/JQIP8m/JOD6kaHKYZ+PTlyeDesH1w8dSEuC\nfWJjiVqYu7F/WrZiAuhEfm/wy3YCKcNQwPAE9fNXVk/CeoaDWpX8BXRlvUW9r73Y\nML7CDfA/kuaWYPLiijpN4rLhva9kr6XGuXvSxYO17fDy4Go6dHVTawNW9xKqAxpx\nZcR0HipZEDCSPApMWQdmso8ef3EwVUN3nIHkSEzzgQKBgQDYOV5gQNSPIDplyEj2\naceyffX4IJVOrSVBu0tp9G64H7lAJMfKJWMmII0Zp5xY4mbFAXqz3Zrll56C2TI/\nJbjq0Ulkoc1oMRlJgI2H3oj1mzqP1bmmmVBUR/CjjmoPnn7P4SEVw9SAjOfAftvR\nzyzN6JOr4IPGygN4Cg1HZWoACwKBgQDJf8DlP8cXnlrsMyzhEb6VoGFcEVCPYPOf\n8N7nxZdxnXBm6xm4VqDpmr/8QxArkegMiyG9P1LqkygZIqDBFkHLlyqGIEQXd+Cd\nuk16HT6y7f4pEwilnRSv49xwv7SWBLOgzibjsZ0qzUz9ESJ0eIrrkL/igshng227\ngafQhbLy4QKBgQCd0FlilU7O2+3jhehC+XfIfgj9vgJbtyIfNK1ZOw9okbbq6y1r\nDBiupkl19RC3Cx+JIIhHKTI56ozF4fK7hjPOJ0yTB0ldh6B2Nj6WcUSzRkXa31ou\nD25C5XLsXTBqD/tsjFtSgGjkHnOz2qNkIfsImnzVkPt9JsqbXXLNrmZMewKBgQDB\nSW0t+5ntjBfHz+dTFwRs32XFPU672tKYMCSCy8XUVKQH9am8bEz7CVj0kRgn01R3\nA9efg+jz36ltQwxVbBY9R4qhEr5+jJ3Ib3f2lasZVLajjACVbTL07mz9Msf1yBjP\nPjGL5UrQThN2BkO42hDYmweWLsIymZ5faaYinr3jwQKBgQDNBJzjz9NWBgTBRiFY\nC4Zcr6T9eZg6/l66VxjpSKnruMcCmXt/2o4zDgkB4wuYIoslJ8CsUO/+wf6DzZS+\nyY/1Krzx23EzvCNSdYXpdpm/RadBmNPzCReb9NXZzMnd2HZiP1POdch3CdxjRXe/\nyZkihh91j/FUKR5+jNee4vvtvg==\n-----END PRIVATE KEY-----\n',
        'client_email': 'firebase-adminsdk-emwby@colegios-tutor.iam.gserviceaccount.com',
        'client_id': '103946865474620873215',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-emwby%40colegios-tutor.iam.gserviceaccount.com',
        'universe_domain': 'googleapis.com'
    }


    certificate = credentials.Certificate(key)
    firebase_admin.initialize_app(certificate, {
        'databaseURL': 'https://colegios-tutor-default-rtdb.firebaseio.com/test/'
    })

init_firebase()