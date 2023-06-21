from database.DatabaseConnector import DatabaseConnector

from models.Document import Document
from models.DocumentLsiSimilarities import DocumentLsiSimilarities

import json

from typing import List

journal_id = 11
local_url_domain = 'https://lobachevskii-dml.ru/'
lang_ru = 'ru'


def get_documents():
    select_articles_script = f"""
    SELECT
        article.id AS id,
        CASE
            WHEN article_file.remote = 0 THEN CONCAT('{local_url_domain}', article_file.url)
            ELSE article_file.url
        END AS url,
        CASE 
            WHEN article.lang = '{lang_ru}' THEN TRUE 
            ELSE FALSE 
        END AS is_russian
    FROM articles article
    JOIN article_files article_file ON article_file.id = article.id
    WHERE article.journal_id = {journal_id};
    """

    with DatabaseConnector() as db_connector:
        rows = db_connector.execute_query(select_articles_script)

    documents = []
    for row in rows:
        documents.append(Document(int(row['id']), str(row['url']), bool(row['is_russian'])))

    return documents


def get_document_ids():
    select_article_ids_script = f"""
    SELECT id
    FROM articles
    WHERE journal_id = {journal_id};
    """

    with DatabaseConnector() as db_connector:
        rows = db_connector.execute_query(select_article_ids_script)

    document_ids = []
    for row in rows:
        document_ids.append(int(row['id']))

    return document_ids


def get_article_lsi_similarities_hash():
    select_hash_script = f"""
    SELECT hash_value
    FROM article_lsi_similarities_hash;
    """

    with DatabaseConnector() as db_connector:
        rows = db_connector.execute_query(select_hash_script)

    if rows:
        return str(rows[0]['hash_value'])

    return None


def update_article_lsi_similarities_hash(hash_value):
    clear_lsi_similarities_script = f"""
    DELETE FROM article_lsi_similarities_hash;
    """

    insert_lsi_similarities_script = f"""
    INSERT INTO article_lsi_similarities_hash (hash_value)
    VALUES ('{hash_value}');
    """

    with DatabaseConnector() as db_connector:
        db_connector.execute_query(clear_lsi_similarities_script)
        db_connector.execute_query(insert_lsi_similarities_script)
        db_connector.commit()


def get_article_lsi_results(article_id):
    select_article_lsi_result_script = f"""
    SELECT lsi_results
    FROM article_lsi_similarities
    WHERE article_id = {article_id};
    """

    with DatabaseConnector() as db_connector:
        rows = db_connector.execute_query(select_article_lsi_result_script)

    json_lsi_result = rows[0]['lsi_results']
    lsi_result = json.loads(json_lsi_result)

    return lsi_result


def update_article_lsi_similarities(lsi_similarities: List[DocumentLsiSimilarities]):
    clear_lsi_similarities_script = f"""
    DELETE FROM article_lsi_similarities;
    """

    insert_lsi_similarities_script = f"""
    INSERT INTO article_lsi_similarities (article_id, lsi_results) 
    VALUES (%s, %s);
    """

    with DatabaseConnector() as db_connector:
        db_connector.execute_query(clear_lsi_similarities_script)

        for item in lsi_similarities:
            article_id = item.id
            lsi_results = [lsi_result.to_dict() for lsi_result in item.lsi_results]
            json_lsi_results = json.dumps(lsi_results)

            db_connector.execute_query(insert_lsi_similarities_script, (article_id, json_lsi_results))

        db_connector.commit()
