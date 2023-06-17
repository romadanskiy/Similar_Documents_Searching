from database.DatabaseConnector import DatabaseConnector

from models.Document import Document


def get_documents():
    journal_id = 11
    local_url_domain = 'https://lobachevskii-dml.ru/'
    lang_ru = 'ru'

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
    WHERE article.journal_id = {journal_id}
    AND article_file.url IS NOT NULL;
    """

    with DatabaseConnector() as db_connector:
        rows = db_connector.execute_query(select_articles_script)

    documents = []
    for row in rows:
        documents.append(Document(int(row['id']), str(row['url']), bool(row['is_russian'])))

    return documents
