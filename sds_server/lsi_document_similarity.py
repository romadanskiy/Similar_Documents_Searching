from models.Document import Document
from models.PreprocessedDocument import PreprocessedDocument

from typing import List

import nltk
import stopwordsiso as stopwords
import re
from pymorphy2 import MorphAnalyzer
from translate import Translator

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

import concurrent.futures


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


def preprocess_documents(documents: List[Document]) -> List[PreprocessedDocument]:
    stop_words = stopwords.stopwords("ru") # Загрузка стоп-слов
    morph = MorphAnalyzer() # Инициализация лемматизатора
    translator = Translator(to_lang="ru") # Инициализация переводчика
    regex = r'^[а-я]+(-[а-я]+)?$' # Объявление регулярного выражения

    def preprocess_text(text: str) -> List[str]:
        # Приведение к нижнему регистру и токенизация
        tokens = nltk.word_tokenize(text.lower(), language='russian')

        lemmatized_tokens = []
        for token in tokens:
            # Удаление токенов, не являющихся словами, и стоп-слов
            if re.fullmatch(regex, token) and token not in stop_words:
                # Лемматизация
                lemmatized_tokens.append(morph.parse(token)[0].normal_form)

        return lemmatized_tokens

    def preprocess_document(document: Document) -> PreprocessedDocument:
        text_for_preprocessing = document.text

        if text_for_preprocessing is None:
            return PreprocessedDocument(document.id, [])

        # Перевод иностранного текста на русский язык
        if not document.is_russian:
            text_for_preprocessing = translator.translate(text_for_preprocessing)

        # Предобработка текста, получение токенов (терминов) документа
        document_tokens = preprocess_text(text_for_preprocessing)

        # Возвращение предобработанного документа
        return PreprocessedDocument(document.id, document_tokens)

    # Параллельная предобработка документов
    with concurrent.futures.ThreadPoolExecutor() as executor:
        preprocessed_documents = executor.map(preprocess_document, documents)

    return list(preprocessed_documents)


def get_term_document_matrix(documents: List[PreprocessedDocument]):
    # Инициализация экземпляра TfidfVectorizer
    vectorizer = TfidfVectorizer(tokenizer=lambda d: d, lowercase=False)

    # Получения списка токенов и идентификаторов документов
    tokens = [document.tokens for document in documents]
    ids = [document.id for document in documents]

    # Преобразование коллекции токенов в матрицу терминов-документов
    term_document_matrix = vectorizer.fit_transform(tokens).astype(float).toarray()

    # Сопоставление индексов полученной матрицы с идентификаторами документов
    index_to_id = dict(enumerate(ids))

    return term_document_matrix, index_to_id


def get_concept_document_matrix(term_document_matrix, k):
    n_components = min(k, min(term_document_matrix.shape))
    svd = TruncatedSVD(n_components=n_components)
    svd_matrix = svd.fit_transform(term_document_matrix)

    return svd_matrix


def get_cosine_similarity_matrix(concept_document_matrix):
    similarity_matrix = cosine_similarity(concept_document_matrix)

    return similarity_matrix
