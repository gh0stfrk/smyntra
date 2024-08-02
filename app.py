from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import json
import requests as rq

app = Flask(__name__)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}


def get_price(style_id):
    url = f"https://www.myntra.com/{style_id}"
    res = rq.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    script_text = next(
        (
            s.get_text(strip=True)
            for s in soup.find_all("script")
            if "pdpData" in s.text
        ),
        None,
    )
    if script_text:
        try:
            data = json.loads(script_text[script_text.index("{") :])
            mrp = data["pdpData"]["price"]["mrp"]
            price = data["pdpData"]["price"]["discounted"]
            return mrp, price
        except (json.JSONDecodeError, KeyError):
            pass
    return "OOS", None


@app.route("/get_prices", methods=["GET"])
def get_prices():
    style_ids = request.args.get("style_ids").split(",")
    data = []
    for style_id in style_ids:
        mrp, price = get_price(style_id)
        if price:
            data.append({"style_id": style_id, "mrp": mrp, "price": price})
        else:
            data.append({"style_id": style_id, "result": None})
    return jsonify(data)





# if __name__ == "__main__":
#     app.run("0.0.0.0", port=5000, debug=True)
# Uncomment to test locally