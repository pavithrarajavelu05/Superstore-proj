import chromadb
import pandas as pd

# ---- Column descriptions (this is the "knowledge" the agent retrieves from) ----
COLUMN_DESCRIPTIONS = {
    "Row ID": "Unique identifier for each row in the dataset.",
    "Order ID": "Unique identifier for each customer order. Multiple rows can share the same Order ID if the order had multiple products.",
    "Order Date": "The date the order was placed. Useful for trend, monthly, yearly, or seasonal analysis.",
    "Ship Date": "The date the order was shipped to the customer.",
    "Ship Mode": "How the order was shipped. Categorical values include Standard Class, Second Class, First Class, Same Day.",
    "Customer ID": "Unique identifier for each customer.",
    "Customer Name": "Full name of the customer who placed the order.",
    "Segment": "Customer segment/type. Categorical values: Consumer, Corporate, Home Office.",
    "Country": "Country where the order was placed. All values are United States in this dataset.",
    "City": "City where the order was placed.",
    "State": "US state where the order was placed.",
    "Postal Code": "Postal/ZIP code of the delivery address.",
    "Region": "Broad geographic region. Categorical values: South, West, Central, East.",
    "Product ID": "Unique identifier for each product.",
    "Category": "High-level product category. Categorical values: Furniture, Office Supplies, Technology.",
    "Sub-Category": "More specific product type within a Category, e.g. Chairs, Phones, Binders.",
    "Product Name": "Full descriptive name of the product.",
    "Sales": "Total sale amount in USD for that line item (before considering profit/discount).",
    "Quantity": "Number of units of the product sold in that order line.",
    "Discount": "Discount applied to that order line, expressed as a decimal (e.g. 0.20 = 20% discount).",
    "Profit": "Profit earned on that order line in USD. Can be negative if the item sold at a loss.",
}

def build_vector_store(csv_path="Sample - Superstore.csv"):
    """Reads the dataset, embeds column descriptions + sample rows into ChromaDB."""
    df = pd.read_csv(csv_path, encoding="latin1")

    client = chromadb.PersistentClient(path="./chroma_store")
    # Reset collection each time we rebuild, so repeated runs don't duplicate entries
    try:
        client.delete_collection("superstore_schema")
    except Exception:
        pass
    collection = client.create_collection("superstore_schema")

    documents = []
    metadatas = []
    ids = []

    for i, (col, desc) in enumerate(COLUMN_DESCRIPTIONS.items()):
        dtype = str(df[col].dtype)
        sample_values = df[col].dropna().unique()[:5].tolist()

        doc_text = (
            f"Column: {col}. "
            f"Description: {desc} "
            f"Data type: {dtype}. "
            f"Sample values: {sample_values}."
        )
        documents.append(doc_text)
        metadatas.append({"column_name": col, "dtype": dtype})
        ids.append(f"col_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Vector store built with {len(documents)} column entries.")
    return collection

def query_relevant_columns(question: str, n_results: int = 6):
    """Given a user question, retrieve the most relevant column descriptions."""
    client = chromadb.PersistentClient(path="./chroma_store")
    collection = client.get_collection("superstore_schema")

    results = collection.query(query_texts=[question], n_results=n_results)
    retrieved_docs = results["documents"][0]
    retrieved_cols = [m["column_name"] for m in results["metadatas"][0]]

    return retrieved_docs, retrieved_cols

if __name__ == "__main__":
    # Step A: build the store (run this once, or whenever data/descriptions change)
    build_vector_store()

    # Step B: test retrieval with a sample question
    test_question = "What were total sales by region over time?"
    docs, cols = query_relevant_columns(test_question)

    print(f"\nTest question: {test_question}")
    print(f"Retrieved columns: {cols}\n")
    for d in docs:
        print("-", d)