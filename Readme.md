# Multi-VM Deployment with CI/CD and Monitoring

## Configuration Steps

1. Configure Virtual Machines
    * Create a VM in VirtualBox with the Host-Only network and NAT and Assign an IP address from the network 192.168.123.0/24
        * Change the IP range from vbox config in host machine where virbualbox is installed
            ```bash
            echo "* 192.168.123.0/0" | sudo tee -a /etc/vbox/networks.conf
            ```
            More details: https://www.virtualbox.org/manual/ch06.html#network_hostonly

        * Create a `host-only` network adapter with IPV4 address `192.168.123.1` and Network Mask `255.255.255.0` called `vboxnet0` in virtualbox.

        * Select both Host only and NAT network adapter from VM's network settings
            * Host only: For assigning static IP with specified IP range. VMs and Host will be in the same network
            * NAT: For using Network Address Translation to connect with internet
        
        * **Configure Static IP with Netplan**.

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
            ```bash
            sudo netplan apply
            ```


     * Clone 3 more VMs from the first VM. 
        * Change hostname and machine-id.
            
            ```bash
            sudo hostnamectl set-hostname <new-hostname>

            sudo sed -i 's/^127\.0\.1\.1\s\+.*/127.0.1.1 <new-hostname>/' /etc/hosts
            
            sudo rm /etc/machine-id
            sudo systemd-machine-id-setup
            ```

        * Update Static IP in netplan and Assign each VM an IP address from the network 192.168.123.0/24 similarly.
            ```yaml
            network:
                version: 2
                ethernets:
                enp0s3:
                    addresses:
                    - 192.168.123.102/24
                enp0s8:
                    dhcp4: true
            ```
            ```bash
            sudo netplan apply
            ```


2. **Known Hosts Setup**
    * ssh-keyscan is used to grab the remote host key without connecting interactively and store it in `~/.ssh/known_hosts`.
        ```bash
        ssh-keyscan 192.168.123.101 >> ~/.ssh/known_hosts
        ```
    * Remove old key of remote machine from known_hosts of host machine (If error occurs because of modified fingerprint/key).
        ```
        ssh-keygen -f "~/.ssh/known_hosts" -R "192.168.123.101"
        ```

3. **Setup Passwordless Authentication** so that Ansible can ssh access from host machine to remote machines.
   - Generate SSH Key:
     ```bash
     ssh-keygen -t rsa -b 4096 -C "riyad.omf@gmail.com"
     ```
   - Copy key to each VM:
     ```bash
     ssh-copy-id omar@192.168.123.101
     ```


4. **Setup Ansible** on the 4th VM (reverse proxy) which is also used to ssh into all the webserver's for deployment
   ```bash
   sudo apt update
   sudo apt install ansible -y
   ```

   Ensure Passwordless SSH access similarly from VM4 (nginx reverse proxy) to the 3 webser VMs since it's used for deploying the app in all 3 VMs based on github actions event.

5. **Configure Self-hosted GitHub Runner**
   - [Runner Setup as a Service](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)

---
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
  - Trigger Ansible playbook via self-hosted runner to deploy the image.

### 3. Test Domain Access
Add this to `/etc/hosts` on host machine:
```
192.168.123.104 myapp.com
```

Then open:
```
http://myapp.com
```

---

## Monitoring
- Prometheus scrapes data from the web servers using Node Exporter.
- Grafana dashboards display system metrics from all 3 webserver VMs.
- Accessible from the reverse proxy machine at:
  ```
  http://myapp.com:3000
  ```

## Reverse Proxy Demo

[▶️ Watch the demo](./documentation/multi-vm-deployment.mp4)
