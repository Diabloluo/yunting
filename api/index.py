
from flask import Flask, request, render_template_string, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

HTML_TEMPLATE = """ 
<!doctype html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sell Put 推荐小工具 📈</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='0.9em' font-size='90'>💹</text></svg>'>
    <style>
        body {{ background-color: #e6f0ff; font-family: Arial, sans-serif; text-align: center; padding: 20px; margin: 0; }}
        h2 {{ color: #0056b3; margin-top: 20px; }}
        form {{ margin-top: 20px; }}
        input[type=text] {{ padding: 12px; width: 80%; max-width: 300px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }}
        input[type=submit] {{ padding: 12px 24px; font-size: 18px; background-color: #0056b3; color: white; border: none; cursor: pointer; border-radius: 6px; margin-top: 10px; }}
        input[type=submit]:hover {{ background-color: #004494; }}
        .card {{ background: white; padding: 20px; margin-top: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: inline-block; width: 90%; max-width: 500px; }}
        .fade-in {{ animation: fadeIn 0.6s ease-in; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .examples {{ margin-top: 10px; font-size: 14px; color: #666; }}
        .history {{ margin-top: 30px; font-size: 14px; color: #444; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
<h2>Sell Put 推荐小工具 📈</h2>
<div class="examples">示例：AMD、TEM、TSLA、NVDA、AAPL</div>
<form method="post">
  <input type="text" name="symbol" placeholder="请输入股票代码，如 AMD" required><br>
  <input type="submit" value="获取推荐">
</form>
{% if recommendation %}
<div class="card fade-in">
  <h3>推荐策略：</h3>
  <p>{{ recommendation }}</p>
</div>
{% endif %}
{% if history %}
<div class="history">
  <h4>最近查询历史：</h4>
  <ul>
    {% for item in history %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
</div>
{% endif %}
</body>
</html>
"""

def recommend_sell_put(symbol: str, current_price: float) -> str:
    symbol = symbol.upper()
    if symbol == "AMD":
        if current_price >= 100:
            return "[AMD] 推荐Sell Put行权价：95美元，预估权利金约1.8美元/股，策略风格：积极进攻"
        elif 95 <= current_price < 100:
            return "[AMD] 推荐Sell Put行权价：90美元，预估权利金约1.3美元/股，策略风格：稳健保守"
        elif 90 <= current_price < 95:
            return "[AMD] 推荐Sell Put行权价：87.5美元，预估权利金约1.0美元/股，策略风格：稳健超保守"
        elif 85 <= current_price < 90:
            return "[AMD] 推荐Sell Put行权价：85美元，预估权利金约0.7美元/股，策略风格：极度保守"
        else:
            return "[AMD] 当前股价过低（85以下），建议观望或重新评估策略。"
    elif symbol == "TEM":
        if current_price >= 60:
            return "[TEM] 推荐Sell Put行权价：55美元，预估权利金约2.0美元/股，策略风格：积极进攻"
        elif 50 <= current_price < 60:
            return "[TEM] 推荐Sell Put行权价：45美元，预估权利金约1.2美元/股，策略风格：稳健保守"
        elif 45 <= current_price < 50:
            return "[TEM] 推荐Sell Put行权价：40美元，预估权利金约0.8美元/股，策略风格：稳健超保守"
        else:
            return "[TEM] 当前股价过低（45以下），建议谨慎操作或暂缓。"
    elif symbol == "TSLA":
        return f"[TSLA] 当前股价{{current_price}}美元，推荐行权价约90%位置附近，策略偏保守。"
    elif symbol == "NVDA":
        return f"[NVDA] 当前股价{{current_price}}美元，推荐行权价约85%-90%位置，适合滚动Sell Put策略。"
    elif symbol == "AAPL":
        return f"[AAPL] 当前股价{{current_price}}美元，推荐行权价135或130美元附近，稳健保守收租。"
    else:
        return "暂不支持该股票代码，请输入AMD/TEM/TSLA/NVDA/AAPL。"

def get_real_time_price(symbol: str) -> float:
    try:
        api_key = "daa15a0f598e4d1595e255110a357ede"
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        if 'price' in data:
            return float(data['price'])
        else:
            return None
    except Exception:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendation = None
    if 'history' not in session:
        session['history'] = []
    if request.method == 'POST':
        symbol = request.form['symbol']
        current_price = get_real_time_price(symbol)
        if current_price:
            recommendation = recommend_sell_put(symbol, current_price)
        else:
            recommendation = "未能获取实时股价，请检查股票代码或稍后重试。"
        session['history'].insert(0, symbol.upper())
        session['history'] = session['history'][:5]
    return render_template_string(HTML_TEMPLATE, recommendation=recommendation, history=session.get('history'))

if __name__ == "__main__":
    app.run(debug=True)
