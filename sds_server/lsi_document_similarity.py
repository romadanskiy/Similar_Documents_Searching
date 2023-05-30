from models.Document import Document

import nltk
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

from sklearn.feature_extraction.text import CountVectorizer

from numpy import linalg as LA

from sklearn.metrics.pairwise import cosine_similarity


def get_document_similarity_matrix_with_lsi(documents):
    # 1. Предобработка текстов документов
    preprocessed_documents = preprocess_documents(documents)

    # 2. Построение матрицы терминов-документов
    term_document_matrix, index_to_id = get_term_document_matrix(preprocessed_documents)

    # 3. Построение сокращенной матрицы терминов-концептов с помощью SVD
    k = 100
    concept_document_matrix = get_concept_document_matrix(term_document_matrix, k)

    # 4. Построение матрицы косинусного сходства документов
    similarity_matrix = get_cosine_similarity_matrix(concept_document_matrix)

    return similarity_matrix, index_to_id


def preprocess_documents(documents):
    # Загрузка стоп-слов и создание лемматизатора
    nltk.download('stopwords')
    stop_words = stopwords.words('russian')
    morph = MorphAnalyzer()

    def preprocess_text(text):
        # Токенизация и приведение к нижнему регистру
        tokens = nltk.word_tokenize(text.lower())

        lemmatized_tokens = []
        for token in tokens:
            # Удаление неалфавитных символов и стоп-слов
            if token.isalpha() and token not in stop_words:
                # Лемматизация
                lemmatized_tokens.append(morph.parse(token)[0].normal_form)

        return ' '.join(lemmatized_tokens)

    preprocessed_documents = []
    for document in documents:
        preprocessed_text = preprocess_text(document.text)
        preprocessed_documents.append(Document(document.id, preprocessed_text))

    return preprocessed_documents


def get_term_document_matrix(documents):
    # Создание экземпляра CountVectorizer
    vectorizer = CountVectorizer()

    # Получения списка идентификаторов и текстов объектов Document
    texts = [document.text for document in documents]
    ids = [document.id for document in documents]

    # Преобразование текстов документов в матрицу терминов-документов
    term_document_matrix = vectorizer.fit_transform(texts).astype(float)

    # Сопоставление индексов полученной матрицы с id документов
    index_to_id = dict(enumerate(ids))

    return term_document_matrix, index_to_id


def get_concept_document_matrix(A, k):
    # Сингулярное разложение
    U, S, V_T = LA.svd(A, full_matrices=False)

    # Понижение размерности матрицы концептов документов
    V_T_k = V_T[:k, :]

    return V_T_k


def get_cosine_similarity_matrix(matrix):
    similarity_matrix = cosine_similarity(matrix)

    return similarity_matrix
