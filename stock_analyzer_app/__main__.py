import uvicorn
from stock_analyzer_app.api.app import runtime


def main() -> None:
    runtime.start_scheduler()
    uvicorn.run("stock_analyzer_app.api:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
