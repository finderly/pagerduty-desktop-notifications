### Pagerduty Desktop Notifications

This script is displaying desktop notifications for alerts assigned to a specific username.

### Linux with systemd

Clone repo
```git clone git@github.com:finderly/pagerduty-desktop-notifications.git```

Copy the unit file in systemd folder
```cp /path/to/repo/pd-notifier.unit /etc/systemd/system/pd-notifier.service```

Reload systemd units
```systemctl daemon-reload```

Start process
```systemctl start pd-notifier```
