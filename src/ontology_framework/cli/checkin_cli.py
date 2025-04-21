"""
CLI interface for the check-in manager.
"""

import click
from ontology_framework.modules.checkin_manager import CheckinManager
from pathlib import Path

@click.group()
def cli():
    """Check-in management CLI."""
    pass

@cli.command()
@click.argument('plan_id')
def create(plan_id):
    """Create a new check-in plan."""
    manager = CheckinManager()
    plan_uri = manager.create_checkin_plan(plan_id)
    manager.save_plan(f"{plan_id}.ttl")
    click.echo(f"Created check-in plan: {plan_id}")

@cli.command()
@click.argument('plan_file')
def load(plan_file):
    """Load an existing check-in plan."""
    manager = CheckinManager()
    manager.load_plan(plan_file)
    click.echo(f"Loaded check-in plan: {plan_file}")

@cli.command()
@click.argument('plan_file')
def status(plan_file):
    """Show the status of a check-in plan."""
    manager = CheckinManager()
    manager.load_plan(plan_file)
    
    plan_uri = next(manager.graph.subjects(
        predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        object="http://example.org/checkin#CheckinPlan"
    ))
    
    click.echo(f"Status for plan: {plan_file}")
    for step in manager.graph.objects(plan_uri, "http://example.org/checkin#hasStep"):
        step_name = manager.graph.value(step, "http://www.w3.org/2000/01/rdf-schema#label")
        step_status = manager.get_step_status(step)
        click.echo(f"{step_name}: {step_status}")

@cli.command()
@click.argument('plan_file')
def execute(plan_file):
    """Execute the next pending step in a check-in plan."""
    manager = CheckinManager()
    manager.load_plan(plan_file)
    
    plan_uri = next(manager.graph.subjects(
        predicate="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        object="http://example.org/checkin#CheckinPlan"
    ))
    
    next_step = manager.get_next_step(plan_uri)
    if next_step:
        click.echo(f"Executing step: {manager.graph.value(next_step, 'http://www.w3.org/2000/01/rdf-schema#label')}")
        manager.execute_step(next_step)
        manager.save_plan(plan_file)
        click.echo("Step completed successfully")
    else:
        click.echo("No pending steps to execute")

if __name__ == '__main__':
    cli() 