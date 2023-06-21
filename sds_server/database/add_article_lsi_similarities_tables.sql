CREATE TABLE article_lsi_similarities (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    article_id INT UNSIGNED NOT NULL,
    lsi_results JSON NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    INDEX idx_article_id (article_id)
);

CREATE TABLE article_lsi_similarities_hash (
	hash_value VARCHAR(20) NOT NULL
);