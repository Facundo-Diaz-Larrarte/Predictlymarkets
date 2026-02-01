from fastapi import FastAPI

app = FastAPI(title="Predictly Markets API")


@app.get("/health")
def health():
    return {"status": "ok"}

