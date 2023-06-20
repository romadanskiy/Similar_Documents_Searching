from flask import Flask, jsonify, make_response

import database.database_utils as database_utils
import pdf_utils

from models.Document import Document
from models.LsiResult import LsiResult

from lsi_document_similarity import get_document_similarity_matrix_with_lsi

import concurrent.futures


app = Flask(__name__)


@app.route('/api/similar_documents/<int:article_id>', methods=['GET'])
def get_similar_documents(article_id):
    # Загрузка коллекции документов из БД
    documents = database_utils.get_documents()

    def get_text_for_document(document):
        document.text = pdf_utils.process_url(document.url)

    # Параллельная загрузка текстов документов
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_text_for_document, documents)

    # Получение матрицы сходства документов с помощью LSI
    similarity_matrix, index_to_id = get_document_similarity_matrix_with_lsi(documents)
    id_to_index = {value: key for key, value in index_to_id.items()}

    # Извлечение данных для запрашиваемого документов
    article_index = id_to_index[article_id]
    values = similarity_matrix[article_index]

    result = []
    for idx, value in enumerate(values):
        other_article_id = index_to_id[idx]
        if other_article_id == article_id: continue
        result.append(LsiResult(other_article_id, round(value, 6)))

    # Сортировка результатов по убыванию значения сходства документов
    sorted_result = sorted(result, key=lambda x: x.similarity, reverse=True)
    # Выбор первых 10 документов
    top_10_result = sorted_result[:10]

    # Представление результа в виде списка словарей
    json_result = [item.to_dict() for item in top_10_result]

    # Преобразование списка словарей в JSON-ответ
    return jsonify(json_result)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=3000)
