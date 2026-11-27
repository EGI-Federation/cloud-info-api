# OpenStack cloud used for deployment
terraform {
  backend "swift" {
    container = "terraform-cloud-api"
    cloud     = "backend"
  }
}

# The provider where the deployment is actually performed
provider "openstack" {
  cloud = "deploy"
}
