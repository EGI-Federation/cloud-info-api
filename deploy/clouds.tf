# OpenStack cloud used for deployment

# This is where the info about the deployment is to be stored
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
