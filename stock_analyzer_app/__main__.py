import os

import uvicorn
from stock_analyzer_app.api.app import runtime


def main() -> None:
    runtime.start_scheduler()
    host = os.getenv("STOCK_ANALYZER_HOST", "0.0.0.0")
    port = int(os.getenv("STOCK_ANALYZER_PORT", "8000"))
    uvicorn.run("stock_analyzer_app.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
