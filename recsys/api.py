import pickle
import scipy.sparse as sparse
from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler, Normalizer, StandardScaler
import pandas as pd

model = pickle.load(open('./model.pkl', 'rb'))


def processing_df(df):
    p_df = df[["user_id", "product_id"]]
    p_df["point"] = 1.0
    p_df = p_df.groupby(["user_id", "product_id"]).point.count().reset_index()
    p_df["minmax_scaled"] = MinMaxScaler().fit_transform(p_df.point.values.astype(float).reshape(-1, 1))
    p_df["standard_scaled"] = StandardScaler().fit_transform(p_df.point.values.astype(float).reshape(-1, 1))
    return p_df


data_df = pd.read_csv("./data/core_events.csv")
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


class UserRecommendation(Resource):

    def get(self):
        args = parser.parse_args()
        uid = args['userid']

        try:
            nitems = int(args['nitems']) if int(args['nitems']) > 0 else 10
        except Exception as e:
            return_js = {"status": 404, "message": "nitems must be an Integer"}
            return jsonify(return_js)

        if uid:
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

        if pid:
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
            return_js = {"status": 404, "message": "No similar product", "productid":pid}
            return jsonify(return_js)


api.add_resource(UserRecommendation, '/api/recommend')
api.add_resource(SimilarProducts, '/api/similar')

if __name__ == '__main__':
     app.run(debug=True)
