import streamlit as st
import requests

def new_user(email,password):
    details={
        'email':email,
        'password':password,
        'returnSecureToken': True
    }
    # send post request
    secret = st.secrets['firebase_api_key']
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(secret),data=details)
    #check for errors in result
    if 'error' in r.json().keys():
        return {'status':'error','message':r.json()['error']['message']}
    #if the registration succeeded
    if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}

def sign_in(email, password):
    details={
        'email':email,
        'password':password,
        'returnSecureToken': True
    }
    # send post request
    secret = st.secrets['firebase_api_key']
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={}'.format(secret),data=details)
    #check for errors in result
    if 'error' in r.json().keys():
        return {'status':'error','message':r.json()['error']['message']}
    #if the registration succeeded
    if 'idToken' in r.json().keys() :
            return {'status':'success','idToken':r.json()['idToken']}


st.sidebar.title("Say Next App")
st.sidebar.subheader("Sign in to access your personalized language simulation")
st.sidebar.markdown("-----")

# AUTHENTICATION
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password',type = 'password')

# Sign up Block
if choice == 'Sign up':
    # handle = st.sidebar.text_input(
    #     'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = new_user(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in?
        # user = sign_in(email, password)
        # db.child(user['localId']).child("Handle").set(handle)
        # db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome')
        st.info('Login via login drop down selection')

# Login Block**
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = sign_in(email,password)
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        bio = st.radio('Jump to',['Home','Workplace Feeds', 'Settings'])
 