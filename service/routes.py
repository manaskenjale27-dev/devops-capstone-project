"""
Account Service REST API
"""
from flask import jsonify, request, make_response, abort, url_for
from service.models import Account, DataValidationError
from service.common import status
from . import app

@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK

@app.route("/")
def index():
    """Root URL response"""
    return jsonify(name="Account REST API Service", version="1.0"), status.HTTP_200_OK

@app.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an account from request JSON."""
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    location_url = url_for("get_accounts", account_id=account.id, _external=True)
    return make_response(jsonify(account.serialize()), status.HTTP_201_CREATED, {"Location": location_url})

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Returns all accounts."""
    app.logger.info("Request to list Accounts")
    accounts = Account.all()
    results = [account.serialize() for account in accounts]
    return jsonify(results), status.HTTP_200_OK

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """Reads an account by ID."""
    app.logger.info("Request to read Account %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")
    return jsonify(account.serialize()), status.HTTP_200_OK

@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """Updates an account by ID."""
    app.logger.info("Request to update Account %s", account_id)
    check_content_type("application/json")
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")
    account.deserialize(request.get_json())
    account.id = account_id
    account.update()
    return jsonify(account.serialize()), status.HTTP_200_OK

@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """Deletes an account by ID."""
    app.logger.info("Request to delete Account %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{account_id}' was not found.")
    account.delete()
    return "", status.HTTP_204_NO_CONTENT

def check_content_type(media_type):
    """Checks that the media type is correct."""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {media_type}")
