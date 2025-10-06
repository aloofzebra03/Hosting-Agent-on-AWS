"""
Main application entry point for the joke generation agent.
"""

import logging
import argparse
import sys
from typing import Optional
from src.config import config
from src.graph import joke_workflow


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('joke_agent.log')
        ]
    )


def generate_joke_interactive():
    """Interactive mode for generating jokes."""
    print("🎭 Welcome to the Joke Generation Agent!")
    print("Type 'quit' to exit\n")
    
    while True:
        topic = input("Enter a topic for the joke: ").strip()
        
        if topic.lower() in ['quit', 'exit', 'q']:
            print("Goodbye! 👋")
            break
        
        if not topic:
            print("Please enter a valid topic.\n")
            continue
        
        try:
            print(f"\n🤔 Generating joke about '{topic}'...")
            result = joke_workflow.invoke(topic, thread_id="interactive")
            
            print(f"\n😄 **Joke:** {result['joke']}")
            print(f"\n💡 **Explanation:** {result['explanation']}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Error generating joke: {str(e)}")
        
        print()


def generate_joke_batch(topics: list, output_file: Optional[str] = None):
    """Batch mode for generating jokes for multiple topics."""
    results = []
    
    for i, topic in enumerate(topics, 1):
        try:
            print(f"Processing {i}/{len(topics)}: {topic}")
            result = joke_workflow.invoke(topic, thread_id=f"batch_{i}")
            results.append({
                'topic': topic,
                'joke': result['joke'],
                'explanation': result['explanation']
            })
        except Exception as e:
            print(f"Error processing '{topic}': {str(e)}")
            results.append({
                'topic': topic,
                'joke': f"Error: {str(e)}",
                'explanation': "N/A"
            })
    
    # Output results
    if output_file:
        import json
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    else:
        for result in results:
            print(f"\nTopic: {result['topic']}")
            print(f"Joke: {result['joke']}")
            print(f"Explanation: {result['explanation']}")
            print("-" * 80)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Joke Generation Agent - AI-powered joke creation and explanation"
    )
    parser.add_argument(
        '--mode', 
        choices=['interactive', 'batch', 'single'], 
        default='interactive',
        help='Operation mode (default: interactive)'
    )
    parser.add_argument(
        '--topic', 
        type=str,
        help='Topic for joke generation (required for single mode)'
    )
    parser.add_argument(
        '--topics', 
        nargs='+',
        help='Multiple topics for batch mode'
    )
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file for batch mode results (JSON format)'
    )
    parser.add_argument(
        '--thread-id', 
        type=str, 
        default='main',
        help='Thread ID for session management'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Override config with command line arguments
    if args.debug:
        config.debug = True
        config.log_level = "DEBUG"
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration
        config.validate()
        logger.info("Configuration validated successfully")
        
        # Run based on mode
        if args.mode == 'interactive':
            generate_joke_interactive()
            
        elif args.mode == 'single':
            if not args.topic:
                print("Error: --topic is required for single mode")
                sys.exit(1)
            
            print(f"Generating joke for topic: {args.topic}")
            result = joke_workflow.invoke(args.topic, thread_id=args.thread_id)
            
            print(f"\n😄 **Joke:** {result['joke']}")
            print(f"\n💡 **Explanation:** {result['explanation']}")
            
        elif args.mode == 'batch':
            if not args.topics:
                print("Error: --topics is required for batch mode")
                sys.exit(1)
            
            generate_joke_batch(args.topics, args.output)
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
