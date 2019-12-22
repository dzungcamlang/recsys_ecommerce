import argparse
import pickle
import scipy.sparse as sparse
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler, Normalizer, StandardScaler
import pandas as pd
from google_images_download import google_images_download
import string
import re
import os


model = pickle.load(open(os.path.join(os.getcwd(), "recsys/model.pkl"), 'rb'))


def processing_df(df):
    p_df = df[["user_id", "product_id"]]
    p_df["point"] = 1.0
    p_df = p_df.groupby(["user_id", "product_id"]).point.count().reset_index()
    p_df["minmax_scaled"] = MinMaxScaler().fit_transform(p_df.point.values.astype(float).reshape(-1, 1))
    p_df["standard_scaled"] = StandardScaler().fit_transform(p_df.point.values.astype(float).reshape(-1, 1))
    return p_df


data_df = pd.read_csv(os.path.join(os.getcwd(), "recsys/data/core_events.csv"))
data_df.columns = ['id', 'time', 'product_id', 'user_id']
data_df = processing_df(data_df)
most_popular_product_df = data_df.groupby(["product_id"]).point.sum().reset_index().sort_values(["point"], ascending=False)


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
api = Api(app)
# Define parser and request args
parser = reqparse.RequestParser()
parser.add_argument('userid', type=int)
parser.add_argument('productid', type=int)
parser.add_argument('nitems', type=int, default=10)
parser.add_argument('query', type=str)


# creating object
response = google_images_download.googleimagesdownload()


class ImageQuery(Resource):
    # keywords is the search query
    # format is the image file format
    # limit is the number of images to be downloaded
    # print urs is to print the image file url
    # size is the image size which can
    # be specified manually ("large, medium, icon")
    # aspect ratio denotes the height width ratio
    # of images to download. ("tall, square, wide, panoramic")
    def get(self):
        args = parser.parse_args()
        query = str(args['query']).replace("_", " ").lower()
        query = "furniture {query}".format(query=query)
        chars = re.escape(string.punctuation)
        query = re.sub(r'[' + chars + ']', '', query)
        try:
            nitems = int(args['nitems']) if int(args['nitems']) > 0 else 10
        except Exception as e:
            return_js = {"status": 404, "message": "nitems must be an Integer"}
            return jsonify(return_js)

        if len(query) >= 0:
            arguments = {"keywords": query,
                         "format": "jpg",
                         "limit": nitems,
                         "size": "medium",
                         "type": "photo",
                         "aspect_ratio": "panoramic",
                         "output_directory": "./imgs",
                         "no_directory": True,
                         "silent_mode": True,
                         "no_numbering": True}
            try:
                path = response.download(arguments)
            except FileNotFoundError:
                arguments = {"keywords": query,
                             "format": "jpg",
                             "limit": nitems,
                             "size": "medium",
                             "type": "photo",
                             "output_directory": "./imgs",
                             "no_directory": True,
                             "silent_mode": True,
                             "no_numbering": True}

                try:
                    path = response.download(arguments)
                except:
                    return_js = {"status": 404, "message": "Image capturing failed", "query": query}
                    return jsonify(return_js)
            if len(path[0].get(query)) > 0:
                return_js = {"status": 200, "url": path[0].get(query)[0]}
            else:
                return_js = {"status": 404, "message": "Images not found", "query": query}
            return jsonify(return_js)


class UserRecommendation(Resource):

    def get(self):
        args = parser.parse_args()
        uid = args['userid']

        try:
            nitems = int(args['nitems']) if int(args['nitems']) > 0 else 10
        except Exception as e:
            return_js = {"status": 404, "message": "nitems must be an Integer"}
            return jsonify(return_js)

        if uid >= 0:
            try:
                uid = int(uid)
                user_data = data_df[data_df.user_id == uid]
                if len(user_data) > 0:  # old user
                    points = list(user_data.minmax_scaled)
                    u_loc = user_data.user_id.astype(int)
                    p_loc = user_data.product_id.astype(int)
                    UserI_sparse = sparse.csr_matrix((points, (u_loc, p_loc)))
                    rec_list = model.recommend(uid, UserI_sparse, N=nitems, recalculate_user=True)
                    return_js = {
                        "status": 200,
                        "result": [int(idx) for idx, score in rec_list],
                        "user_id": uid
                    }
                else:  # new user
                    return_js = {
                        "status": 200,
                        "result": list(most_popular_product_df.nlargest(n=nitems, columns=["point"]).product_id),
                        "message": "User not found. Most popular products are provided instead."
                    }
                return jsonify(return_js)
            except Exception as e:
                return_js = {"status": 404, "message": "User_id must be an Integer"}
                return jsonify(return_js)
        else:
            return_js = {"status": 404, "message": "No recommendation for this user", "userid": uid}
            return jsonify(return_js)


class SimilarProducts(Resource):

    def get(self):
        args = parser.parse_args()
        pid = args['productid']

        try:
            nitems = int(args['nitems']) if int(args['nitems']) > 0 else 10
        except Exception as e:
            return_js = {"status": 404, "message": "nitems must be an Integer"}
            return jsonify(return_js)

        if pid >= 0:
            try:
                pid = int(pid)
                product_data = data_df[data_df.product_id == pid]
                if len(product_data) > 0:  # old product
                    similar_list = model.similar_items(pid, N=nitems)
                    return_js = {
                        "status": 200,
                        "result": [int(idx) for idx, score in similar_list],
                        "product_id": pid
                    }
                else:  # new product
                    return_js = {
                        "status": 200,
                        "result": list(most_popular_product_df.nlargest(n=nitems, columns=["point"]).product_id),
                        "message": "Product not found. Most popular products are provided instead."
                    }
                return jsonify(return_js)
            except Exception as e:
                return_js = {"status": 404, "message": "User_id must be an Integer"}
                return jsonify(return_js)
        else:
            return_js = {"status": 404, "message": "No similar product", "productid": pid}
            return jsonify(return_js)


api.add_resource(UserRecommendation, '/api/recommend')
api.add_resource(SimilarProducts, '/api/similar')
api.add_resource(ImageQuery, '/api/imageurl')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='BET API')
    argparser.add_argument('--debug', dest='debug', action='store_true')
    argparser.add_argument('--host', metavar='host', action='store', default="0.0.0.0", type=str, help='Host of API')
    argparser.add_argument('--port', metavar='port', action='store', default=5000, type=int, help='Port of API')
    cmdargs = argparser.parse_args()
    app.run(debug=cmdargs.debug, host=cmdargs.host, port=cmdargs.port)
