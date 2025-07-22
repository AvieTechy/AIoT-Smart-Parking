# Smart Parking FastAPI Service

## Cấu trúc thư mục

```
smart-parking/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

## Chạy local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Chạy với Docker
```bash
docker build -t smart-parking-api .
docker run -p 8000:8000 smart-parking-api
```
