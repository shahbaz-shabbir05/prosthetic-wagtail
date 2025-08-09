variable "elb_priority" {
  type        = number
  description = "ELB rule priority"
}

variable "hostname" {
  type        = string
  description = "ELB hostname"
}

variable "content_hostname" {
  type        = string
  description = "Hostname for static content CDN"
}
