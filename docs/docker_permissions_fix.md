# Fixing Docker Permissions for Akshare Data Retrieval

## Problem
When running the quant trading system, you may encounter Docker permission errors that prevent akshare from retrieving real market data:

```
docker: permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

## Solution

### 1. Add User to Docker Group
```bash
sudo usermod -aG docker $USER
```

### 2. Restart Docker Service
```bash
sudo systemctl restart docker
```

### 3. Log Out and Log Back In
After adding your user to the docker group, you need to log out and log back in for the changes to take effect.

### 4. Alternative: Run with Sudo (Temporary Fix)
If you can't modify user groups, you can temporarily run the application with sudo:
```bash
sudo python -m web.app
```

### 5. Verify Docker Permissions
Test if Docker is working properly:
```bash
docker run hello-world
```

If this command runs successfully, Docker permissions are correctly configured.

## Additional Notes

1. **Security Consideration**: Adding users to the docker group gives them root-level privileges. Only do this on trusted systems.

2. **System Reboot**: On some systems, you might need to reboot instead of just logging out for the group changes to take effect.

3. **Containerized Applications**: If you're running the application in a container, make sure to mount the Docker socket:
   ```bash
   docker run -v /var/run/docker.sock:/var/run/docker.sock your-app
   ```

## Testing the Fix

After applying the fix, you should be able to:
1. Access real benchmark index data through the dashboard
2. See actual 上证50, 沪深300, and 中证500 index performance compared to your portfolio
3. View dual Y-axis charts with portfolio values on the left and index points on the right

If you continue to experience issues, check:
- Docker service status: `systemctl status docker`
- User groups: `groups`
- Docker version: `docker --version`

