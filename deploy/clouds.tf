# OpenStack cloud used for deployment

# This is where the info about the deployment is to be stored
terraform {
  backend "swift" {
    container = "terraform-dashboard"
    cloud     = "backend"
  }

  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.48"
    }
  }
}

# The provider where the deployment is actually performed
provider "openstack" {
  cloud = "deploy"
}
