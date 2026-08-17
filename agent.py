import os
import pandas as pd
import matplotlib.pyplot as plt
from google import genai

from rag_store import query_relevant_columns


# ==========================================
# CONFIGURATION
# ==========================================

CSV_PATH = "Sample - Superstore.csv"
MODEL_NAME = "gemini-3-flash-preview"


# ==========================================
# GEMINI CLIENT
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Set it in the VS Code PowerShell terminal first."
    )

client = genai.Client(api_key=api_key)


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv(CSV_PATH, encoding="latin1")

print(
    f"Dataset loaded: {df.shape[0]} rows, "
    f"{df.shape[1]} columns"
)


# ==========================================
# GENERATE PANDAS CODE USING GEMINI
# ==========================================

def generate_pandas_code(question, rag_context):

    prompt = f"""
You are a data analysis agent working with a Superstore sales dataset.

The dataset is already loaded into a pandas DataFrame called df.

USER QUESTION:
{question}

RELEVANT RAG CONTEXT:
{rag_context}

Your task:

1. Understand the user's question.
2. Decide what pandas operation is required.
3. Generate ONLY executable Python code.
4. Use the existing DataFrame named df.
5. Store the final result in a variable called result.
6. Do not use markdown.
7. Do not use print().
8. Do not import libraries.
9. Do not read another CSV file.
10. Do not modify the original DataFrame.

Example:

result = df.groupby("Region")["Sales"].sum()

Return ONLY the Python code.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# ==========================================
# GENERATE CHART
# ==========================================

def generate_chart(result, question):

    # --------------------------------------
    # Pandas Series
    # --------------------------------------

    if isinstance(result, pd.Series):

        ax = result.plot(
            kind="bar",
            figsize=(9, 5)
        )

        ax.set_title(question)
        ax.set_xlabel(
            result.index.name or "Category"
        )
        ax.set_ylabel(
            result.name or "Value"
        )

        plt.xticks(rotation=0)
        plt.tight_layout()

        chart_path = "chart.png"

        plt.savefig(
            chart_path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return chart_path


    # --------------------------------------
    # Pandas DataFrame
    # --------------------------------------

    elif isinstance(result, pd.DataFrame):

        ax = result.plot(
            kind="bar",
            figsize=(9, 5)
        )

        ax.set_title(question)

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()

        chart_path = "chart.png"

        plt.savefig(
            chart_path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return chart_path


    # --------------------------------------
    # Unsupported result
    # --------------------------------------

    else:

        return None


# ==========================================
# RUN AGENT
# ==========================================

def run_agent(question):

    print("\n" + "=" * 60)
    print("USER QUESTION")
    print("=" * 60)

    print(question)


    # ======================================
    # STEP 1: RAG RETRIEVAL
    # ======================================

    docs, columns = query_relevant_columns(
        question
    )

    print("\nRetrieved columns:")
    print(columns)

    rag_context = "\n".join(docs)


    # ======================================
    # STEP 2: GEMINI GENERATES PANDAS CODE
    # ======================================

    print(
        "\nGenerating Pandas code with Gemini..."
    )

    code = generate_pandas_code(
        question,
        rag_context
    )

    # Remove markdown code fences
    code = code.replace(
        "```python",
        ""
    )

    code = code.replace(
        "```",
        ""
    )

    code = code.strip()


    print("\nGenerated Pandas code:")
    print(code)


    # ======================================
    # STEP 3: EXECUTE PANDAS CODE
    # ======================================

    local_vars = {
        "df": df
    }

    exec(
        code,
        {"__builtins__": {}},
        local_vars
    )

    result = local_vars.get(
        "result"
    )


    print("\nRaw analysis result:")
    print(result)


    # ======================================
    # STEP 4: GEMINI FORMATS ANSWER
    # ======================================

    answer_prompt = f"""
You are a helpful data analysis assistant.

USER QUESTION:
{question}

RELEVANT COLUMNS:
{columns}

ANALYSIS RESULT:
{result}

Give a clear and concise answer to the user's question.

If the result contains multiple categories,
include the important values.

If there is a highest or lowest value,
mention it clearly.

Use simple human-friendly language.

Do not mention:

- Python
- pandas
- RAG
- ChromaDB
- internal processing
- generated code
"""

    answer_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=answer_prompt
    )

    answer = answer_response.text.strip()


    print("\nFinal answer:")
    print(answer)


    # ======================================
    # STEP 5: DECIDE WHETHER CHART IS NEEDED
    # ======================================

    chart_prompt = f"""
You are deciding whether a data visualization would help
answer the user's question.

USER QUESTION:
{question}

ANALYSIS RESULT:
{result}

Return ONLY one of these two values:

CHART

or

NO_CHART

Use CHART when the result involves:

- comparisons between categories
- rankings
- trends over time
- multiple dates
- multiple categories
- distributions

Use NO_CHART when a chart would not add useful information.

Return ONLY:
CHART
or
NO_CHART
"""

    chart_response = client.models.generate_content(
        model=MODEL_NAME,
        contents=chart_prompt
    )

    chart_decision = (
        chart_response.text
        .strip()
        .upper()
    )


    # Clean Gemini's response

    if "NO_CHART" in chart_decision:

        chart_decision = "NO_CHART"

    else:

        chart_decision = "CHART"


    print("\nChart decision:")
    print(chart_decision)


    # ======================================
    # STEP 6: GENERATE CHART
    # ======================================

    chart_path = None

    if chart_decision == "CHART":

        print("\nGenerating chart...")

        chart_path = generate_chart(
            result,
            question
        )

        if chart_path:

            print(
                f"Chart saved to: {chart_path}"
            )

        else:

            print(
                "Chart could not be generated."
            )


    # ======================================
    # RETURN RESULTS
    # ======================================

    return (
        answer,
        result,
        chart_decision,
        chart_path
    )


# ==========================================
# TEST THE AGENT
# ==========================================

if __name__ == "__main__":

    test_question = (
        "What were the total sales by region?"
    )

    (
        answer,
        result,
        chart_decision,
        chart_path
    ) = run_agent(
        test_question
    )


    print("\n" + "=" * 60)
    print("AGENT COMPLETED")
    print("=" * 60)

    print("\nAnswer:")
    print(answer)

    print("\nChart decision:")
    print(chart_decision)

    if chart_path:

        print(
            f"\nChart file: {chart_path}"
        )