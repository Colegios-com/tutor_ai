import firebase_admin
from firebase_admin import credentials

def init_firebase():
    key = {
        'type': 'service_account',
        'project_id': 'colegios-fc58b',
        'private_key_id': 'd297395c398a6e8fb1665236e5240791e5f4d019',
        'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDT4cfkUAHIQxBd\nu3ZNGcUgbf6EhqywyGKC2M9lsfn22+cDHcginy0MmwlKJM8w8JE4ElppPN0vxZcF\n0EQtHiVrfo5HpGbx21gnYC3PTzyF9ozsNSl6a8hVM6rR7SW8k5KbcMxdexNANur9\nf1YFIxyNbidWoOvF2YqNN076G3Ixhj36pnTlSW6dM21VI7vbDtMsZ8g8TepvYr8H\nHOfVEQ5MRiRsaLofsOJ59WQI1WWLrdux4iTZGv2Sis+mQ4Co4QMiCYtiDWOVFfG9\nbiEui05X7n7j9KW84efrj0xJx26P3vjRqDf6M4BFbs9blu3/D/TOuFEBd8VJHiHs\nGz3S8vGBAgMBAAECggEACA/i6OdjxKNLSnW+lkfGaL8msb46G0Pp/laSQFQEUdtO\nL/UrJKjFMGHvJDjAVXlh3S39mLGDLQp/U5j4Gcti2x3mpgfgZDrXYNrXrg1dcoTO\nGegamu43ojOkFUweZSLXBOkcLZZoRhzmK3Jz6yAfOavDqBfZa3QlQc2lSKj7Wwen\nNoVZpS9qiPJX70+CV+3mqCFPNBL9WnP6wOobq+U++aEY7TTjck7bXrwIpYNY9am/\ne2trmFRsoUHjVO9bimTXzRqGuSapl7emlCKGq+yvmVDxKU5GM/1TVGMlHPGECgz/\nx4d8olk/rdBGNc1Bj08gncsRjsmbmH2xFj7FZmt6DQKBgQDkMQlIIU06jt7W0mzN\n5swlQipm1RCKgZwJrHS99LSFPySIOuLHgVU2XxRAgl+tbvwvapGQ+lgQJgzHkEzi\nOW6urIdPBl2eQgA++2C4k+ClGoZrFp+OK0eclSTxqOkgIIhjH753lCWf2CBUbYox\nsmCkqmdm1QNnOs0Ni1+wnC2B1wKBgQDts+3ZP3qbS3W5nyPaZ1n90MiWZ6ovSnpx\n6tcNpP+J4qgj8oJJnrQPuiqasRB7Z5jzgejSLR+Qr5zwso1GaaiDsCmW5zsBEWQ8\nr81nHuPtB46g5me5VX4HrgnWHo/6gOOfdj2BYdtu+zAFnac8bgNUs4ZmGWCDwZmi\nmk4nA2tsZwKBgCGW8kXS2Rpok3bNzMRWV/CYF8PBU0kAISbvYtPfZH9EtyzydhVl\n/VQelM2WI11VO/wC1OChaTsfTrxFinu2dotxzA0e48L69ixPNoKVCfljuSukTeJQ\njp8G+UQ1V/OptknZD2FsxkkMOF4VLcV4+27hwozJiFG2vx5iSLinlK9LAoGBAOkt\nJTiFBeALIRwK2Z/o3KWYxvyMCq1DcWQIjBeNcUOwvWIuBdL0RQxcgminI1T7JlZR\nbLOoohtLujd/4Ahfo3gzOkkW4ZHFnr/NcUAkVFBzpl1+R+fNzsj32BxcdL626xPF\naMZf2WNAMzZ/Fcu427meNkw3vq7hHrYcimfI+fsnAoGAJuF7zh6+VM1Sag/fXqGA\nUneHLOjLi5GAFN5Nwg9nEH0VY0y8xT+BHv83ObXC0oXFbJcLdnCxstANFcxDxa+o\ntq/QrmmQiZ/bTCaZppoJ8j2AbXfUtXzPp0KjRmBMBJISJbFhSexJm9NEou98nrCQ\nMdGcrCUNAhRtBlwzRD6+3pw=\n-----END PRIVATE KEY-----\n',
        'client_email': 'firebase-adminsdk-debq8@colegios-fc58b.iam.gserviceaccount.com',
        'client_id': '113845024169487544707',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-debq8%40colegios-fc58b.iam.gserviceaccount.com',
        'universe_domain': 'googleapis.com'
    }

    certificate = credentials.Certificate(key)
    firebase_admin.initialize_app(certificate, {
        'databaseURL': 'https://colegios-fc58b-default-rtdb.firebaseio.com/'
    })

init_firebase()