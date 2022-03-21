import requests

class FirebaseConnection:

    def __init__(self, api_key):
        self.__api_key = api_key

    def new_user(self,email,password):
        details={
            'email':email,
            'password':password,
            'returnSecureToken': True
        }
        # send post request
        # secret = st.secrets['firebase_api_key']
        secret = self.__api_key
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(secret),data=details)
        #check for errors in result
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #if the registration succeeded
        if 'idToken' in r.json().keys() :
                return {'status':'success','idToken':r.json()['idToken']}

    def sign_in(self, email, password):
        details={
            'email':email,
            'password':password,
            'returnSecureToken': True
        }
        # send post request
        # secret = st.secrets['firebase_api_key']
        secret = self.__api_key
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(secret),data=details)
        #check for errors in result
        # print(r.json())
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #if the registration succeeded
        if 'idToken' in r.json().keys() :
                return {'status':'success','idToken':r.json()['idToken']}