# Superstore Data Analytics Dashboard

An interactive data analytics dashboard built with Streamlit that analyzes retail sales data and answers natural language questions using an AI-powered RAG (Retrieval-Augmented Generation) pipeline.

## About the Project

This project explores the Sample Superstore dataset to uncover trends in sales, profit, and customer behavior across regions and categories. Beyond static charts, it integrates an AI agent that lets users ask questions about the data in plain English and get context-aware answers, powered by a ChromaDB vector store for retrieval.

## Features

- Interactive dashboards for sales, profit, and category-wise performance
- AI chat agent to query data using natural language
- RAG-based retrieval system using ChromaDB for accurate responses
- Data cleaning and preprocessing pipeline
- Visualizations built with Python

## Tech Stack

- **Frontend:** Streamlit
- **Data Analysis:** Python, Pandas, NumPy
- **Vector Store:** ChromaDB
- **Language:** Python 3.11

## Project Structure

Superstore-proj/
├── app.py # Main Streamlit application
├── agent.py # AI agent logic
├── rag_store.py # RAG pipeline and vector store setup
├── check_data.py # Data validation script
├── chroma_store/ # Vector database storage
├── Sample - Superstore.csv # Dataset
└── chart.png # Sample dashboard visualization
