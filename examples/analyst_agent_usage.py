import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eskai.agents.analyst import AnalystAgent

# Set up your API keys in environment variables
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key"
# os.environ["GROQ_API_KEY"] = "your_groq_api_key"
# os.environ["GEMINI_API_KEY"] = "your_gemini_api_key"

async def main():
    """
    Example of how to use the AnalystAgent to analyze a dataset.
    """
    print("Starting AnalystAgent example...")

    # Path to the sample data
    data_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    
    # The objective for the analysis
    objective = (
        "Analyze the provided dataset to understand the distribution of salaries, "
        "the relationship between age and salary, and identify any significant "
        "differences in salary between different cities. "
        "Generate visualizations to support your findings and provide a summary report."
    )

    # Initialize the AnalystAgent
    # You can choose the provider: "openai", "groq", or "gemini"
    analyst = AnalystAgent(
        data_path=data_path,
        analysis_objective=objective,
        llm_provider="openai",  # or "groq", "gemini"
        llm_model="gpt-4o", # or "llama3-70b-8192", "gemini-1.5-flash"
        verbose=True
    )

    # Run the analysis
    try:
        await analyst.run()
        print("\nAnalysis complete. Check the 'reports' and 'charts' directories for output.")
    except Exception as e:
        print(f"\nAn error occurred during analysis: {e}")

if __name__ == "__main__":
    # To run this async script, we use asyncio.run()
    # If you are in a Jupyter notebook, you can just 'await main()'
    asyncio.run(main())
