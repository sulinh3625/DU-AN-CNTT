"""Chạy web demo:  python -m demo  (từ thư mục neumf_project/)"""
import uvicorn

uvicorn.run("demo.backend.main:app", host="127.0.0.1", port=8000)
