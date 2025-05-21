param virtualMachines_baldo_devbox_name string = 'baldo-devbox'
param disks_baldo_devbox_OsDisk_1_98f1bb79be27493fb21cbe29dc1d47cf_externalid string = '/subscriptions/dae16755-7832-4e6d-bae2-c49ff833042f/resourceGroups/BALDO-DEVBOX-RG/providers/Microsoft.Compute/disks/baldo-devbox_OsDisk_1_98f1bb79be27493fb21cbe29dc1d47cf'
param networkInterfaces_baldo_devboxVMNic_externalid string = '/subscriptions/dae16755-7832-4e6d-bae2-c49ff833042f/resourceGroups/BALDO-DEVBOX-RG/providers/Microsoft.Network/networkInterfaces/baldo-devboxVMNic'

resource virtualMachines_baldo_devbox_name_resource 'Microsoft.Compute/virtualMachines@2024-11-01' = {
  name: virtualMachines_baldo_devbox_name
  location: 'westus'
  properties: {
    hardwareProfile: {
      vmSize: 'Standard_D4s_v3'
    }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        osType: 'Linux'
        name: '${virtualMachines_baldo_devbox_name}_OsDisk_1_98f1bb79be27493fb21cbe29dc1d47cf'
        createOption: 'FromImage'
        caching: 'ReadWrite'
        managedDisk: {
          id: disks_baldo_devbox_OsDisk_1_98f1bb79be27493fb21cbe29dc1d47cf_externalid
        }
        deleteOption: 'Detach'
      }
      dataDisks: []
      diskControllerType: 'SCSI'
    }
    osProfile: {
      computerName: virtualMachines_baldo_devbox_name
      adminUsername: 'lou'
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/lou/.ssh/authorized_keys'
              keyData: 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJlhANX/daB1uTlsPeRPDKRSnVHnlUX8Bf6m6r+e0mHE lou@pico.local'
            }
          ]
        }
        provisionVMAgent: true
        patchSettings: {
          patchMode: 'ImageDefault'
          assessmentMode: 'AutomaticByPlatform'
        }
      }
      secrets: []
      allowExtensionOperations: true
      requireGuestProvisionSignal: true
    }
    securityProfile: {
      uefiSettings: {
        secureBootEnabled: true
        vTpmEnabled: true
      }
      securityType: 'TrustedLaunch'
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: networkInterfaces_baldo_devboxVMNic_externalid
        }
      ]
    }
    priority: 'Spot'
    evictionPolicy: 'Deallocate'
    billingProfile: {
      maxPrice: json('-1')
    }
  }
}
