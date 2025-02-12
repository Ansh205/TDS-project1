#This is tds project 1 


from fastapi import FastAPI , HTTPException, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import subprocess
import json

app=FastAPI ()

app.add_middleware (
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['GET', 'POST'],
    allow_headers = ['*']

)

tools = [
    {
        "type": "function",
        "function":{
            "name": "script_runner",
            "description": "Install a package and run a script from a url with provided arguments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_url": {
                        "type": "string",
                        "description": "The url of the script to run."
                    },
                    "args": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of arguments to pass to the script."
                    },
                },"required": ["script_url", "args"]
            }
        },
    }
]


AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise Exception("AIPROXY_TOKEN is required. Set it as an environment variable.")
@app.get("/")
def read_root():
    return {"message": "Hello from the Automation Agent!"}


@app.get("/read", response_class=PlainTextResponse)
def read(path: str = Query(..., description="Path to file under /data to read.")):
    try:
        # Set allowed root to your project's data folder.
        #allowed_root = os.path.join(os.getcwd(), "data")
        #validate_path(path, allowed_root)
        #if not os.path.exists(path):
        #    raise HTTPException(status_code=404, detail="File not found")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
def run(task: str = Query(..., description="The plain‑English task description.")):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json" 
    }
    data={
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user", "content": task
            },
            {
                "role": "system",
                "content": """
                
                You are an assistant who has to do a varity of tasks
                if your task involves running a script, you can use script_runner tool.
                If your task involves writing a code, you can use the task_runner tool.
                """
                
            }
        ],
        "tools": tools,
        "tool_choice":"auto"
    }
    response = requests.post(url=url, headers=headers, json=data)
    #return response.json()['choices'][0]['message']['tool_calls'][0]['function']
    raw_args =response.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    if isinstance(raw_args, str):
        arguments = json.loads(raw_args)
    else:
        arguments = raw_args
    
    script_url=arguments['script_url']
    email=arguments['args'][0]
    command= ["uv", "run", script_url, email]
    subprocess.run(command)
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)