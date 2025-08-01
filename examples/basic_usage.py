"""
Basic usage example for ESKAI
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import eskai
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eskai import ESKAI, ESKAIConfig

def main():
    # Initialize ESKAI with default configuration
    agi = ESKAI()
    
    # Simple chat interaction
    print("=== Simple Chat ===")
    response = agi.process("Hello, how are you?")
    print(f"Response: {response['response']}")
    print()
    
    # Objective-driven task
    print("=== Objective Task ===")
    result = agi.process("Create a brief market analysis for electric vehicles")
    
    print(f"Execution ID: {result['execution_id']}")
    print(f"Processing Time: {result['processing_time']:.2f}s")
    print(f"Type: {result['type']}")
    
    if result['success']:
        final_result = result['final_result']['final_result']
        print(f"Result: {final_result}")
        
        alignment = result['final_result']['objective_alignment']
        print(f"Objective Alignment: {alignment['overall_alignment_score']:.1%}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
