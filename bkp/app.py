from flask import Flask, render_template, request
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

app = Flask(__name__)

# Dictionary mapping workload names to Azure resource types
workload_services = {
    'web_app': 'Microsoft.Web/sites',
    'database': 'Microsoft.Sql/servers',
    'storage': 'Microsoft.Storage/storageAccounts',
    'aks': 'Microsoft.ContainerService/managedClusters',
    'snet': 'Microsoft.Network/virtualNetworks/subnets',
    'vnet': 'Microsoft.Network/virtualNetworks',
    'sql': 'Microsoft.Sql/servers',
    # Add more workload-service mappings as needed
}

@app.route('/', methods=['GET', 'POST'])
def select_service():
    subscription_id = None
    selected_workload = None  # Initialize selected_workload variable
    resources = []  # Initialize resources variable

    if request.method == 'POST':
        subscription_id = request.form.get('subscription_id')
        selected_workload = request.form.getlist('workload')  # Get list of selected workloads
        resource_types = [workload_services.get(workload) for workload in selected_workload]
        if subscription_id and resource_types:
            credential = DefaultAzureCredential()
            resource_client = ResourceManagementClient(credential, subscription_id)
            for resource_type in resource_types:
                resources.extend(resource_client.resources.list(filter=f"resourceType eq '{resource_type}'"))

    if resources:
        resource_list = []
        for resource in resources:
            resource_group = resource.id.split('/')[4]
            resource_properties = resource.properties
            resource_provisioning_state = resource_properties.provisioning_state if resource_properties else None
            resource_sku = resource.sku.name if resource.sku else None
            resource_created_time = resource_properties.created_at if resource_properties else None
            resource_updated_time = resource_properties.updated_at if resource_properties else None

            resource_list.append([
                resource.name,
                resource.type,
                resource.location,
                resource.id,
                resource_group,
                subscription_id,
                resource.tags,
                resource_provisioning_state,
                resource_sku,
                resource_created_time,
                resource_updated_time
            ])

        if resource_list:
            return render_template('result.html', resources=resource_list, selected_workloads=selected_workload)
        else:
            return render_template('result.html', error='No Azure resources found for the specified workload')
    else:
        return render_template('index.html', error=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
