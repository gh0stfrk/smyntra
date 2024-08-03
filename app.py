from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import json
import requests as rq

app = Flask(__name__)

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding":"gzip, deflate, br, zstd",
    "accept-language":"en-US,en;q=0.6",
    "sec-ch-ua":'"Brave";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-platform": '"Linux"'
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


@app.route("/status")
def status():
    return "OK"




# if __name__ == "__main__":
#     app.run(port=5000, debug=True)
# Uncomment to test locally