"""
Advanced usage example with custom configuration
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import eskai
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eskai import ESKAI, ESKAIConfig

def main():
    # Custom configuration
    config = ESKAIConfig(
        max_concurrent_agents=5,
        enable_parallel_execution=True,
        log_level="DEBUG",
        default_timeout=1800  # 30 minutes
    )
    
    # Initialize ESKAI with custom config
    agi = ESKAI(config=config)
    
    # Complex multi-objective task
    complex_prompt = """
    I need you to:
    1. Research the latest trends in artificial intelligence for 2025
    2. Analyze the potential impact on software development
    3. Create a strategic roadmap for a tech company to adopt these technologies
    4. Provide specific implementation recommendations with timelines
    """
    
    print("Processing complex multi-objective task...")
    print("This may take a few minutes...")
    
    result = agi.process(
        prompt=complex_prompt,
        max_execution_time=1800,  # 30 minutes
        enable_internet=True,
        enable_code_execution=True
    )
    
    if result['success']:
        print(f"\n=== Execution Summary ===")
        print(f"Execution ID: {result['execution_id']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        
        # Show objectives that were formulated
        objectives = result['objectives']['primary_objectives']
        print(f"\nPrimary Objectives ({len(objectives)}):")
        for i, obj in enumerate(objectives, 1):
            print(f"  {i}. {obj}")
        
        # Show final result
        final_result = result['final_result']['final_result']
        print(f"\n=== Final Result ===")
        print(final_result)
        
        # Show alignment metrics
        alignment = result['final_result']['objective_alignment']
        print(f"\n=== Quality Metrics ===")
        print(f"Overall Alignment: {alignment['overall_alignment_score']:.1%}")
        print(f"Objectives Addressed: {alignment['fully_addressed']}/{alignment['total_objectives']}")
        print(f"Completeness Score: {result['final_result']['completeness_score']:.1%}")
        
        # Show execution details
        exec_summary = result['final_result']['execution_summary']
        print(f"Success Rate: {exec_summary['success_rate']:.1%}")
        print(f"Total Duration: {exec_summary['total_duration']:.2f}s")
        
    else:
        print(f"Error: {result['error']}")

async def async_example():
    """Example of asynchronous processing"""
    config = ESKAIConfig()
    agi = ESKAI(config=config)
    
    # Process multiple tasks concurrently
    tasks = [
        "Summarize the key benefits of renewable energy",
        "Explain the basics of machine learning",
        "List the top 5 programming languages for 2025"
    ]
    
    print("Processing multiple tasks asynchronously...")
    
    async_results = await asyncio.gather(*[
        agi.process_async(task) for task in tasks
    ])
    
    for i, result in enumerate(async_results):
        print(f"\nTask {i+1}: {tasks[i]}")
        if result['type'] == 'chat':
            print(f"Response: {result['response']}")
        else:
            print(f"Result: {result['final_result']['final_result']}")

if __name__ == "__main__":
    # Run synchronous example
    main()
    
    # Uncomment to run async example
    # asyncio.run(async_example())
