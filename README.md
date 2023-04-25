# tube2radio
A test project with ChatGPT-4: Convert Tube radio to a sound file, then send into a cloud storage to save on mobile costs.


# Prerequisites
- Your favourite YouTube radio station :)
- A Linux server
- YouTube API Key
- Dropbox access token

# How to set up in a nutshell
1. Create a virtualenv
2. Install the libraries
3. Set up your YouTube API and add values to the JSON file under `/cfg`
4. Add your target channel ids to the JSON file
5. Set up your Dropbox API and add values to the JSON file under `/cfg`
6. Set up `systemd` for the download and upload scripts. You will need two services.

# Details for the setup
## 2. Install
Please use `requirements.txt`

## 5. Dropbox API, "refresh-token"
Here are the instructions on how to get the "refresh-token"


https://www.dropboxforum.com/t5/Dropbox-API-Support-Feedback/Get-refresh-token-from-access-token/td-p/596739

## 6. systemd
1. Create a service file `sample-tube-monitor.service` in `/etc/systemd/system`

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

2. Reload the systemd daemon to recognize the new services
3. Enable the service to start on boot
4. Start the service
5. Check the services' status

```
# 2
sudo systemctl daemon-reload

# 3
sudo systemctl enable sample-tube-monitor.service

# 4
sudo systemctl start sample-tube-monitor.service

# 5
sudo systemctl status sample-tube-monitor.service
```

NB! You need one more service for uploading to Dropbox

# Contributing

If you would like to contribute to the project, please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request
