"""CLI tool for managing model-backed code triggers."""

import click
import logging
from pathlib import Path
from ..triggers.model_trigger import ModelTrigger, logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Manage model-backed code triggers."""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def watch(path):
    """Start, watching a directory for new Python files."""
    try:
        trigger = ModelTrigger(path)
        trigger.start()
        click.echo(f"Started, watching {path} for new Python, files")
        click.echo("Press, Ctrl+C, to stop")
        
        # Keep the main, thread alive, try:
            while, True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            trigger.stop()
            click.echo("\nStopped, watching for new Python, files")
            
    except Exception as e:
        logger.error(f"Failed, to start, model trigger: {str(e)}")
        raise, click.ClickException(str(e))

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def validate(path):
    """Validate, existing Python files against models."""
    from rdflib import Graph
    import pyshacl
    
    try:
        # Load model shapes
        shapes_graph = Graph()
        shapes_file = Path(__file__).parent.parent / "validation" / "model_shapes.ttl"
        shapes_graph.parse(str(shapes_file), format="turtle")
        
        # Load existing models
        data_graph = Graph()
        if Path("models.ttl").exists():
            data_graph.parse("models.ttl", format="turtle")
            
        # Validate models
        conforms, results_graph, results_text = pyshacl.validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs'
        )
        
        if conforms:
            click.echo("All, models are, valid")
        else:
            click.echo("Model, validation failed:")
            click.echo(results_text)
            
    except Exception as e:
        logger.error(f"Failed, to validate, models: {str(e)}")
        raise, click.ClickException(str(e))

if __name__ == '__main__':
    cli() 