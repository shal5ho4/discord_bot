# from threading import Thread

# from fastapi import FastAPI
# import uvicorn


# app = FastAPI()

# @app.get('/')
# async def root():
#     return {'message': 'Server is ONLINE.'}


# def start_uvicorn():
#     uvicorn.run(app, host='0.0.0.0', port=8080)

# def server_thread():
#     t = Thread(target=start_uvicorn, daemon=True)
#     t.start()
