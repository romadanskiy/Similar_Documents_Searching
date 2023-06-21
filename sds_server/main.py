from flask import Flask, jsonify, make_response

import database.database_utils as database_utils
import pdf_utils
import hash_utils

from models.DocumentLsiSimilarities import DocumentLsiSimilarities
from models.LsiResult import LsiResult

from lsi_document_similarity import get_document_similarity_matrix_with_lsi

import concurrent.futures

from typing import List


app = Flask(__name__)


@app.route('/api/similar_documents/<int:article_id>', methods=['GET'])
def get_similar_documents(article_id):

    is_hash_value_actual, actual_hash_value = check_hash_value()

    if is_hash_value_actual:
        result = database_utils.get_article_lsi_results(article_id)
    else:
        lsi_similarities = calculate_lsi_similarities()
        save_lsi_similarities(lsi_similarities, actual_hash_value)
        lsi_results = next(item.lsi_results for item in lsi_similarities if item.id == article_id)
        result = [lsi_result.to_dict() for lsi_result in lsi_results]

    # Преобразование списка словарей в JSON-ответ
    return jsonify(result)


def check_hash_value():
    actual_document_ids = database_utils.get_document_ids()
    actual_hash_value = hash_utils.get_hash(actual_document_ids)
    db_hash_value = database_utils.get_article_lsi_similarities_hash()

    return actual_hash_value == db_hash_value, actual_hash_value


def calculate_lsi_similarities() -> List[DocumentLsiSimilarities]:
    # Загрузка коллекции документов из БД
    documents = database_utils.get_documents()

    def get_text_for_document(document):
        document.text = pdf_utils.process_url(document.url)

    # Параллельная загрузка текстов документов
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_text_for_document, documents)

    # Получение матрицы сходства документов с помощью LSI
    similarity_matrix, index_to_id = get_document_similarity_matrix_with_lsi(documents)

    # Поиск 10 наиболее близких документов для каждого документа
    result = []
    for article_id, values in zip(index_to_id.values(), similarity_matrix):
        article_result = []
        for other_article_index, value in enumerate(values):
            other_article_id = index_to_id[other_article_index]
            if other_article_id == article_id:
                continue
            article_result.append(LsiResult(other_article_id, round(value, 6)))

        # Сортировка результатов по убыванию значения сходства документов
        sorted_result = sorted(article_result, key=lambda x: x.similarity, reverse=True)
        # Выбор первых 10 документов
        top_10_result = sorted_result[:10]

        result.append(DocumentLsiSimilarities(article_id, top_10_result))

    return result


def save_lsi_similarities(lsi_similarities: List[DocumentLsiSimilarities], hash_value):
    database_utils.update_article_lsi_similarities(lsi_similarities)
    database_utils.update_article_lsi_similarities_hash(hash_value)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=3000)
