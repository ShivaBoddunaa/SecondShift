import traceback
from fastapi.templating import Jinja2Templates

try:
    # We need to mock the request object for Jinja2 url_for etc.
    class MockRequest(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.scope = {}
            self.url = ""
            
    templates = Jinja2Templates(directory="templates")
    context = {
        "request": MockRequest({"type": "http"}),
        "items": [],
        "user_id": 1,
        "category": "",
        "min_price": "",
        "max_price": "",
        "condition": "",
        "search": "",
        "sort": "newest"
    }
    templates.get_template("buy.html").render(context)
    print("SUCCESS")
except Exception:
    with open("traceback.txt", "w") as f:
        f.write(traceback.format_exc())
