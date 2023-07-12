import logging
import tempfile
import hashlib
import json
from flask import Flask, session, current_app, render_template, redirect, url_for, request, g
from flask_socketio import SocketIO, emit, join_room
from flask_session import Session
from pathlib import Path
import app_config
from ms_identity_web import IdentityWebPython
from ms_identity_web.adapters import FlaskContextAdapter
from ms_identity_web.errors import NotAuthenticatedError
from ms_identity_web.configuration import AADConfig
from threading import Thread
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import AzureSearch
from langchain.chains import RetrievalQA
from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.indexes.models import (  
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SearchIndex,  
    SearchField,  
    VectorSearch,  
    VectorSearchAlgorithmConfiguration,  
)

def ensure_index_created():
    service_endpoint = app_config.SEARCH_ENDPOINT
    credential = AzureKeyCredential(app_config.SEARCH_ADMIN_KEY)
    index_name = app_config.SEARCH_INDEX_NAME
    index_client = SearchIndexClient(service_endpoint, credential)

    vector_search = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(
                name="config",
                kind="hnsw")
        ])
    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, facetable=False),
        SearchField(name="document_title", type=SearchFieldDataType.String, filterable=True, searchable=True, facetable=False),
        SearchField(name="page", type=SearchFieldDataType.Int32, filterable=True, sortable=True, facetable=False),
        SearchField(name="chunk", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True, facetable=False),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), searchable=True, dimensions=1536, vector_search_configuration="config"),
        SearchField(name="oid", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True, facetable=False),
        SearchField(name="metadata", type=SearchFieldDataType.String, facetable=False) # required to be here for langchain compat
    ]
    index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_search)
    index_client.create_or_update_index(index)
    return SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)

def create_user_filter(oid):
    return f"oid/any(g:search.in(g, '{oid}'))"

def get_user_documents_count(search_client, oid):
    result = search_client.search(search_text="*", top=0, include_total_count=True, filter=create_user_filter(oid))
    return result.get_count()

def reset_user_documents(search_client, oid):
    result = search_client.search(search_text="*", top=100000, select='id', filter=create_user_filter(oid)).by_page()
    for page in result:
        search_client.delete_documents(list(page))

def create_app(secure_client_credential=None):
    app = Flask(__name__, root_path=Path(__file__).parent) #initialize Flask app
    socketio = SocketIO(app)
    app.config.from_object(app_config) # load Flask configuration file (e.g., session configs)
    Session(app) # init the serverside session for the app: this is requireddue to large cookie size
    # tell flask to render the 401 template on not-authenticated error. it is not strictly required:
    app.register_error_handler(NotAuthenticatedError, lambda err: (render_template('auth/401.html'), err.code))
    # comment out the previous line and uncomment the following line in order to use (experimental) <redirect to page after login>
    # app.register_error_handler(NotAuthenticatedError, lambda err: (redirect(url_for('auth.sign_in', post_sign_in_url=request.url_rule))))
    # other exceptions - uncomment to get details printed to screen:
    # app.register_error_handler(Exception, lambda err: (f"Error {err.code}: {err.description}"))
    aad_configuration = AADConfig.parse_json('aad.b2c.config.json') # parse the aad configs
    app.logger.level=logging.INFO # can set to DEBUG for verbose logs
    if app.config.get('ENV') == 'production':
        # The following is required to run on Azure App Service or any other host with reverse proxy:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
        # Use client credential from outside the config file, if available.
        if secure_client_credential: aad_configuration.client.client_credential = secure_client_credential

    AADConfig.sanity_check_configs(aad_configuration)
    adapter = FlaskContextAdapter(app) # ms identity web for python: instantiate the flask adapter
    ms_identity_web = IdentityWebPython(aad_configuration, adapter) # then instantiate ms identity web for python
    search_client = ensure_index_created()

    embeddings = OpenAIEmbeddings(
        openai_api_key=app_config.OPENAI_API_KEY,
        openai_api_base=app_config.OPENAI_API_BASE,
        openai_api_type=app_config.OPENAI_API_TYPE,
        openai_api_version=app_config.OPENAI_API_VERSION,
        model=app_config.OPENAI_EMB_DEPLOYMENT_NAME)
    splitter = CharacterTextSplitter()
    vectorstore = AzureSearch(
        azure_search_endpoint=app_config.SEARCH_ENDPOINT,
        azure_search_key=app_config.SEARCH_ADMIN_KEY,
        embedding_function=embeddings.embed_query,
        index_name=app_config.SEARCH_INDEX_NAME)
    llm = AzureChatOpenAI(
        openai_api_key=app_config.OPENAI_API_KEY,
        openai_api_base=app_config.OPENAI_API_BASE,
        openai_api_type=app_config.OPENAI_API_TYPE,
        openai_api_version=app_config.OPENAI_API_VERSION,
        deployment_name=app_config.OPENAI_CHAT_DEPLOYMENT_NAME,
        temperature=0)
    

    @app.route('/')
    @app.route('/sign_in_status')
    def index():
        if g.identity_context_data.authenticated:
            oid = g.identity_context_data._id_token_claims['oid']
            g.user_documents_count = get_user_documents_count(search_client, oid)
        return render_template('auth/status.html')

    def index_pdf(oid, temp_file_name, pdf_name):
        loader = PyPDFLoader(temp_file_name)
        pages = loader.load_and_split()
        socketio.emit('server_update', {'state': 'split_pages', 'file': pdf_name, 'message': f'Indexing {pdf_name}, total pages {len(pages)}'}, namespace='/updates', room=oid)
        for page_num, page in enumerate(pages):
            split_text = splitter.split_text(page.page_content)
            text_embeddings = embeddings.embed_documents(split_text)
            documents = [
                {
                    'id': hashlib.sha512(f'{pdf_name}_{page_num}_{i}'.encode()).hexdigest(),
                    'document_title': pdf_name,
                    'page': page_num,
                    'chunk': i,
                    'content': split_text[i],
                    'content_vector': text_embeddings[i],
                    'oid': [oid],
                    'metadata': json.dumps({'page': page_num, 'chunk': i, 'document_title': pdf_name})
                }
                for i in range(len(split_text))
            ]
            search_client.upload_documents(documents)
            socketio.emit('server_update', {'state': 'indexed_page', 'file': pdf_name, 'message': f'Indexing {pdf_name}, page {page_num + 1} of {len(pages)}'}, namespace='/updates', room=oid)

    @app.route('/upload', methods=['POST'])
    @ms_identity_web.login_required # <-- developer only needs to hook up login-required endpoint like this
    def upload():
        file = request.files['pdf_file']
        filename = file.filename  # Get the original file name
        oid = g.identity_context_data._id_token_claims['oid']
        socketio.emit('server_update', {'state': 'start_indexing', 'file': filename}, namespace='/updates', room=oid)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file)
            temp_file_name = temp_file.name
        # Process the uploaded file here
        # For example, save it to a folder or perform any required operations
        thread = Thread(target=index_pdf, args=(oid, temp_file_name, filename))
        thread.start()
        return ''

    @app.route('/token_details')
    @ms_identity_web.login_required # <-- developer only needs to hook up login-required endpoint like this
    def token_details():
        current_app.logger.info("token_details: user is authenticated, will display token details")
        return render_template('auth/token.html')

    @socketio.on('connect', namespace='/updates')
    def handle_connect():
        if session['identity_context_data']['_authenticated']:
            oid = session['identity_context_data']['_id_token_claims']['oid']
            join_room(oid)

    @app.route('/reset', methods=['POST'])
    @ms_identity_web.login_required # <-- developer only needs to hook up login-required endpoint like this
    def reset():
        # Reset index logic goes here
        # Add the appropriate code to handle the reset operation
        oid = session['identity_context_data']['_id_token_claims']['oid']
        reset_user_documents(search_client, oid)

        return 'Index reset successfully'

    @socketio.on('ask_question', namespace='/updates')
    def handle_ask_question(data):
        if session['identity_context_data']['_authenticated']:
            oid = session['identity_context_data']['_id_token_claims']['oid']
            question = data['question']
            # Process the question logic and get the answer
            # Replace this with the actual code to handle the question and generate the answer
            qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever(search_kwargs={'filters': create_user_filter(oid)}), return_source_documents=True)
            result = qa_chain({"query": question})
            sources = [{'document_title': r.metadata['document_title'], 'page': r.metadata['page']} for r in result['source_documents']]
            # Emit the answer back to the client
            emit('answer_received', {'answer': result['result'], 'sources': sources})

    return app, socketio

if __name__ == '__main__':
    app, socketio=create_app() # this is for running flask's dev server for local testing purposes ONLY
    socketio.run(app)

app, socktio=create_app()