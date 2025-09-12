#!/usr/bin/env python3
"""
MAS Family Inheritance Experiment Runner

Enhanced script to run the experiment with comprehensive console output and logging
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Google API key for CrewAI
google_key = os.getenv('GOOGLE_API_KEY')
if google_key:
    os.environ['GOOGLE_API_KEY'] = google_key
    # Set as OpenAI key for CrewAI compatibility (CrewAI expects this)
    os.environ['OPENAI_API_KEY'] = google_key

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Create output directory structure with model-specific folders
output_dir = "output"

# Note: model_dir will be set later based on command line arguments

# Create timestamped log file (will be updated with month suffix if needed)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = None  # Will be set when we know which month we're running

# Configure logging to output to console only initially
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console output only
    ],
    force=True  # Override any existing logging configuration
)

# Also configure root logger to ensure all messages go to console
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for handler in root_logger.handlers:
    root_logger.removeHandler(handler)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Create logger
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all requirements are met"""
    logger.info("🔍 Checking requirements...")
    
    # Check for Google API key
    logger.info("📋 LLM Provider: Gemini Pro (via Google)")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        logger.error("❌ Error: GOOGLE_API_KEY environment variable not set or invalid")
        logger.error("Please create a .env file with your Google API key:")
        logger.error("GOOGLE_API_KEY=your_google_api_key_here")
        return False
    else:
        logger.info(f"✅ Google API Key found: {api_key[:10]}...")
    
    # Check for required packages
    required_packages = ['crewai', 'langchain', 'pandas', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is missing")
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All required packages are installed")
    logger.info("✅ Using GOOGLE GEMINI as LLM provider")
    return True

def main():
    """Main entry point with enhanced logging"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run MAS Family Inheritance Experiment')
    parser.add_argument('--month', type=int, choices=range(1, 7), 
                       help='Run specific month (1-6). If not specified, runs all months.')
    parser.add_argument('--resume', action='store_true', 
                       help='Resume from the last completed month')
    parser.add_argument('--model-variant', type=str, choices=['base', 'altered'], default='base',
                       help='Model variant to use: base (normal behavior) or altered (with self-interest prompt)')
    parser.add_argument('--self-interest', action='store_true',
                       help='Enable self-interest maximization prompt for agents')
    args = parser.parse_args()
    
    logger.info("🚀 MAS Family Inheritance Experiment")
    logger.info("=" * 60)
    logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("🤖 Using model: gemini-1.5-flash (google)")
    
    # Determine model variant and self-interest settings
    model_variant = args.model_variant
    use_self_interest = args.self_interest
    
    # If self-interest is enabled, automatically set variant to altered
    if use_self_interest and model_variant == "base":
        model_variant = "altered"
    
    # Create model-specific directory structure
    variant_suffix = f"_{model_variant}" if model_variant != "base" else ""
    model_dir = os.path.join(output_dir, f"gemini{variant_suffix}")
    logs_dir = os.path.join(model_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    logger.info(f"📁 Output directory: {model_dir}")
    logger.info(f"📊 Model variant: {model_variant}")
    logger.info(f"🎯 Self-interest prompt: {'Enabled' if use_self_interest else 'Disabled'}")
    
    if args.month:
        logger.info(f"📅 Running Month {args.month} only")
        # Create month-specific log file
        log_file = os.path.join(logs_dir, f"experiment_log_month_{args.month}_{timestamp}.txt")
    elif args.resume:
        logger.info("📅 Resuming from last completed month")
        # Create general log file for resume
        log_file = os.path.join(logs_dir, f"experiment_log_resume_{timestamp}.txt")
    else:
        logger.info("📅 Running all 6 months")
        # Create general log file for full run
        log_file = os.path.join(logs_dir, f"experiment_log_full_{timestamp}.txt")
    
    # Add file handler for the large detailed log
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Display log file location
    logger.info(f"📄 Log file: {log_file}")
    
    if not check_requirements():
        logger.error("❌ Requirements check failed. Exiting.")
        return 1
    
    try:
        # Set Google API key for CrewAI (Gemini model)
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            os.environ['OPENAI_API_KEY'] = google_key
            logger.info("🔑 Set Google API key for CrewAI compatibility (Gemini model)")
        
        logger.info("📦 Importing experiment modules...")
        from experiment.main import FamilyInheritanceExperiment
        
        logger.info(f"🏗️  Creating experiment instance...")
        experiment = FamilyInheritanceExperiment(model_variant=model_variant, use_self_interest_prompt=use_self_interest)
        logger.info("✅ Experiment instance created successfully")
        
        logger.info("⚙️  Setting up crew...")
        experiment.setup_crew()
        logger.info("✅ Crew setup completed")
        
        # Run experiment based on arguments
        if args.month:
            logger.info(f"🚀 Starting Month {args.month} execution...")
            logger.info("-" * 60)
            experiment.run_single_month(args.month)
        elif args.resume:
            logger.info("🚀 Resuming experiment from last completed month...")
            logger.info("-" * 60)
            experiment.run_from_resume()
        else:
            logger.info("🚀 Starting full experiment execution...")
            logger.info("-" * 60)
            experiment.run_full_experiment()
        
        logger.info("-" * 60)
        logger.info("🎉 Experiment completed successfully!")
        logger.info("📊 Check the generated files in the output directory:")
        logger.info(f"   📁 {output_dir}/")
        logger.info(f"   📄 {log_file}")
        logger.info(f"   📊 {output_dir}/results/experiment_results.json")
        logger.info(f"   📊 {output_dir}/results/experiment_data.json")
        logger.info(f"   💾 {output_dir}/state/experiment_state.json")
        logger.info(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}")
        logger.error("Full error details:")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
