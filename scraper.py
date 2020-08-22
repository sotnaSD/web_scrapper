from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from collections import defaultdict
import pandas as pd
import bs4
import re


class Spider:
    """
    This class is created based on two diaries, it is not optimized
    for working with any web site.
    """

    def __init__(self, start_url: str, key_words: list):
        self.start_url = start_url
        self.current_url = start_url
        self.key_words_to_search = key_words
        self.visited_urls = []
        self.current_id =''
        self.articles_found= defaultdict(dict)

    
    def _initialize_articles_found_dict(self):
        for key_word in self.key_words_to_search:
            self.articles_found[self.current_id][key_word] = 0


    def _get_formated_html(self, url):
        try:
            html = urlopen(url)
            bs = BeautifulSoup(html.read(), 'html.parser')
            return bs
        except HTTPError as e:
            return None
    
    def _get_article_tag(self, bs):
        try:
            article = bs.find('article', {'id':re.compile('\w+-\d+')})            
            return article
        except AttributeError as e:
            return None


    def _crawl_text(self, article):
        already_founded = False
        for child in article.children:
            if type(child) == bs4.element.Tag:
                for key_word in self.key_words_to_search:
                    matches = re.findall(key_word, child.get_text(), re.IGNORECASE)
                    if len(matches) > 0:
                        if not already_founded:
                            self._set_basic_info(article)
                            self._initialize_articles_found_dict()
                            already_founded = True
                        self._update_apperance_counter(key_word, len(matches))


    def _update_apperance_counter(self, key_word, n_matches):
        self.articles_found[self.current_id][key_word] += n_matches


    def _set_basic_info(self, article):
        try:
            self.current_id = article['id']
            self.articles_found[self.current_id ]['date'] = article.find('', {'class':['content-time','entry-date']}).get_text()
            self.articles_found[self.current_id ]['url'] = self.current_url
        except:
            print('Error')


    def start_crawling(self):
        bs = self._get_formated_html(self.current_url)
        article = self._get_article_tag(bs) if bs is not None else None
        if bs and article:
            self.visited_urls.append(self.current_url)
            self._crawl_text(article)

    def show_results(self):
        for k, v in self.articles_found.items():
            print(f'id:{k}')
            for k_v, v_v in v.items():
                print(f'\t{k_v}{v_v}')
    
    def write_to_csv(self, file_name):
        aux_dict = {}
        for k, v in self.articles_found.items():
            aux_dict['id_article'] = [k]
            for k_v, v_v in v.items():
                aux_dict[k_v] = [v_v]
        
        df = pd.DataFrame.from_dict(aux_dict)
        # print(df.head())

        df.to_csv(file_name)

url = 'http://www.heraldocanar.com/articulo/canar/kimera-agrupacion-musical-kanari-todo-alto/20190812170648000936.html/'
# url = 'https://ww2.elmercurio.com.ec/2020/08/22/siguen-reclamos-por-las-planillas-de-agua-potable/'
peter = Spider(url, ['Casa de la Cultura', 'Cañar', 'Benjamín Carrión'])
peter.start_crawling()

peter.write_to_csv('heraldo_canar.csv')