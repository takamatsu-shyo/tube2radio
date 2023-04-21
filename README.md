# tube2radio
A test project with ChatGPT-4: Convert Tube radio to a sound file, then send it to a cloud storage to save on mobile costs.

# How to setup in short
1. Create a virtualenv
2. Install libraries
3. Set up your YouTube API and add values to the JSON file under `/cfg`
4. Add your target channel ids to the JSON file
5. Set up your Dropbox API and add values to the JSON file under `/cfg`
6. Set up `systemd` for 

# Details for the setup
## 5. Dropbox API, "refresh-token"
https://www.dropboxforum.com/t5/Dropbox-API-Support-Feedback/Get-refresh-token-from-access-token/td-p/596739

## 6. systemd
Create a service file `sample-tube-monitor.service` in `/etc/systemd/system`

```
[Unit]
Description=YouTube Channel Monitor
After=network.target

[Service]
Type=simple
User=your_user
Group=your_group
WorkingDirectory=/path/to/working_directory
ExecStart=/path/to/venv/bin/python /path/to/your_script/download.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

