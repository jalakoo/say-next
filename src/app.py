import streamlit as st
from firebase_utils import FirebaseConnection
from neo4j_utils import Neo4jConnection
import constants

firebase = FirebaseConnection(st.secrets['firebase_api_key'])
iso_languages = constants.ISO_LANGUAGES
# st.session_state['current_phrase'] = ''
data = Neo4jConnection(st.secrets['neo4j_uri'], st.secrets['neo4j_user'], st.secrets['neo4j_password'])

CURRENT = 'current_user'
USER = 'user_token'

# HEADER
def header():
    st.title('SayNext')
    st.text("""
        This app allows you to simulate possible foreign language 
        conversations by traversing a tree of phrases.
        """)
    with st.expander('Instructions'):
        st.text("""
        After selecting an initial phrase you will be presented 
        with possible phrases that follow it.\n
        These next phrases may be statements that can contextually
        accompanies, follows, or answers the selected phrase.\n
        After selecting a phrase, new follow up phrases will be
        presented.\n
        You may add new phrases. When doing so, selecting the 
        'follows <phrase>' will add that as a new next phrase
        option to <phrase>.
        """)
    st.markdown('--------\n')

# DASHBOARD
def dashboard():
    st.header('1. Select languages')

    lang = data.read_languages()
    print(f'languages: {lang}')

    col1, col2 = st.columns(2)
    with col1:
        user_language_code_key = st.selectbox('Your language', iso_languages.keys())
        user_language_code = iso_languages[user_language_code_key]
    with col2:
        language_code_key = st.selectbox('Learning', iso_languages.keys())
        language_code = iso_languages[language_code_key]

    print(f'user_language_code selected: {user_language_code}')
    print(f'language_code selected: {language_code}')

    st.markdown('--------\n')
    if CURRENT not in st.session_state:
        st.session_state[CURRENT] = ''
    current_phrase = st.session_state[CURRENT]
    all_phrases = data.get_all_phrases(user_language_code, language_code)
    st.selectbox('Select a new phrase', all_phrases)
    phrases = data.get_phrases(current_phrase, user_language_code, language_code)
    print(f'current_phrase: {current_phrase}')
    print(f'phrases: {phrases}')
    st.text(f'Current phrase: {current_phrase}')
    if current_phrase != None and current_phrase != "" and len(phrases) == 0:
        # st.selectbox('Select a Phrase', [current_phrase])
        st.header('2. Add follow-up phrases')
    elif phrases != None and len(phrases) != 0:
        # current_phrase = st.selectbox('Select a Phrase', phrases)
        # st.session_state['current_phrase'] = current_phrase
        st.header('2. Next Phrases')
        for phrase in phrases:
            st.text(phrase)
    else:
        st.header('2. New language')
        st.text("""
        No phrases yet for your selected learning language. 
        Start by adding new phrase below:
        """)
        
    st.markdown('--------\n')

    with st.form(key="new_phrase", clear_on_submit=True):
        new_phrase = st.text_input(f'Add New {language_code_key} phrase')
        equal_phrase = st.text_input(f'Equals the {user_language_code_key} phrase')
        prior_phrase = current_phrase
        if CURRENT in locals() and current_phrase != '':
            should_link = st.checkbox(f'Follows "{current_phrase}"')
            if should_link == False:
                prior_phrase = None
        add_button = st.form_submit_button(label='Add')
        if add_button:
            # Commit new phrase
            try:
                data.add_phrase(equal_phrase, user_language_code, new_phrase, language_code, prior_phrase)
                st.session_state[CURRENT] = new_phrase
            except Exception as e:
                print(f'new word submission form ERROR: {e}')




# SIDEBAR
st.sidebar.title("SayNext App")
st.sidebar.subheader("Sign in to access your personalized language learning simulation")
st.sidebar.markdown("-----")

# AUTHENTICATION
choice = st.sidebar.selectbox('login / Signup / Reset Password', ['Login', 'Sign up', 'Reset Password'])

# Obtain User Input for email and password

# Sign up Block
if choice == 'Sign up':
    with st.sidebar.form(key='sign_up_form', clear_on_submit=True):
        email = st.text_input('Email address')
        password = st.text_input('New password',type = 'password')
        submit = st.form_submit_button('Create my account')

        if submit:
            user = firebase.new_user(email, password)
            if user['status'] == 'success':
                st.success('Your account was successfully created! Please login now')
                st.balloons()
            else:
                message = user['message']
                st.error(f'There was a problem creating your account: {message}')
# Login Block**
elif choice == 'Login':
    if USER not in st.session_state:
        with st.sidebar.form(key='login_form', clear_on_submit=True):
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            login = st.form_submit_button('Login')
            if login:
                user = firebase.sign_in(email,password)
                if user['status'] == 'success':

                    st.session_state[USER] = user
                    st.experimental_rerun()
                else:
                    message = user['message']
                    st.error(f'Problem logging in: {message}')
    else:
        with st.sidebar.form(key='logout_form', clear_on_submit=True):
            email = st.session_state[USER]['email']
            st.text(f'Logged in as:\n{email}')
            logout = st.form_submit_button('Logout')
            if logout:
                del st.session_state[USER]
                st.experimental_rerun()
elif choice == 'Reset Password':
    with st.sidebar.form(key="reset_form", clear_on_submit=True):
        email = st.text_input('Email')
        submit = st.form_submit_button('Reset password')
        if submit:
            result = firebase.reset_password(email)  
            if result['status'] == 'error':
                message = result['message']
                st.error(f'Reset password error:{message}')
            elif result['status'] == 'success':
                st.success('Reset request successful, please check your email')
            

if USER not in st.session_state:
    header()
    original_title = '<p style="font-family:Courier; color:red; font-size: 20px;">Please login</p>'
    st.markdown(original_title, unsafe_allow_html=True)
else:
    header()
    dashboard()
 
