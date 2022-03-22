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
        secret = self.__api_key
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(secret),data=details)
        #check for errors in result
        # print(f'sign_in: {r.json()}')
        # EXAMPLE SUCCESS
        # {'kind': 'identitytoolkit#VerifyPasswordResponse', 'localId': '<user_id>', 'email': 'email@email.com', 'displayName': '', 'idToken': '<long_token_string>', 'registered': True, 'refreshToken': '<refresh_token_string>', 'expiresIn': '3600'}
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #if the registration succeeded
        if 'idToken' in r.json().keys() :
                return {'status':'success','idToken':r.json()['idToken'],'email':r.json()['email'], 'localId':r.json()['localId']}

    def reset_password(self, email):
        details={
            'email':email,
            'requestType': 'PASSWORD_RESET'
        }
        # send post request
        secret = self.__api_key
        r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={}'.format(secret),data=details)
        #check for errors in result
        # Possible ERROR:
        # {'error': {'code': 400, 'message': 'EMAIL_NOT_FOUND', 'errors': [{'message': 'EMAIL_NOT_FOUND', 'domain': 'global', 'reason': 'invalid'}]}}
        # Possible SUCCESS:
        # {'kind': 'identitytoolkit#GetOobConfirmationCodeResponse', 'email': 'name@email.com'}
        if 'error' in r.json().keys():
            return {'status':'error','message':r.json()['error']['message']}
        #if the registration succeeded
        else :
            return {'status':'success','email':r.json()['email']}