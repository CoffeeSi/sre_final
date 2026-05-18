# outputs.tf
output "instance_public_ip" {
  description = "Public IP address of the instance"
  value       = aws_instance.endterm_instance.public_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.endterm_instance.id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.main_sg.id
}

output "deployment_info" {
  description = "Deployment information and access URLs"
  value = {
    frontend      = "http://${aws_instance.endterm_instance.public_ip}"
    api_gateway   = "http://${aws_instance.endterm_instance.public_ip}:8080"
    grafana       = "http://${aws_instance.endterm_instance.public_ip}:3000"
    prometheus    = "http://${aws_instance.endterm_instance.public_ip}:9090"
    auth_service  = "http://${aws_instance.endterm_instance.public_ip}:8000"
    ssh_command   = "ssh -i ~/assignment-key.pem ubuntu@${aws_instance.endterm_instance.public_ip}"
  }
}