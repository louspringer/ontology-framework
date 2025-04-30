from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD, PROV
import os

# Define custom namespace
BFG = Namespace("./build_process#")

class BuildProcessManager:
    def __init__(self):
        self.graph = Graph()
        self._bind_namespaces()
        self._create_classes()
        self._create_properties()
        self._create_build_process()

    def _bind_namespaces(self):
        self.graph.bind("bfg", BFG)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
        self.graph.bind("prov", PROV)

    def _create_classes(self):
        # Create classes
        self.graph.add((BFG.BuildProcess, RDF.type, OWL.Class))
        self.graph.add((BFG.BuildProcess, RDFS.label, Literal("Azure Build Process", lang="en")))
        self.graph.add((BFG.BuildProcess, RDFS.comment, Literal("Process for building and deploying Azure resources", lang="en")))

        self.graph.add((BFG.ResourceGroup, RDF.type, OWL.Class))
        self.graph.add((BFG.ResourceGroup, RDFS.label, Literal("Azure Resource Group", lang="en")))
        self.graph.add((BFG.ResourceGroup, RDFS.comment, Literal("Container for Azure resources", lang="en")))

        self.graph.add((BFG.VirtualMachine, RDF.type, OWL.Class))
        self.graph.add((BFG.VirtualMachine, RDFS.label, Literal("Azure Virtual Machine", lang="en")))
        self.graph.add((BFG.VirtualMachine, RDFS.comment, Literal("Compute resource in Azure", lang="en")))

        self.graph.add((BFG.ContainerRegistry, RDF.type, OWL.Class))
        self.graph.add((BFG.ContainerRegistry, RDFS.label, Literal("Azure Container Registry", lang="en")))
        self.graph.add((BFG.ContainerRegistry, RDFS.comment, Literal("Private Docker registry in Azure", lang="en")))

        self.graph.add((BFG.NetworkResource, RDF.type, OWL.Class))
        self.graph.add((BFG.NetworkResource, RDFS.label, Literal("Azure Network Resource", lang="en")))
        self.graph.add((BFG.NetworkResource, RDFS.comment, Literal("Networking components in Azure", lang="en")))

        self.graph.add((BFG.BuildStep, RDF.type, OWL.Class))
        self.graph.add((BFG.BuildStep, RDFS.label, Literal("Build Step", lang="en")))
        self.graph.add((BFG.BuildStep, RDFS.comment, Literal("Individual step in the build process", lang="en")))

    def _create_properties(self):
        # Create properties
        self.graph.add((BFG.hasLocation, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasLocation, RDFS.domain, BFG.ResourceGroup))
        self.graph.add((BFG.hasLocation, RDFS.range, XSD.string))
        self.graph.add((BFG.hasLocation, RDFS.label, Literal("Location", lang="en")))
        self.graph.add((BFG.hasLocation, RDFS.comment, Literal("Azure region for the resource", lang="en")))

        self.graph.add((BFG.hasSize, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasSize, RDFS.domain, BFG.VirtualMachine))
        self.graph.add((BFG.hasSize, RDFS.range, XSD.string))
        self.graph.add((BFG.hasSize, RDFS.label, Literal("VM Size", lang="en")))
        self.graph.add((BFG.hasSize, RDFS.comment, Literal("Size specification for the VM", lang="en")))

        self.graph.add((BFG.hasImage, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasImage, RDFS.domain, BFG.VirtualMachine))
        self.graph.add((BFG.hasImage, RDFS.range, XSD.string))
        self.graph.add((BFG.hasImage, RDFS.label, Literal("VM Image", lang="en")))
        self.graph.add((BFG.hasImage, RDFS.comment, Literal("OS image for the VM", lang="en")))

        self.graph.add((BFG.hasPriority, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasPriority, RDFS.domain, BFG.VirtualMachine))
        self.graph.add((BFG.hasPriority, RDFS.range, XSD.string))
        self.graph.add((BFG.hasPriority, RDFS.label, Literal("VM Priority", lang="en")))
        self.graph.add((BFG.hasPriority, RDFS.comment, Literal("Priority setting for the VM", lang="en")))

        self.graph.add((BFG.hasEvictionPolicy, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasEvictionPolicy, RDFS.domain, BFG.VirtualMachine))
        self.graph.add((BFG.hasEvictionPolicy, RDFS.range, XSD.string))
        self.graph.add((BFG.hasEvictionPolicy, RDFS.label, Literal("Eviction Policy", lang="en")))
        self.graph.add((BFG.hasEvictionPolicy, RDFS.comment, Literal("Policy for VM eviction", lang="en")))

        self.graph.add((BFG.hasStepOrder, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasStepOrder, RDFS.domain, BFG.BuildStep))
        self.graph.add((BFG.hasStepOrder, RDFS.range, XSD.integer))
        self.graph.add((BFG.hasStepOrder, RDFS.label, Literal("Step Order", lang="en")))
        self.graph.add((BFG.hasStepOrder, RDFS.comment, Literal("Order of execution for the build step", lang="en")))

        self.graph.add((BFG.hasCommand, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasCommand, RDFS.domain, BFG.BuildStep))
        self.graph.add((BFG.hasCommand, RDFS.range, XSD.string))
        self.graph.add((BFG.hasCommand, RDFS.label, Literal("Command", lang="en")))
        self.graph.add((BFG.hasCommand, RDFS.comment, Literal("Command to execute for this step", lang="en")))

        self.graph.add((BFG.hasAutoConfirm, RDF.type, OWL.DatatypeProperty))
        self.graph.add((BFG.hasAutoConfirm, RDFS.domain, BFG.BuildStep))
        self.graph.add((BFG.hasAutoConfirm, RDFS.range, XSD.boolean))
        self.graph.add((BFG.hasAutoConfirm, RDFS.label, Literal("Auto Confirm", lang="en")))
        self.graph.add((BFG.hasAutoConfirm, RDFS.comment, Literal("Whether the step requires auto-confirmation", lang="en")))

    def _create_build_process(self):
        # Create build process instance
        self.graph.add((BFG.pdfProcessorBuild, RDF.type, BFG.BuildProcess))
        self.graph.add((BFG.pdfProcessorBuild, RDFS.label, Literal("PDF Processor Build", lang="en")))
        self.graph.add((BFG.pdfProcessorBuild, RDFS.comment, Literal("Build process for PDF processor application", lang="en")))

        # Define build steps
        steps = [
            {
                "name": "cleanupStep",
                "order": 1,
                "command": "az group delete --name $RESOURCE_GROUP --yes",
                "auto_confirm": True
            },
            {
                "name": "createResourceGroupStep",
                "order": 2,
                "command": "az group create --name $RESOURCE_GROUP --location $LOCATION",
                "auto_confirm": True
            },
            {
                "name": "createNetworkStep",
                "order": 3,
                "command": "az network vnet create --resource-group $RESOURCE_GROUP --name ${VM_NAME}VNET --address-prefix 10.0.0.0/16 --subnet-name ${VM_NAME}Subnet --subnet-prefix 10.0.0.0/24",
                "auto_confirm": True
            },
            {
                "name": "createNSGStep",
                "order": 4,
                "command": "az network nsg create --resource-group $RESOURCE_GROUP --name ${VM_NAME}NSG",
                "auto_confirm": True
            },
            {
                "name": "createSSHRuleStep",
                "order": 5,
                "command": "az network nsg rule create --resource-group $RESOURCE_GROUP --nsg-name ${VM_NAME}NSG --name AllowSSH --protocol tcp --priority 1000 --destination-port-range 22 --access allow",
                "auto_confirm": True
            },
            {
                "name": "createPublicIPStep",
                "order": 6,
                "command": "az network public-ip create --resource-group $RESOURCE_GROUP --name ${VM_NAME}PublicIP --sku Standard --version IPv4",
                "auto_confirm": True
            },
            {
                "name": "createVMStep",
                "order": 7,
                "command": "az vm create --resource-group $RESOURCE_GROUP --name $VM_NAME --image $VM_IMAGE --size $VM_SIZE --admin-username $ADMIN_USERNAME --ssh-key-values ~/.ssh/pdf-processor-vm_key.pub --priority Spot --eviction-policy Deallocate --public-ip-address ${VM_NAME}PublicIP --vnet-name ${VM_NAME}VNET --subnet ${VM_NAME}Subnet --nsg ${VM_NAME}NSG",
                "auto_confirm": True
            },
            {
                "name": "createACRStep",
                "order": 8,
                "command": "az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic",
                "auto_confirm": True
            },
            {
                "name": "installDockerStep",
                "order": 9,
                "command": "ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP 'sudo apt-get update && sudo apt-get install -y docker.io'",
                "auto_confirm": True
            },
            {
                "name": "setupAppStep",
                "order": 10,
                "command": "ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP 'mkdir -p /app'",
                "auto_confirm": True
            },
            {
                "name": "copyFilesStep",
                "order": 11,
                "command": "scp -i ~/.ssh/pdf-processor-vm_key -r ./* $ADMIN_USERNAME@$VM_IP:/app/",
                "auto_confirm": True
            },
            {
                "name": "loginACRStep",
                "order": 12,
                "command": "ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP 'docker login $ACR_NAME.azurecr.io -u $ACR_USERNAME -p $ACR_PASSWORD'",
                "auto_confirm": True
            },
            {
                "name": "buildPushImageStep",
                "order": 13,
                "command": "ssh -i ~/.ssh/pdf-processor-vm_key $ADMIN_USERNAME@$VM_IP 'cd /app && docker build -t $ACR_NAME.azurecr.io/pdf-processor:latest . && docker push $ACR_NAME.azurecr.io/pdf-processor:latest'",
                "auto_confirm": True
            }
        ]

        for step in steps:
            step_uri = BFG[step["name"]]
            self.graph.add((step_uri, RDF.type, BFG.BuildStep))
            self.graph.add((step_uri, BFG.hasStepOrder, Literal(step["order"], datatype=XSD.integer)))
            self.graph.add((step_uri, BFG.hasCommand, Literal(step["command"])))
            self.graph.add((step_uri, BFG.hasAutoConfirm, Literal(step["auto_confirm"], datatype=XSD.boolean)))

    def save(self, filename="build_process.ttl"):
        self.graph.serialize(destination=filename, format="turtle")

    def load(self, filename="build_process.ttl"):
        if os.path.exists(filename):
            self.graph.parse(filename, format="turtle")

    def get_steps(self):
        query = """
        SELECT ?step ?order ?command ?auto_confirm
        WHERE {
            ?step a bfg:BuildStep .
            ?step bfg:hasStepOrder ?order .
            ?step bfg:hasCommand ?command .
            ?step bfg:hasAutoConfirm ?auto_confirm .
        }
        ORDER BY ?order
        """
        results = self.graph.query(query, initNs={"bfg": BFG})
        return [(str(row.step), int(row.order), str(row.command), bool(row.auto_confirm)) for row in results]

if __name__ == "__main__":
    manager = BuildProcessManager()
    manager.save() 