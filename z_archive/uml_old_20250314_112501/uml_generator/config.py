from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import logging


@dataclass
class Configuration:
    """Configuration for the UML generator."""
    # Input/output settings
    source_dir: Path
    output_dir: Path
    single_file: Optional[Path] = None
    input_extension: str = ".py"
    output_format: str = "plantuml"
    
    # Processing options
    subdirs: List[str] = field(default_factory=lambda: ["models", "services"])
    recursive: bool = False
    list_only: bool = False
    show_imports: bool = False
    generate_report: bool = False
    
    # PlantUML specific settings
    plantuml_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default settings and ensure directories exist."""
        # Ensure paths are Path objects
        if isinstance(self.source_dir, str):
            self.source_dir = Path(self.source_dir)
        
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        
        if self.single_file and isinstance(self.single_file, str):
            self.single_file = Path(self.single_file)
        
        # Set default PlantUML settings if not provided
        if not self.plantuml_settings:
            self.plantuml_settings = {
                'PLANTUML_START': "@startuml",
                'PLANTUML_END': "@enduml",
                'PLANTUML_SETTINGS': [
                    "skinparam classAttributeIconSize 0",
                ],
                'show_imports': self.show_imports,
            }
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)


def create_config_from_args(args) -> Configuration:
    """Create configuration from command line arguments."""
    # Determine source directory
    if hasattr(args, 'file') and args.file:
        source_dir = Path(args.file).parent
        single_file = Path(args.file)
    elif hasattr(args, 'directory') and args.directory:
        source_dir = Path(args.directory)
        single_file = None
    elif hasattr(args, 'app_dir') and args.app_dir:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent
        source_dir = project_root / "app"
        single_file = None
    else:
        raise ValueError("No source directory or file specified")
    
    # Create configuration
    config = Configuration(
        source_dir=source_dir,
        output_dir=Path(args.output),
        single_file=single_file,
        subdirs=args.subdirs if hasattr(args, 'subdirs') else None,
        recursive=args.recursive if hasattr(args, 'recursive') else False,
        list_only=args.list_only if hasattr(args, 'list_only') else False,
        show_imports=args.show_imports if hasattr(args, 'show_imports') else False,
        generate_report=args.generate_report if hasattr(args, 'generate_report') else False,
    )
    
    return config


def configure_logging(args) -> logging.Logger:
    """Configure logging based on command line arguments."""
    logger = logging.getLogger("uml_generator")
    
    # Configure handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set log level based on verbosity
    if hasattr(args, 'debug') and args.debug:
        logger.setLevel(logging.DEBUG)
    elif hasattr(args, 'verbose') and args.verbose:
        logger.setLevel(logging.INFO)
    elif hasattr(args, 'quiet') and args.quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)
    
    return logger
