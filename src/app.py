import streamlit as st
from firebase_utils import FirebaseConnection
from constants import *
import numpy as np
from neo4j_repo import Neo4jRepository

firebase = FirebaseConnection(st.secrets['firebase_api_key'])
n4j = Neo4jRepository(st.secrets['neo4j_uri'], st.secrets['neo4j_user'], st.secrets['neo4j_password']) 

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
        accompany, follow, or answers the selected phrase.\n
        After selecting another phrase, new follow up phrases will
        be presented.\n
        You may add new phrases. When doing so, selecting the 
        'follows <phrase>' will add that as a new next phrase
        option to <phrase>.
        """)
    st.markdown('--------\n')

# DASHBOARD
def selectbox_with_default(text, values, default=DEFAULT, sidebar=False):
    func = st.sidebar.selectbox if sidebar else st.selectbox
    return func(text, np.insert(np.array(values, object), 0, default))

def update_state(key, value):
    """
    Updates session state key-value. Returns True if
    value was differnt from prior, False if the
    value arg equals the existing value.
    """
    if key not in st.session_state:
        st.session_state[key] = value    
        return True
    prior = st.session_state[key]
    if value != prior:
        st.session_state[key] = value
        return True
    return False


def dashboard():
    # Step 1. Select user language preferences
    st.header('1. Select languages')
    col1, col2 = st.columns(2)
    # Successful login stores the User object in state
    uid = st.session_state[USER][USER_ID]
    with col1:
        user_language_code_key = selectbox_with_default('Your language', [*ISO_LANGUAGES.keys()])
        if user_language_code_key == DEFAULT:
            # No option selected
            st.stop()
        else:
            # Convert English selection to ISO code
            user_language_code = ISO_LANGUAGES[user_language_code_key]
            is_new_user_language = update_state(USER_LANGUAGE_CODE, user_language_code_key)
            if is_new_user_language == True: 
                # User selection has changed
                n4j.set_user_language(uid, user_language_code, 'SPEAKS')
    with col2:
        language_code_key = selectbox_with_default('Learning', [*ISO_LANGUAGES.keys()])
        if language_code_key == DEFAULT:
            # No option selected
            st.stop()
        else:
            language_code = ISO_LANGUAGES[language_code_key]
            if update_state(NEW_LANGUAGE_CODE, language_code_key) == True: 
                n4j.set_user_language(uid, language_code, 'LEARNING')

    st.markdown('--------\n')
    
    # Step 2. Select a starting phrase
    if CURRENT not in st.session_state:
        st.session_state[CURRENT] = ''
    current_phrase = st.session_state[CURRENT]
    all_phrases = n4j.conn.get_all_phrases(language_code)
    print(all_phrases)
    if len(all_phrases) == 0:
        # No phrases in DB yet
        st.header('2. No phrases to select')
        # st.caption(f'Be the first to add some new phrases in {language_code_key}!')
        custom_caption = f'<p style="font-family:Courier; color:green; font-size: 16px;">Be the first to add a new phrase in {language_code_key}!</p>'
        st.markdown(custom_caption, unsafe_allow_html=True)
    else:
        st.header('2. Select a Phrase')
        new_phrase = selectbox_with_default('', all_phrases, current_phrase)
        if new_phrase == DEFAULT:
            add_phrase_block(user_language_code_key, user_language_code, language_code_key, language_code, current_phrase)
            st.stop()
        if new_phrase != current_phrase:
            st.session_state[CURRENT] = new_phrase
            current_phrase = new_phrase

        st.markdown('--------\n')

        # Step 3. Selecting things to say next
        phrases = n4j.conn.get_phrases(current_phrase, user_language_code, language_code)
        if current_phrase != None and current_phrase != "" and len(phrases) == 0:
            st.header('3. Add phrases you can say next')
        elif phrases != None and len(phrases) != 0:
            st.header('3. Phrases you can say next')
            for phrase in phrases:
                with st.expander(phrase):
                    translation = n4j.conn.get_translation(phrase, user_language_code)
                    txt = ', '.join(translation)
                    st.markdown(f'*{txt}*')
        else:
            st.header('3. New language')
            st.text("""
            No phrases yet for your selected learning language. 
            Start by adding a new phrase below:
            """)
        
    add_phrase_block(user_language_code_key, user_language_code, language_code_key, language_code, current_phrase)

def add_phrase_block(user_language_key, user_language, new_language_key, new_language, current_phrase):
    st.markdown('--------\n')
    st.header('+ Add new phrase')
    with st.form(key="new_phrase", clear_on_submit=True):
        if CURRENT in st.session_state and current_phrase != '':
            should_link = st.checkbox(f'Follows "{current_phrase}"')
            if should_link == False:
                prior_phrase = None
        new_phrase = st.text_input(f'Add New {new_language_key} phrase')
        equal_phrase = st.text_input(f'Equals the {user_language_key} phrase')
        prior_phrase = current_phrase
        # TODO: Add equals to (for similar phrases)
        # TODO: Add a notes field
        col1, col2 = st.columns(2)
        with col1:
            add_button_1 = st.form_submit_button(label='Add')
            if add_button_1:
                try:
                    n4j.add_phrase(equal_phrase, user_language, new_phrase, new_language, prior_phrase=prior_phrase)
                    st.experimental_rerun()
                except Exception as e:
                    print(f'new phrase submission form ERROR: {e}')
        with col2:
            # Add new phrase then make it the new selection
            add_button = st.form_submit_button(label='Add & Select')
            if add_button:
                try:
                    n4j.add_phrase(equal_phrase, user_language, new_phrase, new_language, prior_phrase=prior_phrase)
                    st.session_state[CURRENT] = new_phrase
                    st.experimental_rerun()
                except Exception as e:
                    print(f'new phrase submission form ERROR: {e}')

# SIDEBAR
def sidebar():
    st.sidebar.subheader("Sign in to access your personalized language learning simulation")
    st.sidebar.markdown("-----")

    # AUTHENTICATION
    choice = st.sidebar.selectbox('Login / Signup / Reset Password', ['Login', 'Sign up', 'Reset Password'])

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
        # No previously logged in
        if USER not in st.session_state:
            with st.sidebar.form(key='login_form', clear_on_submit=True):
                email = st.text_input('Email')
                password = st.text_input('Password', type='password')
                login = st.form_submit_button('Login')
                if login:
                    try: 
                        user = firebase.sign_in(email,password)
                        if user['status'] == 'success':
                            uid = user['localId']
                            result = n4j.create_user(uid)
                            st.session_state[USER] = user
                            # TODO: While we're here lets see
                            # if the user had prior language prefs
                            usr_lang, new_lang = n4j.get_user_preferences(uid)
                            update_state(USER_LANGUAGE_CODE, usr_lang)
                            update_state(NEW_LANGUAGE_CODE, new_lang)
                            st.experimental_rerun()
                        else:
                            message = user['message']
                            st.error(f'Problem logging in: {message}')
                    except Exception as e:
                        st.error(f'Login error: {e}')
        # We're already logged in - Present logout option
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
            

# LAYDOWN UI
sidebar()

if USER not in st.session_state:
    # Logged out state
    header()
    original_title = '<p style="font-family:Courier; color:red; font-size: 20px;">Please login to begin</p>'
    st.markdown(original_title, unsafe_allow_html=True)
else:
    # Logged in - display main UI
    header()
    dashboard()
 
