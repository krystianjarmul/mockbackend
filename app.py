import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "postgresdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "postgres")
DB_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    keywords = db.Column(db.String(120), unique=True, nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    fund = db.Column(db.Float, nullable=False)
    status = db.Column(db.Boolean, nullable=False)
    town = db.Column(db.String(120))
    radius = db.Column(db.Float)

    def __repr__(self):
        return self.name

    
class CampaignSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Campaign


@app.route("/campaigns", methods=["GET"])
def list_campaigns():
    campaigns = Campaign.query.all()
    campaigns_schema = CampaignSchema(many=True)
    result = campaigns_schema.dump(campaigns)
    return jsonify(result), 200


@app.route("/campaigns", methods=["POST"])
def create_campaign():
    campaign_schema = CampaignSchema()
    errors = campaign_schema.validate(request.json)
    if errors:
        return jsonify({"errors": errors}), 400
    
    campaign = Campaign(**request.json)
    db.session.add(campaign)
    db.session.commit()

    result = campaign_schema.dump(campaign)
    return jsonify(result), 200


@app.route('/campaigns/<int:pk>', methods=['GET'])
def retrieve_campaign(pk):
    campaign = Campaign.query.get(pk)
    campaign_schema = CampaignSchema()
    if not campaign:
        return jsonify({"error": "A campaign does not exist"}), 404

    result = campaign_schema.dump(campaign)
    return jsonify(result), 200


@app.route('/campaigns/<int:pk>', methods=['PUT'])
def update_campaign(pk):
    campaign = Campaign.query.get(pk)
    campaign_schema = CampaignSchema()
    if not campaign:
        return jsonify({"error": "A campaign does not exist"}), 404

    errors = campaign_schema.validate(request.json)
    if errors:
        return jsonify({"errors": errors}), 404

    campaign.name = request.json.get("name")
    campaign.keywords = request.json.get("keywords")
    campaign.bid_amount = request.json.get("bid_amount")
    campaign.fund = request.json.get("fund")
    campaign.status = request.json.get("status")
    campaign.town = request.json.get("town")
    campaign.radius = request.json.get("radius")
    db.session.commit()

    result = campaign_schema.dump(campaign)

    return jsonify(result), 200


@app.route('/campaigns/<int:pk>', methods=['DELETE'])
def destroy_campaign(pk):
    campaign = Campaign.query.get(pk)
    campaign_schema = CampaignSchema()
    if not campaign:
        return jsonify({"error": "A campaign does not exist"}), 404

    db.session.delete(campaign)
    db.session.commit()

    result = campaign_schema.dump(campaign)

    return jsonify(result), 200


if __name__ == "__main__":
    db.create_all()
    app.run()
