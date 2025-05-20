"""Testing our glue component"""

# flake8: noqa

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
            name="ops - 038db3eeca5c4960a443a89b92373cd2 share",
            vo="ops",
            project_id="038db3eeca5c4960a443a89b92373cd2",
            images=[
                GlueImage(
                    id="06c8bfac-0f93-48da-b0eb-4fbad3356f73",
                    name="EGI Small Ubuntu for Monitoring",
                    appdb_id="egi.small.ubuntu.16.04.for.monitoring",
                    mpuri="https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
                    version="2024.11.18",
                    vo="ops",
                )
            ],
            instancetypes=[GlueInstanceType(name="m1.tiny")],
        )
    ],
    url="https://colossus.cesar.unizar.es:5000/v3",
)

another_site_fixture = GlueSite(
    name="FAKE",
    hostname="bar",
    gocdb_id="16649G0",
    shares=[
        GlueShare(
            name="Share in service https://example.com/v3_cloud.compute for VO access (Project X)",
            vo="access",
            project_id="foobar",
            images=[
                GlueImage(
                    id="06c8bfac-0f93-48da-b03b-8f8ad3356f73",
                    name="EGI Fake Image",
                    appdb_id="egi.fake.id",
                    mpuri="https://appdb.egi.eu/store/vo/image/0123:456/",
                    version="0.01",
                    vo="access",
                )
            ],
            instancetypes=[GlueInstanceType(name="m1.small")],
        )
    ],
    url="https://example.com/v3",
)

site_info_fixture = {
    "CloudComputingService": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Name": "Cloud Compute service at BIFI",
            "OtherInfo": {"gocdb_id": "12249G0", "site_name": "BIFI"},
            "Associations": {"AdminDomain": ["BIFI"]},
            "Type": "org.cloud.iaas",
            "QualityLevel": "production",
            "StatusInfo": "https://argo.egi.eu/egi/report-status/Critical/SITES/BIFI",
            "ServiceAUP": "http://go.egi.eu/aup",
            "Complexity": "endpointType=1,share=1",
            "Capability": [
                "executionmanagement.dynamicvmdeploy",
                "security.accounting",
            ],
            "TotalVM": 0,
            "RunningVM": 0,
            "SuspendedVM": 0,
            "HaltedVM": 0,
        }
    ],
    "CloudComputingManager": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Associations": {
                "CloudComputingService": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
                ]
            },
            "InstanceMaxCPU": 16,
            "InstanceMinCPU": 0,
            "InstanceMaxRAM": 16384,
            "InstanceMinRAM": 0,
        }
    ],
    "CloudComputingEndpoint": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Name": "Cloud computing endpoint for https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc",
            "Associations": {
                "CloudComputingService": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
                ]
            },
            "Capability": [],
            "QualityLevel": "production",
            "InterfaceName": "org.openstack.nova",
            "InterfaceVersion": "2.0",
            "HealthState": "ok",
            "HealthStateInfo": "Endpoint funtioning properly",
            "ServingState": "production",
            "Technology": "webservice",
            "Implementor": "OpenStack Foundation",
            "ImplementationName": "OpenStack Nova",
            "ImplementationVersion": "2.96",
            "DowntimeInfo": "https://goc.egi.eu/portal/index.php?Page_Type=Downtimes_Calendar&site=BIFI",
            "Semantics": "https://developer.openstack.org/api-ref/compute",
            "Authentication": "oidc",
            "IssuerCA": "/C=NL/O=GEANT Vereniging/CN=GEANT OV RSA CA 4",
            "TrustedCA": [],
            "URL": "https://colossus.cesar.unizar.es:5000/v3",
        }
    ],
    "CloudComputingImage": [
        {
            "ID": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Name": "EGI Image for EGI Small Ubuntu for Monitoring [Ubuntu/20.04/KVM]",
            "OtherInfo": {
                "base_mpuri": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
            },
            "Associations": {
                "Share": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_share_ops_038db3eeca5c4960a443a89b92373cd2"
                ],
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
                "CloudComputingManager": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager"
                ],
            },
            "MarketplaceURL": "https://appdb.egi.eu/store/vo/image/63fcad1c-b737-5091-9668-1342b6d4f84c:15705/",
            "OSPlatform": "x86_64",
            "OSName": "ubuntu",
            "OSVersion": "20.04",
            "Description": "Regular image update",
            "AccessInfo": "none",
        }
    ],
    "CloudComputingInstanceType": [
        {
            "ID": "1",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Name": "m1.tiny",
            "Associations": {
                "Share": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_share_ops_038db3eeca5c4960a443a89b92373cd2"
                ],
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
                "CloudComputingManager": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute_manager"
                ],
            },
            "Platform": "amd64",
            "CPU": 1,
            "RAM": 512,
            "Disk": 1,
            "NetworkIn": "UNKNOWN",
            "NetworkOut": True,
        },
    ],
    "Share": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_share_ops_038db3eeca5c4960a443a89b92373cd2",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Name": "ops - 038db3eeca5c4960a443a89b92373cd2 share",
            "OtherInfo": {
                "project_name": "ops",
                "project_domain_name": "default",
                "quotas": {
                    "instances": 10,
                    "cores": 20,
                    "ram": 51200,
                    "floating_ips": -1,
                    "fixed_ips": -1,
                    "metadata_items": 128,
                    "injected_files": 5,
                    "injected_file_content_bytes": 10240,
                    "injected_file_path_bytes": 255,
                    "key_pairs": 100,
                    "security_groups": -1,
                    "security_group_rules": -1,
                    "server_groups": 10,
                    "server_group_members": 10,
                },
            },
            "Associations": {
                "CloudComputingService": [
                    "https://colossus.cesar.unizar.es:5000/v3_cloud.compute"
                ],
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ],
            },
            "InstanceMaxCPU": 16,
            "InstanceMaxRAM": 16384,
            "TotalVM": 0,
            "RunningVM": 0,
            "SuspendedVM": 0,
            "HaltedVM": 0,
            "MaxVM": 10,
            "ProjectID": "038db3eeca5c4960a443a89b92373cd2",
        }
    ],
    "MappingPolicy": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_share_ops_038db3eeca5c4960a443a89b92373cd2_Policy",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Associations": {
                "Share": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_share_ops_038db3eeca5c4960a443a89b92373cd2"
                ],
                "PolicyUserDomain": ["ops"],
            },
            "Rule": ["VO:ops"],
            "Scheme": "org.glite.standard",
        }
    ],
    "AccessPolicy": [
        {
            "ID": "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc_policy",
            "Validity": 3600,
            "CreationTime": "2025-05-08T15:07:06.423857",
            "Associations": {
                "CloudComputingEndpoint": [
                    "https://colossus.cesar.unizar.es:5000/v3_OpenStack_v3_oidc"
                ]
            },
            "Rule": ["VO:ops"],
            "Scheme": "org.glite.standard",
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

images_fixture = [
    {
        "appdb_id": "egi.small.ubuntu.16.04.for.monitoring",
        "endpoint": "https://colossus.cesar.unizar.es:5000/v3",
        "id": "06c8bfac-0f93-48da-b0eb-4fbad3356f73",
        "mpuri": (
            "https://appdb.egi.eu/store/vo/image/"
            "63fcad1c-b737-5091-9668-1342b6d4f84c:15705/"
        ),
        "name": "EGI Small Ubuntu for Monitoring",
        "version": "2024.11.18",
        "vo": "ops",
    },
    {
        "appdb_id": "egi.fake.id",
        "endpoint": "https://example.com/v3",
        "id": "06c8bfac-0f93-48da-b03b-8f8ad3356f73",
        "mpuri": "https://appdb.egi.eu/store/vo/image/0123:456/",
        "name": "EGI Fake Image",
        "version": "0.01",
        "vo": "access",
    },
]
