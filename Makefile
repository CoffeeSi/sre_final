
compose_up:
	docker compose up -d --build

compose_down:
	docker compose down

swarm_init:
	docker swarm init

swarm_deploy:
	docker compose build
	docker stack deploy -c docker-compose.yaml sre_stack

swarm_remove:
	docker stack rm sre_stack

terraform_init:
	cd terraform && terraform init

terraform_plan:
	cd terraform && terraform plan

terraform_apply:
	@cd terraform && terraform apply -auto-approve
	@powershell -NoProfile -Command "$$ip = terraform -chdir=terraform output -raw instance_public_ip; $$line = $$ip + ' ansible_user=ubuntu ansible_ssh_private_key_file=~/assignment-key.pem'; @('[aws_servers]', $$line) | Set-Content -Encoding ASCII ansible/inventory.ini"
	
terraform_destroy:
	cd terraform && terraform destroy -auto-approve

ansible_deploy:
	cd ansible && wsl -d Ubuntu -- cp ./assignment-key.pem ~/assignment-key.pem
	wsl -d Ubuntu -- chmod 600 ~/assignment-key.pem
	cd ansible && wsl -d Ubuntu -- ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.ini playbook.yml
