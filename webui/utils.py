from time import time
from pymongo import collection
import pyotp
import qrcode
import qrcode.image.svg
import googleapiclient
factory = qrcode.image.svg.SvgPathImage

def generate_mfa(secret = pyotp.random_base32()):
    totp = pyotp.TOTP(secret)
    link = totp.provisioning_uri(name="Shivansh MFA", issuer_name='Shivansh')
    img = qrcode.make(link, image_factory=factory)
    return img.to_string().decode(), secret

def getUserInfo(credentials):
    oauth2_client = googleapiclient.discovery.build('oauth2','v2',credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()
    return {
        "_id": str(hash(user_info['id'])),
        'email': user_info['email']
    }
    
def upsert_mongo(collection: collection.Collection, user_info):
    if not collection.find_one({"_id": user_info['_id']}):
        collection.insert_one(user_info)
        
def add_device_code(collection: collection.Collection, id, code):
    collection.update_one({"_id": id}, {'$set': {f'device_codes.{code}': time()}})

def verify_device_code(collection: collection.Collection, code):
    user_info = collection.find_one({"code": code})
    print(user_info)
    if user_info :
        print(time()-user_info['code_time'] <60)
        if time()-user_info['code_time'] < 60:
            collection.delete_one({"code": code})
            del user_info['code']
            del user_info['code_time']
            return user_info
        else:
            collection.delete_one({"code": code})
            return False
    return False
            
            
def mfa_exists(collection, id):
    user = collection.find_one({"_id": id})
    if 'mfa_secret' not in user:
        return False
    return True
    