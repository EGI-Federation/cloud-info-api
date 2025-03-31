"""Testing our glue component"""

from app.glue import GlueImage, GlueInstanceType, GlueShare, GlueSite

ops_portal_fixture = {
    "data": [
        {
            "serial": "2",
            "status": "Production",
            "name": "alice",
            "scope": "Global",
            "homeUrl": "https://alice-collaboration.web.cern.ch/",
            "members": "0.0",
            "membersTotal": "3097",
            "Vo": [],
        },
        {
            "serial": "967",
            "status": "Production",
            "name": "vo.epos-eric.eu",
            "scope": "Global",
            "homeUrl": "https://www.epos-eu.org/",
            "members": "0.0",
            "membersTotal": "0.0",
            "Vo": [],
        },
    ]
}


site_fixture = GlueSite(
    name="BIFI",
    hostname="foo",
    gocdb_id="12249G0",
    shares=[
        GlueShare(
            name="Share in service https://colossus.cesar.unizar.es:5000/v3_cloud.compute for VO ops (Project 038db3eeca5c4960a443a89b92373cd2)",
            vo="ops",
            project_id="038db3eeca5c4960a443a89b92373cd2",
            images=[
                GlueImage(
                    id="06c8bfac-0f93-48da-b0eb-4fbad3356f73",
                    name="EGI Small Ubuntu for Monitoring",
                    appdb_id="egi.small.ubuntu.16.04.for.monitoring",
                    mpuri="https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
                    version="2024.11.18",
                )
            ],
            instancetypes=[GlueInstanceType(name="m1.tiny")],
        )
    ],
    url="https://colossus.cesar.unizar.es:5000/v3",
)

site_info_fixture = {
    "CloudComputingService": [
        {
            "CreationTime": "2025-02-18T12:36:34.334839",
            "Validity": 3600,
            "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute",
            "Name": "Cloud Compute service on BIFI",
            "Type": "org.cloud.iaas",
            "QualityLevel": "production",
            "StatusInfo": "http://argo.egi.eu/lavoisier/status_report-sf?site=BIFI",
            "ServiceAUP": "http://go.egi.eu/aup",
            "Complexity": "endpointType=2,share=1",
            "Capability": [
                "executionmanagement.dynamicvmdeploy",
                "security.accounting",
            ],
            "TotalVM": 0,
            "RunningVM": 0,
            "SuspendedVM": 0,
            "HaltedVM": 0,
            "Associations": {"AdminDomain": ["BIFI"]},
            "OtherInfo": {"gocdb_id": "12249G0"},
        }
    ],
    "CloudComputingManager": {
        "CreationTime": "2025-02-18T12:36:34.334839",
        "Validity": 3600,
        "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager",
        "Name": "Cloud Manager for https://colossus.cesar.unizar.es:5000/v3",
        "Associations": {
            "CloudComputingService": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
        },
        "TotalCPUs": 0,
        "TotalRAM": 0,
        "InstanceMaxCPU": 8,
        "InstanceMinCPU": 1,
        "InstanceMaxRAM": 16384,
        "InstanceMinRAM": 512,
        "ManagerFailover": False,
        "ManagerLiveMigration": False,
        "ManagerVMBackupRestore": False,
    },
    "CloudComputingEndpoint": [
        {
            "CreationTime": "2025-02-18T12:36:34.334839",
            "Validity": 3600,
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc",
            "Name": "Cloud computing endpoint for https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc",
            "URL": "https://colossus.cesar.unizar.es:5000/v3",
            "Associations": {
                "CloudComputingService": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
                ]
            },
            "Capability": [],
            "QualityLevel": "production",
            "InterfaceName": "org.openstack.nova",
            "InterfaceVersion": "v3",
            "HealthState": "ok",
            "HealthStateInfo": "Endpoint functioning properly",
            "ServingState": "production",
            "Technology": "webservice",
            "Implementor": "OpenStack Foundation",
            "ImplementationName": "OpenStack Nova",
            "ImplementationVersion": "UNKNOWN",
            "DowntimeInfo": "See the GOC DB for downtimes: https://goc.egi.eu/portal/index.php?Page_Type=Downtimes_Calendar&site=BIFI",
            "Semantics": "https://developer.openstack.org/api-ref/compute",
            "Authentication": "oidc",
            "IssuerCA": "/C=NL/O=GEANT Vereniging/CN=GEANT OV RSA CA 4",
            "TrustedCA": [],
        }
    ],
    "CloudComputingImage": [
        {
            "CreationTime": "2025-02-18T12:36:34.334839",
            "Validity": 3600,
            "ID": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
            "Name": "EGI Image for EGI Small Ubuntu for Monitoring [Ubuntu/20.04/KVM]",
            "Associations": {
                "Share": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_share_ops_038db3eeca5c4960a443a89b92373cd2"
                ],
                "CloudComputingManager": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager",
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
            },
            "MarketPlaceURL": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
            "OSPlatform": "amd64",
            "OSName": "ubuntu",
            "OSVersion": "20.04",
            "Description": "Regular image update",
            "AccessInfo": "none",
            "OtherInfo": {
                "base_mpuri": "https://appdb.egi.eu/store/vm/image/bf991f56-cf3a-4ac9-ad07-b22a54dbead6:8082/"
            },
        }
    ],
    "CloudComputingImageNetwokConfiguration": [],
    "CloudComputingInstanceType": [
        {
            "CreationTime": "2025-02-18T12:36:34.334839",
            "Validity": 3600,
            "ID": "1",
            "Name": "m1.tiny",
            "Associations": {
                "Share": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_share_ops_038db3eeca5c4960a443a89b92373cd2"
                ],
                "CloudComputingManager": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager",
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
            },
            "Platform": "amd64",
            "CPU": 1,
            "RAM": 512,
            "NetworkIn": "UNKNOWN",
            "NetworkOut": True,
            "NetworkInfo": "UNKNOWN",
            "Disk": 1,
        },
    ],
    "CloudComputingVirtualAccelerator": [],
    "AccessPolicy": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_Policy",
            "Name": "Access control rules for ops on https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc",
            "Associations": {
                "CloudComputingEndpoint": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
            },
            "Scheme": "org.glite.standard",
            "PolicyRule": "VO:ops",
        }
    ],
    "MappingPolicy": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_share_ops_038db3eeca5c4960a443a89b92373cd2_Policy",
            "Associations": {
                "Share": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_share_ops_038db3eeca5c4960a443a89b92373cd2",
                "PolicyUserDomain": "ops",
            },
            "Rule": ["VO:ops"],
        }
    ],
    "Share": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_share_ops_038db3eeca5c4960a443a89b92373cd2",
            "Name": "Share in service https://colossus.cesar.unizar.es:5000/v3_cloud.compute for VO ops (Project 038db3eeca5c4960a443a89b92373cd2)",
            "Associations": {
                "CloudComputingService": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
                ],
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
            },
            "Description": "Share in service https://colossus.cesar.unizar.es:5000/v3_cloud.compute for VO ops (Project 038db3eeca5c4960a443a89b92373cd2)",
            "InstanceMaxCPU": 8,
            "InstanceMaxRAM": 16384,
            "SLA": "UNKNOWN",
            "TotalVM": 0,
            "RunningVM": 0,
            "SuspendedVM": 0,
            "HaltedVM": 0,
            "NetworkInfo": "UNKNOWN",
            "DefaultNetworkType": "UNKNOWN",
            "PublicNetworkName": "UNKNOWN",
            "ProjectID": "038db3eeca5c4960a443a89b92373cd2",
            "MaxVM": 10,
            "OtherInfo": {"project_name": "ops", "project_domain_name": "default"},
        }
    ],
}

gocdb_fixture = """
<?xml version="1.0" encoding="UTF-8"?>
<results>
  <SERVICE_ENDPOINT PRIMARY_KEY="7513G0">
    <PRIMARY_KEY>7513G0</PRIMARY_KEY>
    <HOSTNAME>api.cloud.ifca.es</HOSTNAME>
    <GOCDB_PORTAL_URL>https://goc.egi.eu/portal/index.php?Page_Type=Service&amp;id=7513</GOCDB_PORTAL_URL>
    <HOSTDN>/DC=org/DC=terena/DC=tcs/C=ES/ST=Madrid/L=Madrid/O=Consejo Superior de Investigaciones Cientificas/CN=api.cloud.ifca.es</HOSTDN>
    <BETA>N</BETA>
    <SERVICE_TYPE>org.openstack.nova</SERVICE_TYPE>
    <CORE/>
    <IN_PRODUCTION>Y</IN_PRODUCTION>
    <NODE_MONITORED>Y</NODE_MONITORED>
    <NOTIFICATIONS>Y</NOTIFICATIONS>
    <SITENAME>IFCA-LCG2</SITENAME>
    <COUNTRY_NAME>Spain</COUNTRY_NAME>
    <COUNTRY_CODE>ES</COUNTRY_CODE>
    <ROC_NAME>NGI_IBERGRID</ROC_NAME>
    <URL>https://api.cloud.ifca.es:5000/v3/</URL>
    <ENDPOINTS/>
    <SCOPES>
      <SCOPE>EGI</SCOPE>
      <SCOPE>wlcg</SCOPE>
      <SCOPE>tier2</SCOPE>
      <SCOPE>cms</SCOPE>
      <SCOPE>FedCloud</SCOPE>
    </SCOPES>
    <EXTENSIONS/>
  </SERVICE_ENDPOINT>
</results>
"""

appdb_image_fixture = {
    "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/": {
        "imageVAppCName": "egi.small.ubuntu.16.04.for.monitoring",
        "imageVAppName": "EGI Small Ubuntu for Monitoring",
        "version": "2024.11.18",
    }
}
