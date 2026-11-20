

\# Crop Guardian

\### Understand Your Crops. Protect Your Harvest.



Crop Guardian is an AI-powered agricultural assistance platform that helps farmers examine possible crop diseases through plant photographs.



\## Features



\- AI-powered plant disease assessment

\- Google Gemini visual analysis

\- Custom EfficientNet-B0 classifier

\- Hybrid AI prediction comparison

\- Uncertainty and review detection

\- Agricultural knowledge retrieval using RAG

\- ChromaDB vector database

\- Weather information and agricultural context

\- Disease Guide

\- Diagnosis History

\- Original image storage

\- Printable diagnosis reports

\- English and Bengali interface



\## Supported Crops



\- Potato

\- Tomato

\- Rice

\- Brinjal

\- Jute



Note: EfficientNet-B0 currently supports potato and tomato. Other crop selections use the Gemini assessment pathway.



\## Technology Stack



\### Frontend

\- React

\- TypeScript

\- Vite

\- Tailwind CSS



\### Backend

\- Python 3.11

\- FastAPI

\- Uvicorn

\- Pydantic



\### AI and Machine Learning

\- Google Gemini API

\- PyTorch

\- Torchvision

\- TIMM

\- EfficientNet-B0



\### RAG

\- ChromaDB

\- Sentence Transformers

\- all-MiniLM-L6-v2



\## AI Architecture



Crop Guardian combines Gemini visual assessment with EfficientNet-B0 classification for supported crops.



A custom hybrid diagnosis engine compares predictions and flags disagreements for further review.



The RAG system uses Sentence Transformers and ChromaDB to retrieve relevant agricultural knowledge.



Farmer-facing recommendations are restricted when model agreement or knowledge verification requirements are not satisfied.



\## Local Installation



Requirements:

\- Python 3.11

\- Node.js and npm

\- Gemini API key



\### Backend
