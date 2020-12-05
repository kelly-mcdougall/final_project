import http.client
import json
import pandas as pd
import requests
from datetime import datetime
from lxml import etree
from json.decoder import JSONDecodeError
import logging

logging.basicConfig(filename='log.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

init_doi = '10.1162/rest_a_00754'
edges_array = []
nodes_array = []
total_citations = 0
new_citation_lists = []

def get_json(article_doi):
    global total_citations
    total_citations += 1
    url = 'https://opencitations.net/index/api/v1/metadata/{}'.format(article_doi)
    header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    r = requests.get(url, headers=header)
    json_data = r.json()
    return json_data

def load_article(article_doi):
    json_data = get_json(article_doi)

    def build_node_list(article_data):
        nodes_array.append(article_data)

    def build_edge_list(citation_list):
        for i in range(len(citation_list)):
            edges_array.append([i, citation_list[i].strip(), article_doi, 'citation', 1])
            json_data = get_json(citation_list[i].strip())
            article_data, citation_list_two = parse_json(json_data)
            build_node_list(article_data)

    article_data, citation_list = parse_json(json_data)

    build_node_list(article_data)
    build_edge_list(citation_list)

    df1 = pd.DataFrame(nodes_array, columns=['~id', '~label', 'oa_link', 'citation_count', 'source_title', 'year', 'author', 'title'])
    df1.to_csv('nodes.csv', index=None) # save df to file
    df2 = pd.DataFrame(edges_array, columns=['~id', '~from', '~to', '~label', 'strength'])
    df2.to_csv('edges.csv', index=None) # save df to file
    return citation_list

def parse_json(json_data):
    doi = json_data[0]['doi']
    oa_link = json_data[0]['oa_link']
    citation_count = json_data[0]['citation_count']
    citation_list = json_data[0]['citation'].split("; ")
    source_title = json_data[0]['source_title']
    year = json_data[0]['year']
    author = json_data[0]['author']
    title = json_data[0]['title']
    data_list = [doi, 'article', oa_link, citation_count, source_title, year, author, title]
    return data_list, citation_list


def reload(citation_list):
    y = citation_list
    try:
        new_citation_lists.remove(citation_list)
    except ValueError as ve:
        pass

    for citation in y:
        try:
            print(citation.strip())
            x = load_article(citation.strip())
            print(x)
            new_citation_lists.append(x)
        except JSONDecodeError as e:
            pass

    for citation_list in new_citation_lists:
        print(citation_list)
        reload(citation_list)

citation_list = load_article(init_doi)
reload(citation_list)
