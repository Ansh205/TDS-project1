#This is tds project 1 


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI ()

app.add_middleware (
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['GET', 'POST'],
    allow_headers = ['*']

)


@app.get("/")
def read_root():
    return {"message": "Hello from the Automation Agent!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)