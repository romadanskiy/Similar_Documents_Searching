from flask import Flask, jsonify, make_response

from models.Document import Document
from models.LsiResult import LsiResult


from lsi_document_similarity import get_document_similarity_matrix_with_lsi

app = Flask(__name__)

test_documents = []

# test_documents.append(Document(1, "матрица вектор алгебра", True))
# test_documents.append(Document(2, "спорт футбол мяч", True))
# test_documents.append(Document(3, "мяч матрица", True))
# test_documents.append(Document(4, "вектор алгебра спорт", True))
# test_documents.append(Document(5, "матрица вектор", True))

test_documents.append(Document(1, "Матрицы и вектора являются фундаментальными понятиями в линейной алгебре.", True))
test_documents.append(Document(2, "Математическая статистика - это раздел математики, который изучает методы анализа данных и принятия статистических выводов на основе вероятностных моделей.", True))
test_documents.append(Document(3, "Матрица представляет собой двумерную таблицу чисел, расположенных в строках и столбцах.", True))
test_documents.append(Document(4, "Основная цель теории вероятностей - описать и формализовать случайные явления, а также предсказать их вероятности и свойства с помощью математических моделей.", True))
test_documents.append(Document(5, "Теория вероятностей - это математическая наука, которая изучает случайные явления и их вероятностные свойства.", True))
test_documents.append(Document(6, "В математической статистике исследуются различные статистические методы, такие как оценка параметров, проверка гипотез, построение доверительных интервалов и анализ дисперсии.", True))
test_documents.append(Document(7, "В линейной алгебре изучаются понятия векторов, матриц, линейных преобразований и их свойств.", True))
test_documents.append(Document(8, "В линейной алгебре матрицы и вектора играют важную роль и являются базовыми элементами.", True))
test_documents.append(Document(9, "В линейной алгебре фундаментальными понятиями являются вектора и матрицы.", True))

@app.route('/api/similar_documents/<int:article_id>', methods=['GET'])
def get_similar_documents(article_id):

    # \/ тестовый код

    similarity_matrix, index_to_id = get_document_similarity_matrix_with_lsi(test_documents)
    id_to_index = {value: key for key, value in index_to_id.items()}
    article_index = id_to_index[article_id]
    values = similarity_matrix[article_index]

    result = []
    for idx, value in enumerate(values):
        other_article_id = index_to_id[idx]
        if other_article_id == article_id: continue
        result.append(LsiResult(other_article_id, round(value, 6)))

    sorted_result = sorted(result, key=lambda x: x.similarity, reverse=True)

    # /\ тестовый код

    json_result = [item.to_dict() for item in sorted_result]
    return jsonify(json_result)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=3000)
