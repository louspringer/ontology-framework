import os
import subprocess
from build_process_manager import BuildProcessManager
import logging

logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG level
logger = logging.getLogger(__name__)

class BuildExecutor:
    def __init__(self):
        logger.debug("Initializing BuildExecutor")
        self.manager = BuildProcessManager()
        self.manager.load()
        self.env_vars = {
            "RESOURCE_GROUP": "pdf-processor-rg",
            "LOCATION": "eastasia",
            "VM_NAME": "pdf-processor-vm",
            "VM_SIZE": "Standard_D2_v2",
            "VM_IMAGE": "Canonical:0001-com-ubuntu-server-jammy:22_04-lts:latest",
            "ADMIN_USERNAME": "azureuser",
            "ACR_NAME": "pdfprocessor1234"
        }
        logger.debug(f"Environment variables: {self.env_vars}")

    def _expand_command(self, command):
        """Expand environment variables in the command."""
        logger.debug(f"Expanding command: {command}")
        # Replace $VAR and ${VAR} with their values
        for var, value in self.env_vars.items():
            command = command.replace(f"${var}", value)
            command = command.replace(f"${{{var}}}", value)
        logger.debug(f"Expanded command: {command}")
        return command

    def _execute_command(self, command, auto_confirm=True):
        """Execute a command with optional auto-confirmation."""
        expanded_command = self._expand_command(command)
        logger.info(f"Executing: {expanded_command}")
        
        try:
            if auto_confirm:
                # Only add --yes to specific commands that support it
                if "az group delete" in expanded_command and " --yes" not in expanded_command:
                    expanded_command += " --yes"
                elif "apt-get" in expanded_command and " -y" not in expanded_command:
                    expanded_command = expanded_command.replace("apt-get", "apt-get -y")
            
            logger.debug(f"Final command to execute: {expanded_command}")
            result = subprocess.run(
                expanded_command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Command output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            # Handle specific error cases
            if "az group delete" in expanded_command and "ResourceGroupNotFound" in str(e.stderr):
                logger.info("Resource group not found, continuing with creation")
                return True
            logger.error(f"Command failed: {e.stderr}")
            return False

    def execute_build(self):
        """Execute all build steps in order."""
        logger.debug("Starting build execution")
        steps = self.manager.get_steps()
        logger.debug(f"Found {len(steps)} steps to execute")
        for step_uri, order, command, auto_confirm in steps:
            logger.info(f"Executing step {order}: {step_uri}")
            if not self._execute_command(command, auto_confirm):
                logger.error(f"Build failed at step {order}")
                return False
        logger.info("Build completed successfully")
        return True

    def get_acr_credentials(self):
        """Get ACR credentials and update environment variables."""
        logger.debug("Getting ACR credentials")
        try:
            result = subprocess.run(
                f"az acr credential show --name {self.env_vars['ACR_NAME']}",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            # Parse the JSON output to get username and password
            import json
            creds = json.loads(result.stdout)
            self.env_vars["ACR_USERNAME"] = creds["username"]
            self.env_vars["ACR_PASSWORD"] = creds["passwords"][0]["value"]
            logger.debug("Successfully retrieved ACR credentials")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get ACR credentials: {e.stderr}")
            return False

    def get_vm_ip(self):
        """Get VM IP address and update environment variables."""
        logger.debug("Getting VM IP address")
        try:
            result = subprocess.run(
                f"az vm show -d -g {self.env_vars['RESOURCE_GROUP']} -n {self.env_vars['VM_NAME']} --query publicIps -o tsv",
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            self.env_vars["VM_IP"] = result.stdout.strip()
            logger.debug(f"VM IP address: {self.env_vars['VM_IP']}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get VM IP: {e.stderr}")
            return False

if __name__ == "__main__":
    logger.debug("Starting build process")
    executor = BuildExecutor()
    
    # Execute the build process
    if executor.execute_build():
        # Get ACR credentials after ACR is created
        if executor.get_acr_credentials():
            # Get VM IP after VM is created
            if executor.get_vm_ip():
                # Execute remaining steps
                executor.execute_build()
            else:
                logger.error("Failed to get VM IP")
        else:
            logger.error("Failed to get ACR credentials")
    else:
        logger.error("Build process failed") 