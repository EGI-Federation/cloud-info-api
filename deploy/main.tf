resource "openstack_compute_instance_v2" "cloud-info-api" {
  name      = "cloud-info-api"
  image_id  = data.openstack_images_image_v2.egi-docker.id
  flavor_id = var.flavor_id
  user_data = file("cloud-init.yaml")
  network {
    uuid = var.net_id
  }
  security_groups = ["HTTP-cloud-info-api", "motley-cue-cloud-info-api"]
}

resource "openstack_compute_secgroup_v2" "secgroup" {
  name        = "HTTP-cloud-info-api"
  description = "HTTP and HTTPS access"

  rule {
    from_port   = 80
    to_port     = 80
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

  rule {
    from_port   = 443
    to_port     = 443
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }
}

resource "openstack_compute_secgroup_v2" "motley-cloud-info-api" {
  name        = "motley-cue-cloud-info-api"
  description = "Open access via ssh-oidc"

  rule {
    from_port   = 22
    to_port     = 22
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

  rule {
    from_port   = 8181
    to_port     = 8181
    ip_protocol = "tcp"
    cidr        = "0.0.0.0/0"
  }

}

resource "openstack_networking_floatingip_v2" "fip" {
  pool = var.ip_pool
}

resource "openstack_compute_floatingip_associate_v2" "fip" {
  floating_ip = openstack_networking_floatingip_v2.fip.address
  instance_id = openstack_compute_instance_v2.cloud-info-api.id
}

output "public_ip" {
  value = openstack_networking_floatingip_v2.fip.address
}
