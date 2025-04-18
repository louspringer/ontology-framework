import asyncio
import os
import subprocess
from ontology_framework.checkin_manager import CheckinManager, LLMClient
from ontology_framework.patch_management import PatchManager
from ontology_framework.patch import OntologyPatch, Change, PatchType, PatchStatus

def get_1password_secret(item_path):
    try:
        result = subprocess.run(
            ['op', 'read', item_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching secret from 1Password: {e}")
        return None

async def main():
    # Get OpenAI API key from 1Password
    api_key = get_1password_secret('op://Private/OPENAI_API_KEY/api key')
    if not api_key:
        print("Failed to get OpenAI API key from 1Password")
        return

    # Set environment variables
    os.environ['OPENAI_API_KEY'] = api_key
    os.environ['GIT_REPO_PATH'] = os.getcwd()
    os.environ['MODEL_PATH'] = os.path.join(os.getcwd(), 'models', 'checkin_process.ttl')

    # Initialize dependencies
    llm_client = LLMClient(api_key=api_key)
    patch_manager = PatchManager(patch_directory=os.path.join(os.getcwd(), 'patches'))

    # Create a sample patch
    patch = OntologyPatch(
        patch_id="test-patch-1",
        patch_type=PatchType.ADD,
        target_ontology="http://example.org/ontology",
        content="Test patch for checkin manager",
        changes=[
            Change(
                type="add",
                subject="http://example.org/test",
                predicate="http://example.org/hasValue",
                object="test value"
            )
        ]
    )

    # Initialize and run checkin manager
    manager = CheckinManager(
        llm_client=llm_client,
        patch_manager=patch_manager
    )

    try:
        print("Starting checkin process...")
        await manager.checkin(patch)
        print("Checkin completed successfully!")
    except Exception as e:
        print(f"Error during checkin: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 