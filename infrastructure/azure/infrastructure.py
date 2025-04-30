from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SH
import uuid
from datetime import datetime

def create_infrastructure_ontology():
    # Create a new graph
    g = Graph()
    
    # Define namespaces
    INF = Namespace("http://example.org/infrastructure#")
    AZURE = Namespace("http://example.org/azure#")
    GUIDANCE = Namespace("https://raw.githubusercontent.com/louspringer/ontology-framework/main/guidance#")
    META = Namespace("http://example.org/meta#")
    METAMETA = Namespace("http://example.org/metameta#")
    PROBLEM = Namespace("http://example.org/problem#")
    SOLUTION = Namespace("http://example.org/solution#")
    CONVERSATION = Namespace("http://example.org/conversation#")
    PROCESS = Namespace("http://example.org/process#")
    AGENT = Namespace("http://example.org/agent#")
    TIME = Namespace("http://example.org/time#")
    DCT = Namespace("http://purl.org/dc/terms/")
    
    # Bind namespaces
    g.bind("inf", INF)
    g.bind("azure", AZURE)
    g.bind("guidance", GUIDANCE)
    g.bind("meta", META)
    g.bind("metameta", METAMETA)
    g.bind("problem", PROBLEM)
    g.bind("solution", SOLUTION)
    g.bind("conversation", CONVERSATION)
    g.bind("process", PROCESS)
    g.bind("agent", AGENT)
    g.bind("time", TIME)
    g.bind("dct", DCT)
    g.bind("sh", SH)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    
    # Add ontology metadata
    g.add((INF[''], RDF.type, OWL.Ontology))
    g.add((INF[''], RDFS.label, Literal("Infrastructure Ontology")))
    g.add((INF[''], RDFS.comment, Literal("Ontology for Azure infrastructure resources and configurations")))
    g.add((INF[''], OWL.versionInfo, Literal("1.0.0")))
    g.add((INF[''], DCT.created, Literal(datetime.now().isoformat())))
    g.add((INF[''], DCT.creator, Literal("Ontology Framework")))
    
    # TODO section for future refinements
    g.add((INF['TODO'], RDF.type, OWL.AnnotationProperty))
    g.add((INF['TODO'], RDFS.label, Literal("Future Refinements")))
    g.add((INF['TODO'], RDFS.comment, Literal("""
    1. Add more detailed SHACL validation rules
    2. Implement cost estimation properties
    3. Add support for additional Azure services
    4. Enhance security rule validation
    """)))
    
    # Define classes
    classes = [
        (INF.VirtualMachine, "Virtual Machine", "Azure virtual machine instance"),
        (INF.VirtualNetwork, "Virtual Network", "Azure virtual network"),
        (INF.AutoShutdown, "Auto Shutdown", "Azure auto shutdown configuration"),
        (INF.SpotInstance, "Spot Instance", "Azure spot instance configuration"),
        (INF.NetworkInterface, "Network Interface", "Azure network interface"),
        (INF.NetworkSecurityGroup, "Network Security Group", "Azure network security group"),
        (INF.PublicIPAddress, "Public IP Address", "Azure public IP address"),
        (INF.SecurityRule, "Security Rule", "Azure network security rule"),
        (INF.Subnet, "Subnet", "Azure virtual network subnet"),
        (INF.OSProfile, "OS Profile", "Operating system profile configuration"),
        (INF.StorageProfile, "Storage Profile", "Storage configuration"),
        (INF.SSHConfiguration, "SSH Configuration", "SSH access configuration"),
        (INF.DNSSettings, "DNS Settings", "DNS configuration")
    ]
    
    for cls, label, comment in classes:
        g.add((cls, RDF.type, OWL.Class))
        g.add((cls, RDFS.label, Literal(label)))
        g.add((cls, RDFS.comment, Literal(comment)))
        g.add((cls, OWL.versionInfo, Literal("1.0.0")))
    
    # Define properties
    properties = [
        # Object properties
        (INF.hasAutoShutdown, "has auto shutdown", "The auto shutdown configuration of the VM", OWL.ObjectProperty, INF.VirtualMachine, INF.AutoShutdown),
        (INF.hasSpotInstance, "has spot instance", "The spot instance configuration of the VM", OWL.ObjectProperty, INF.VirtualMachine, INF.SpotInstance),
        (INF.hasNetworkInterface, "has network interface", "The network interface of the VM", OWL.ObjectProperty, INF.VirtualMachine, INF.NetworkInterface),
        (INF.hasNetworkSecurityGroup, "has network security group", "The network security group of the subnet", OWL.ObjectProperty, INF.Subnet, INF.NetworkSecurityGroup),
        (INF.hasPublicIP, "has public IP", "The public IP address of the network interface", OWL.ObjectProperty, INF.NetworkInterface, INF.PublicIPAddress),
        (INF.hasSecurityRule, "has security rule", "The security rule of the network security group", OWL.ObjectProperty, INF.NetworkSecurityGroup, INF.SecurityRule),
        (INF.hasSubnet, "has subnet", "The subnet of the network interface", OWL.ObjectProperty, INF.NetworkInterface, INF.Subnet),
        (INF.hasOSProfile, "has OS profile", "The operating system profile of the VM", OWL.ObjectProperty, INF.VirtualMachine, INF.OSProfile),
        (INF.hasStorageProfile, "has storage profile", "The storage profile of the VM", OWL.ObjectProperty, INF.VirtualMachine, INF.StorageProfile),
        (INF.hasSSHConfiguration, "has SSH configuration", "The SSH configuration of the VM", OWL.ObjectProperty, INF.OSProfile, INF.SSHConfiguration),
        (INF.hasDNSSettings, "has DNS settings", "The DNS settings of the public IP", OWL.ObjectProperty, INF.PublicIPAddress, INF.DNSSettings),
        
        # Datatype properties
        (INF.hasName, "has name", "The name of the resource", OWL.DatatypeProperty, None, XSD.string),
        (INF.hasLocation, "has location", "The Azure region location", OWL.DatatypeProperty, None, XSD.string),
        (INF.hasSize, "has size", "The VM size specification", OWL.DatatypeProperty, INF.VirtualMachine, XSD.string),
        (INF.hasIPAddress, "has IP address", "The IP address of the resource", OWL.DatatypeProperty, [INF.NetworkInterface, INF.PublicIPAddress], XSD.string),
        (INF.hasShutdownTime, "has shutdown time", "The auto shutdown time", OWL.DatatypeProperty, INF.AutoShutdown, XSD.time),
        (INF.hasNotificationTime, "has notification time", "The notification time before shutdown", OWL.DatatypeProperty, INF.AutoShutdown, XSD.integer),
        (INF.hasPriority, "has priority", "The priority of the rule", OWL.DatatypeProperty, INF.SecurityRule, XSD.integer),
        (INF.hasProtocol, "has protocol", "The network protocol", OWL.DatatypeProperty, INF.SecurityRule, XSD.string),
        (INF.hasPort, "has port", "The network port number", OWL.DatatypeProperty, INF.SecurityRule, XSD.integer),
        (INF.hasAdminUsername, "has admin username", "The admin username for the VM", OWL.DatatypeProperty, INF.OSProfile, XSD.string),
        (INF.hasSSHPublicKey, "has SSH public key", "The SSH public key for the VM", OWL.DatatypeProperty, INF.SSHConfiguration, XSD.string),
        (INF.hasOSPublisher, "has OS publisher", "The publisher of the OS image", OWL.DatatypeProperty, INF.StorageProfile, XSD.string),
        (INF.hasOSOffer, "has OS offer", "The offer of the OS image", OWL.DatatypeProperty, INF.StorageProfile, XSD.string),
        (INF.hasOSSku, "has OS SKU", "The SKU of the OS image", OWL.DatatypeProperty, INF.StorageProfile, XSD.string),
        (INF.hasOSVersion, "has OS version", "The version of the OS image", OWL.DatatypeProperty, INF.StorageProfile, XSD.string),
        (INF.hasStorageType, "has storage type", "The type of storage", OWL.DatatypeProperty, INF.StorageProfile, XSD.string),
        (INF.hasDomainNameLabel, "has domain name label", "The domain name label for DNS", OWL.DatatypeProperty, INF.DNSSettings, XSD.string),
        (INF.hasFQDN, "has FQDN", "The fully qualified domain name", OWL.DatatypeProperty, INF.DNSSettings, XSD.string),
        (INF.hasAddressPrefix, "has address prefix", "The address prefix for the subnet", OWL.DatatypeProperty, INF.Subnet, XSD.string),
        (INF.hasAddressSpace, "has address space", "The address space for the virtual network", OWL.DatatypeProperty, INF.VirtualNetwork, XSD.string)
    ]
    
    for prop, label, comment, prop_type, domain, range_ in properties:
        g.add((prop, RDF.type, prop_type))
        g.add((prop, RDFS.label, Literal(label)))
        g.add((prop, RDFS.comment, Literal(comment)))
        if domain:
            if isinstance(domain, list):
                for d in domain:
                    g.add((prop, RDFS.domain, d))
            else:
                g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_))
    
    # Create SHACL shapes for each class
    for cls, label, comment in classes:
        shape = INF[f"{label.replace(' ', '')}Shape"]
        g.add((shape, RDF.type, SH.NodeShape))
        g.add((shape, SH.targetClass, cls))
        g.add((shape, RDFS.label, Literal(f"Validation shape for {label}")))
        
        # Add property constraints based on class
        if cls == INF.VirtualMachine:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.NetworkInterface:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.NetworkSecurityGroup:
            g.add((shape, SH.property, BNode()))
        elif cls == INF.PublicIPAddress:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.Subnet:
            g.add((shape, SH.property, BNode()))
        elif cls == INF.SecurityRule:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.AutoShutdown:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.SpotInstance:
            g.add((shape, SH.property, BNode()))
        elif cls == INF.OSProfile:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.StorageProfile:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
        elif cls == INF.SSHConfiguration:
            g.add((shape, SH.property, BNode()))
        elif cls == INF.DNSSettings:
            g.add((shape, SH.property, BNode()))
            g.add((shape, SH.property, BNode()))
    
    # Create instances
    vm = INF[f"vm-{uuid.uuid4()}"]
    g.add((vm, RDF.type, INF.VirtualMachine))
    g.add((vm, INF.hasName, Literal("cursor-ide-vm")))
    g.add((vm, INF.hasLocation, Literal("eastus")))
    g.add((vm, INF.hasSize, Literal("Standard_D8s_v3")))
    
    nic = INF[f"nic-{uuid.uuid4()}"]
    g.add((nic, RDF.type, INF.NetworkInterface))
    g.add((nic, INF.hasName, Literal("cursor-ide-nic")))
    g.add((nic, INF.hasIPAddress, Literal("10.0.0.4")))
    
    nsg = INF[f"nsg-{uuid.uuid4()}"]
    g.add((nsg, RDF.type, INF.NetworkSecurityGroup))
    g.add((nsg, INF.hasName, Literal("cursor-ide-nsg")))
    
    ip = INF[f"ip-{uuid.uuid4()}"]
    g.add((ip, RDF.type, INF.PublicIPAddress))
    g.add((ip, INF.hasName, Literal("cursor-ide-ip")))
    g.add((ip, INF.hasIPAddress, Literal("20.0.0.1")))
    
    subnet = INF[f"subnet-{uuid.uuid4()}"]
    g.add((subnet, RDF.type, INF.Subnet))
    g.add((subnet, INF.hasName, Literal("cursor-ide-subnet")))
    g.add((subnet, INF.hasAddressPrefix, Literal("10.0.0.0/24")))
    
    vnet = INF[f"vnet-{uuid.uuid4()}"]
    g.add((vnet, RDF.type, INF.VirtualNetwork))
    g.add((vnet, INF.hasName, Literal("cursor-ide-vnet")))
    g.add((vnet, INF.hasAddressSpace, Literal("10.0.0.0/16")))
    
    rule = INF[f"rule-{uuid.uuid4()}"]
    g.add((rule, RDF.type, INF.SecurityRule))
    g.add((rule, INF.hasName, Literal("SSH-Custom")))
    g.add((rule, INF.hasPriority, Literal(1000)))
    g.add((rule, INF.hasProtocol, Literal("Tcp")))
    g.add((rule, INF.hasPort, Literal(22222)))
    
    shutdown = INF[f"shutdown-{uuid.uuid4()}"]
    g.add((shutdown, RDF.type, INF.AutoShutdown))
    g.add((shutdown, INF.hasShutdownTime, Literal("17:00:00", datatype=XSD.time)))
    g.add((shutdown, INF.hasNotificationTime, Literal(30)))
    
    spot = INF[f"spot-{uuid.uuid4()}"]
    g.add((spot, RDF.type, INF.SpotInstance))
    g.add((spot, INF.hasName, Literal("cursor-ide-spot")))
    
    os_profile = INF[f"osprofile-{uuid.uuid4()}"]
    g.add((os_profile, RDF.type, INF.OSProfile))
    g.add((os_profile, INF.hasAdminUsername, Literal("lou")))
    
    ssh_config = INF[f"sshconfig-{uuid.uuid4()}"]
    g.add((ssh_config, RDF.type, INF.SSHConfiguration))
    g.add((ssh_config, INF.hasSSHPublicKey, Literal("REPLACE_WITH_GENERATED_SSH_PUBLIC_KEY")))
    
    storage_profile = INF[f"storageprofile-{uuid.uuid4()}"]
    g.add((storage_profile, RDF.type, INF.StorageProfile))
    g.add((storage_profile, INF.hasOSPublisher, Literal("Canonical")))
    g.add((storage_profile, INF.hasOSOffer, Literal("UbuntuServer")))
    g.add((storage_profile, INF.hasOSSku, Literal("18.04-LTS")))
    g.add((storage_profile, INF.hasOSVersion, Literal("latest")))
    g.add((storage_profile, INF.hasStorageType, Literal("Premium_LRS")))
    
    dns_settings = INF[f"dnssettings-{uuid.uuid4()}"]
    g.add((dns_settings, RDF.type, INF.DNSSettings))
    g.add((dns_settings, INF.hasDomainNameLabel, Literal("cursor-ide")))
    g.add((dns_settings, INF.hasFQDN, Literal("cursor-ide.eastus.cloudapp.azure.com")))
    
    # Add relationships between instances
    g.add((vm, INF.hasNetworkInterface, nic))
    g.add((vm, INF.hasAutoShutdown, shutdown))
    g.add((vm, INF.hasSpotInstance, spot))
    g.add((vm, INF.hasOSProfile, os_profile))
    g.add((vm, INF.hasStorageProfile, storage_profile))
    g.add((nic, INF.hasPublicIP, ip))
    g.add((nic, INF.hasSubnet, subnet))
    g.add((subnet, INF.hasNetworkSecurityGroup, nsg))
    g.add((nsg, INF.hasSecurityRule, rule))
    g.add((os_profile, INF.hasSSHConfiguration, ssh_config))
    g.add((ip, INF.hasDNSSettings, dns_settings))
    
    # Add guidance relationships
    for cls, label, comment in classes:
        g.add((cls, GUIDANCE.hasValidationRule, INF[f"{label.replace(' ', '')}Shape"]))
    
    # Serialize the graph
    g.serialize(destination="infrastructure.ttl", format="turtle")

if __name__ == "__main__":
    create_infrastructure_ontology() 