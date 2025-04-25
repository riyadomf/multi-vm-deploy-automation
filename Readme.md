# Multi-VM Deployment with CI/CD and Monitoring

[Problem Description](./documentation/DevOps_Problem1.pdf)

## Virtual Machines

- **VM1, VM2, VM3**: Web App Servers
- **VM4**: Reverse Proxy + Monitoring + CI/CD Runner

## Configuration Steps

1. **Configure Virtual Machines**
    * Create a VM in VirtualBox with the Host-Only network and NAT and assign an IP from `192.168.123.0/24`.
        * Update VirtualBox config to allow the specified range:
            ```bash
            echo "* 192.168.123.0/0" | sudo tee -a /etc/vbox/networks.conf
            ```
            More details: https://www.virtualbox.org/manual/ch06.html#network_hostonly

        * Create a `host-only` network adapter `vboxnet0` with IP `192.168.123.1` and mask `255.255.255.0`.

        * Select both Host only and NAT network adapter from VM's network settings
            * Host only: For assigning static IP with specified IP range. VMs and Host will be in the same network
            * NAT: For using Network Address Translation to access internet
        
        * Configure Static IP with Netplan

            Example: /etc/netplan/*.yaml
            ```yaml
            network:
                version: 2
                ethernets:
                enp0s3:  # Host-only network
                    addresses:
                    - 192.168.123.101/24
                enp0s8:  # NAT (default gateway & DNS)
                    dhcp4: true
            ```

            Apply the changes with
            ```bash
            sudo netplan apply
            ```


    * Clone 3 more VMs from the first VM and Configure: 
        * Update hostname and machine-id.
            
            ```bash
            sudo hostnamectl set-hostname <new-hostname>

            sudo sed -i 's/^127\.0\.1\.1\s\+.*/127.0.1.1 <new-hostname>/' /etc/hosts
            
            sudo rm /etc/machine-id
            sudo systemd-machine-id-setup
            ```

        * Update IP in netplan for each VM (e.g., 192.168.123.102, 103, 104).

2. **Known Hosts Setup**
    * ssh-keyscan is used to grab the remote host key without connecting interactively and store it in `~/.ssh/known_hosts`.
        ```bash
        ssh-keyscan 192.168.123.101 >> ~/.ssh/known_hosts
        ```
    * Remove old key of remote machine from known_hosts of host machine (If error occurs because of modified fingerprint/key).
        ```
        ssh-keygen -f "~/.ssh/known_hosts" -R "192.168.123.101"
        ```

3. **Passwordless SSH Authentication** so that Ansible can ssh from host machine to remote machines programmatically.
   - Generate SSH Key:
     ```bash
     ssh-keygen -t rsa -b 4096 -C "riyad.omf@gmail.com"
     ```
   - Copy public key to each VM:
     ```bash
     ssh-copy-id omar@192.168.123.101
     ```


4. **Install Ansible on VM4 (Reverse Proxy)**
   ```bash
   sudo apt update
   sudo apt install ansible -y
   ```

   Ensure passwordless SSH to VM1-3 from VM4 since VM4 is used for deploying the app in all 3 VMs based on github actions event.

5. **Configure Self-hosted GitHub Runner on VM4**
   - [Runner Setup as a Service](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)


## How to Run

### 1. Run the Ansible Playbook
Run this on host machine:
```bash
ansible-playbook -i ./ansible/inventory ./ansible/playbooks/configure_servers.yml --ask-become-pass
```
This will configure Docker, nginx reverse proxy, prometheus, grafana, and node exporter in remote machines.

### 2. Trigger CI/CD from GitHub
- Push to the `deployment` branch.
- GitHub Actions will:
  - Build and push the Docker image.
  - Trigger Ansible playbook via self-hosted runner (VM4) to deploy the image.

### 3. Access App via Domain
Update `/etc/hosts` on **host machine**:
```
192.168.123.104 myapp.com
```

Then access:
```
http://myapp.com
```


## Monitoring
- **Prometheus** scrapes data from Node Exporter on each web server.
- **Grafana** visualitzes system metrics
- Access Grafana
  ```
  http://myapp.com:3000
  ```

## Reverse Proxy Demo

[▶️ Watch the demo](./documentation/multi-vm-deployment.mp4)
