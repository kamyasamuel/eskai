# RAW AGI FRAMEWORK DESIGN

## Overview
This framework approaches a custom AGI that executes solutions following layers of actions.

## Layer Architecture

### Layer 1: Prompt Assessment Layer
- Determines intent with two outcomes: objective or mere response (chat)
- For generic conversational prompts (hello, hi, casual chat), the AGI stops here and generates a simple response
- No further processing needed for non-objective conversations

### Layer 2: Objective Formulation
- Uses Groq, OpenAI, and Gemini inference to extract objective(s)
- Generates expected outcome list
- Critiques objectives to ensure they can be met
- Multi-provider validation for robustness

### Layer 3: Work Plan Generation
- Creates workflow for downstream agents based on expected outcomes from Layer 2
- Critiques workflow using Groq, OpenAI, and Gemini
- Generates final validated workflow

### Layer 4: Agent Orchestration
- Interprets workflow and breaks it down into individual objectives
- Determines agent execution order based on dependencies:
  - Dependent agents run after primary agents complete
  - Independent agents run concurrently
- Outputs:
  - Markdown documentation
  - JSON object containing:
    - Agent name
    - Input prompt
    - System prompt
    - Tools called (if applicable)
    - Model to use
    - Order of agent execution

### Layer 5: Execution
- Interprets JSON from Layer 4
- Deploys and runs different agents
- Extensive logging throughout the process
- Yields markdown file with results from each agent according to objectives pursued

### Layer 6: Final Result Rendering
- Synthesizes results from execution layer into final result
- Maintains full awareness of initial objectives
- Produces coherent final output

## Key Requirements

### Tools and Capabilities
- Must support internet access and computer use for code execution
- Should create tools on-the-fly as needed
- Must save working tools to its arsenal for future use
- Core tools: internet, computer use (code execution)

### Multi-Provider AI Integration
- Groq, OpenAI, and Gemini for critical decision points
- Cross-validation and critique capabilities
- Redundancy for reliability

### Tracking and Documentation
- Extensive logging at all layers
- Markdown output for human readability
- JSON objects for machine processing
- Full traceability from input to output
