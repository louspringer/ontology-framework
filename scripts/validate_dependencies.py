import yaml
import toml
import subprocess
from pathlib import Path


def parse_environment_yml():
    """Parse environment.yml and return a set of package names."""
    env_file = Path("environment.yml")
    if not env_file.exists():
        raise FileNotFoundError("environment.yml not found")

    with open(env_file) as f:
        env_data = yaml.safe_load(f)

    dependencies = set()
    for dep in env_data.get("dependencies", []):
        if isinstance(dep, str):
            dependencies.add(dep.split("=")[0].replace("-", "_").lower())
        elif isinstance(dep, dict) and "pip" in dep:
            for pip_dep in dep["pip"]:
                dependencies.add(pip_dep.split("=")[0].replace("-", "_").lower())

    return dependencies


def parse_pyproject_toml():
    """Parse pyproject.toml and return a set of package names."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        raise FileNotFoundError("pyproject.toml not found")

    with open(pyproject_file) as f:
        pyproject_data = toml.load(f)

    dependencies = set()
    project_deps = pyproject_data.get("project", {}).get("dependencies", [])
    optional_deps = pyproject_data.get("project", {}).get("optional-dependencies", {}).get("dev", [])

    for dep in project_deps + optional_deps:
        dependencies.add(dep.split("=")[0].replace("-", "_").lower())

    return dependencies


def get_installed_packages():
    """Get a set of installed package names from pip and conda."""
    pip_list = subprocess.check_output(["pip", "list", "--format=freeze"]).decode().splitlines()
    conda_list = subprocess.check_output(["conda", "list", "--export"]).decode().splitlines()

    installed_packages = set()
    for line in pip_list + conda_list:
        if "=" in line:
            installed_packages.add(line.split("=")[0].replace("-", "_").lower())

    return installed_packages


def compare_dependencies():
    """Compare declared and installed dependencies."""
    env_deps = parse_environment_yml()
    pyproject_deps = parse_pyproject_toml()
    installed_packages = get_installed_packages()

    declared_deps = env_deps.union(pyproject_deps)

    not_installed = declared_deps - installed_packages
    not_declared = installed_packages - declared_deps

    if not_installed:
        print("Declared but not installed:")
        for dep in not_installed:
            print(f"- {dep}")

    if not_declared:
        print("Installed but not declared:")
        for dep in not_declared:
            print(f"- {dep}")

    if not not_installed and not not_declared:
        print("All dependencies are consistent!")


if __name__ == "__main__":
    compare_dependencies() 