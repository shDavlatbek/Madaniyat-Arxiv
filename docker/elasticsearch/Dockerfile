FROM docker.elastic.co/elasticsearch/elasticsearch:8.15.3

# Multi-lingual support: ICU tokenizer + folding handle the Uzbek
# Cyrillic/Latin/Russian mix that lives in Ministry archive documents.
RUN bin/elasticsearch-plugin install --batch analysis-icu
