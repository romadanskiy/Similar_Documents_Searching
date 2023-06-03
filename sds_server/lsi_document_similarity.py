from models import Document
from models.PreprocessedDocument import PreprocessedDocument

from typing import List

import nltk
from nltk.corpus import stopwords

from pymorphy2 import MorphAnalyzer

from translate import Translator

from sklearn.feature_extraction.text import CountVectorizer

from numpy import linalg as LA

from sklearn.metrics.pairwise import cosine_similarity


def get_document_similarity_matrix_with_lsi(documents: List[Document]):
    # 1. Предобработка текстов документов
    preprocessed_documents = preprocess_documents(documents)

    # 2. Построение матрицы терминов-документов
    term_document_matrix, index_to_id = get_term_document_matrix(preprocessed_documents)

    # 3. Построение сокращенной матрицы концептов-документов с помощью SVD
    k = 100
    concept_document_matrix = get_concept_document_matrix(term_document_matrix, k)

    # 4. Построение матрицы косинусного сходства документов
    similarity_matrix = get_cosine_similarity_matrix(concept_document_matrix)

    return similarity_matrix, index_to_id


def preprocess_documents(documents: List[Document]):
    # Загрузка стоп-слов
    nltk.download('stopwords')
    stop_words = stopwords.words('russian')

    # Cоздание лемматизатора
    morph = MorphAnalyzer()

    # Создание переводчика
    translator = Translator(to_lang="ru")

    def preprocess_text(text):
        # Токенизация и приведение к нижнему регистру
        tokens = nltk.word_tokenize(text.lower())

        lemmatized_tokens = []
        for token in tokens:
            # Удаление неалфавитных символов и стоп-слов
            if token.isalpha() and token not in stop_words:
                # Лемматизация
                lemmatized_tokens.append(morph.parse(token)[0].normal_form)

        return lemmatized_tokens

    preprocessed_documents = []
    for document in documents:
        text_for_preprocessing = document.text
        if not document.is_russian:
            text_for_preprocessing = translator.translate(text_for_preprocessing)
        document_tokens = preprocess_text(text_for_preprocessing)
        preprocessed_documents.append(PreprocessedDocument(document.id, document_tokens))

    return preprocessed_documents


def get_term_document_matrix(documents: List[PreprocessedDocument]):
    # Создание экземпляра CountVectorizer
    vectorizer = CountVectorizer(tokenizer=lambda doc: doc, lowercase=False)

    # Получения списка токенов и идентификаторов документов
    tokens = [document.tokens for document in documents]
    ids = [document.id for document in documents]

    # Преобразование коллекции токенов в матрицу терминов-документов
    term_document_matrix = vectorizer.fit_transform(tokens).astype(float)

    # Сопоставление индексов полученной матрицы с идентификаторами документов
    index_to_id = dict(enumerate(ids))

    return term_document_matrix, index_to_id


def get_concept_document_matrix(A, k):
    # Сингулярное разложение
    U, S, V_T = LA.svd(A, full_matrices=False)

    # Понижение размерности матрицы концептов-документов
    V_T_k = V_T[:k, :]

    return V_T_k


def get_cosine_similarity_matrix(matrix):
    similarity_matrix = cosine_similarity(matrix)

    return similarity_matrix
