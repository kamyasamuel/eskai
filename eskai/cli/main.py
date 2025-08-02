"""
ESKAI Command Line Interface
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

from ..core.eskai_main import ESKAI
from ..utils.config import ESKAIConfig


@click.group()
@click.version_option(version="0.1.1")
def cli():
    """ESKAI - Evolved Strategic Knowledge and AI Framework"""
    pass


@cli.command()
@click.argument('prompt', required=False)
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.option('--max-time', type=int, default=3600, help='Maximum execution time in seconds')
@click.option('--no-internet', is_flag=True, help='Disable internet access')
@click.option('--no-code', is_flag=True, help='Disable code execution')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--verbose', '-v', is_flag=True, help='Verbose logging')
def process(
    prompt: Optional[str],
    config: Optional[str],
    interactive: bool,
    max_time: int,
    no_internet: bool,
    no_code: bool,
    output: Optional[str],
    verbose: bool
):
    """Process a prompt through the ESKAI framework."""
    
    # Load configuration
    if config:
        try:
            eskai_config = ESKAIConfig.from_file(config)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    else:
        eskai_config = ESKAIConfig()
    
    # Set verbose logging
    if verbose:
        eskai_config.log_level = "DEBUG"
    
    try:
        # Initialize ESKAI
        agi = ESKAI(config=eskai_config)
        
        if interactive:
            run_interactive_mode(agi, max_time, not no_internet, not no_code)
        elif prompt:
            result = agi.process(
                prompt=prompt,
                max_execution_time=max_time,
                enable_internet=not no_internet,
                enable_code_execution=not no_code
            )
            
            # Output result
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2)
                click.echo(f"Results saved to {output}")
            else:
                display_result(result)
        else:
            click.echo("Please provide a prompt or use --interactive mode")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def run_interactive_mode(agi: ESKAI, max_time: int, enable_internet: bool, enable_code: bool):
    """Run ESKAI in interactive mode."""
    click.echo("ESKAI Interactive Mode")
    click.echo("Type 'exit' to quit, 'help' for commands")
    click.echo("-" * 40)
    
    while True:
        try:
            prompt = click.prompt("ESKAI", type=str)
            
            if prompt.lower() in ['exit', 'quit']:
                click.echo("Goodbye!")
                break
            elif prompt.lower() == 'help':
                show_help()
                continue
            elif prompt.lower() == 'status':
                status = agi.get_status()
                click.echo(json.dumps(status, indent=2))
                continue
            
            click.echo("Processing...")
            
            result = agi.process(
                prompt=prompt,
                max_execution_time=max_time,
                enable_internet=enable_internet,
                enable_code_execution=enable_code
            )
            
            display_result(result)
            
        except KeyboardInterrupt:
            click.echo("\nGoodbye!")
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def display_result(result: dict):
    """Display processing result in a formatted way."""
    
    if result["type"] == "chat":
        click.echo(f"\n💬 {result['response']}\n")
    elif result["type"] == "objective":
        click.echo(f"\n📋 Execution ID: {result['execution_id']}")
        click.echo(f"⏱️  Processing Time: {result['processing_time']:.2f}s")
        
        if "final_result" in result and "final_result" in result["final_result"]:
            click.echo("\n📄 Final Result:")
            click.echo("-" * 40)
            click.echo(result["final_result"]["final_result"])
            
            if "objective_alignment" in result["final_result"]:
                alignment = result["final_result"]["objective_alignment"]
                click.echo(f"\n📊 Objective Alignment: {alignment['overall_alignment_score']:.1%}")
                click.echo(f"✅ Objectives Addressed: {alignment['fully_addressed']}/{alignment['total_objectives']}")
        
        click.echo()
    elif result["type"] == "error":
        click.echo(f"\n❌ Error: {result['error']}")
        click.echo(f"⏱️  Processing Time: {result['processing_time']:.2f}s\n")


def show_help():
    """Show interactive mode help."""
    help_text = """
        Available commands:
        help     - Show this help message
        status   - Show ESKAI system status
        exit     - Exit interactive mode
        
        Just type your request to process it through ESKAI.
    """
    click.echo(help_text)


@cli.command()
def status():
    """Show ESKAI system status."""
    try:
        config = ESKAIConfig()
        agi = ESKAI(config=config)
        status = agi.get_status()
        click.echo(json.dumps(status, indent=2))
    except Exception as e:
        click.echo(f"Error getting status: {e}", err=True)


@cli.command()
@click.option('--output', '-o', type=click.Path(), default='eskai_config.yaml')
def init_config(output: str):
    """Generate a sample configuration file."""
    
    config_template = """eskai:
  providers:
    openai:
      model: "gpt-4.1-2025-04-14"
      temperature: 0.7
    groq:
      model: "qwen/qwen3-32b"
    gemini:
      model: "gemini-2.5-flash"
  
  execution:
    max_concurrent_agents: 3
    timeout_seconds: 3600
    enable_parallel_execution: true
  
  tools:
    enable_internet: true
    enable_code_execution: true
    enable_file_operations: true
  
  logging:
    level: "INFO"
    file: "eskai.log"
"""
    
    try:
        with open(output, 'w') as f:
            f.write(config_template)
        click.echo(f"Configuration template created: {output}")
        click.echo("Don't forget to set your API keys in environment variables:")
        click.echo("  export OPENAI_API_KEY='your-key-here'")
        click.echo("  export GROQ_API_KEY='your-key-here'")
        click.echo("  export GEMINI_API_KEY='your-key-here'")
    except Exception as e:
        click.echo(f"Error creating config: {e}", err=True)


if __name__ == '__main__':
    cli()
