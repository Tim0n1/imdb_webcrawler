import requests
from bs4 import BeautifulSoup
import concurrent.futures
import pymongo
from Interface import open_gui
import re
IMDB_URL = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

my_client = pymongo.MongoClient("mongodb+srv://timon:U9MzT7HgEAZPsCER@cluster0.nm2hp.mongodb.net/?retryWrites=true&w=majority")
mydb = my_client["imdb"]
mycol = mydb["imdb"]

data = []


class Crawler:
    ratings = []
    all_movies = []
    best_rated_movies_tags = []
    movies_info = []

    def __init__(self, url):
        self.url = url
        results = requests.get(self.url).text
        self.doc = BeautifulSoup(results, 'html.parser')

    def get_all_movie_tags(self):
        all_movies = self.doc.find_all('tbody', class_='lister-list')
        doc = BeautifulSoup(str(all_movies[0]), 'html.parser')
        all_movies = doc.find_all("tr")
        Crawler.all_movies = all_movies
        return Crawler.all_movies

    @staticmethod
    def get_movie_rating(index):
        movie = BeautifulSoup(str(Crawler.all_movies[index]), 'html.parser')
        rating_tag = movie.find(class_="ratingColumn imdbRating")
        rating = rating_tag.text
        rating = rating[1:-1]
        if rating == '':
            return 0
        return float(rating)

    @staticmethod
    def get_a_tag(movie):
        movie = BeautifulSoup(str(movie), 'html.parser')
        tag = movie.find_all('a')[1]
        return tag

    @staticmethod
    def get_title(tag):
        tag = BeautifulSoup(str(tag), 'html.parser')
        title = tag.find('a').text
        return title

    @staticmethod
    def get_director(tag):
        tag = BeautifulSoup(str(tag), 'html.parser')
        director = tag.find('a').attrs['title']
        director = director.split(',')[0]
        director = director[:-7]
        return director

    @staticmethod
    def get_genre(tag):
        genres = []
        tag = BeautifulSoup(str(tag), 'html.parser')
        link = tag.find('a').attrs['href']
        link = 'https://www.imdb.com' + link
        result = requests.get(link, headers=headers).text
        result_doc = BeautifulSoup(result, 'html.parser')
        #print(result_doc)
        result = result_doc.find_all('div', class_="ipc-chip-list--baseAlt ipc-chip-list sc-16ede01-4 bMBIRz")
        for i in result:
            #a_tag = i.find_all("a")
            genres.append(i.text)
        genres = re.findall('[a-zA-Z][^A-Z]*', genres[0])
        return genres

    @staticmethod
    def get_best_rated_movies_tags():
        for index, i in enumerate(Crawler.all_movies):
            if Crawler.get_movie_rating(index) >= 8:
                Crawler.ratings.append(Crawler.get_movie_rating(index))
                a_tags = Crawler.get_a_tag(i)
                Crawler.best_rated_movies_tags.append(a_tags)
        return Crawler.best_rated_movies_tags

    @staticmethod
    def movies_full_info(args):
        title = Crawler.get_title(args[1])
        genre = Crawler.get_genre(args[1])
        directors = Crawler.get_director(args[1])
        rating = Crawler.ratings[args[0]]
        data.append([title, genre, directors, rating])
        return {'title': title, 'genre': genre, 'directors': directors, 'rating': rating}

    @staticmethod
    def get_movies_full_info():
        Crawler.get_best_rated_movies_tags()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(Crawler.movies_full_info, (index, i)) for index, i in enumerate(Crawler.best_rated_movies_tags)]
            results = [i.result() for i in results]

        return results

    @staticmethod
    def save_in_db(movies):
        mycol.insert_many(movies)


crawler = Crawler(IMDB_URL)

# gets all movies and inserts them in Crawler.all_movies
crawler.get_all_movie_tags()

# searches in Crawler.all_movies and gets full info of movies with rating >= 8
results = crawler.get_movies_full_info()

# saves results in database
crawler.save_in_db(results)

# opens GUI
open_gui(data=data)
