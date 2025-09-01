# Email Configuration Setup for SafeNetAi

This guide explains how to configure the email service to use Gmail SMTP for sending OTP verification emails and fraud alerts.

## Prerequisites

1. **Gmail Account**: You need a Gmail account with 2-factor authentication enabled
2. **App Password**: Generate an App Password for your Gmail account (not your regular password)

## Gmail Setup Steps

### 1. Enable 2-Factor Authentication
1. Go to your Google Account settings
2. Navigate to Security → 2-Step Verification
3. Enable 2-Step Verification if not already enabled

### 2. Generate App Password
1. In Security settings, go to "App passwords"
2. Select "Mail" as the app and "Other" as the device
3. Click "Generate"
4. Copy the 16-character password (this is your `EMAIL_HOST_PASSWORD`)

## Environment Configuration

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# Other Django settings
SECRET_KEY=your-secret-key-here
DEBUG=1
DATABASE_URL=sqlite:///db.sqlite3
SITE_BASE_URL=http://localhost:3000
EMAIL_TOKEN_TTL_HOURS=24
```

## Testing the Configuration

Run the test script to verify your email configuration:

```bash
cd backend
python test_email_config.py
```

This will:
- Display your current email settings
- Check if all required variables are configured
- Test the SMTP connection

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Ensure you're using an App Password, not your regular Gmail password
   - Verify 2-factor authentication is enabled
   - Check that the email address is correct

2. **Connection Refused**
   - Verify `EMAIL_PORT=587` for TLS
   - Ensure `EMAIL_USE_TLS=True`
   - Check your firewall/network settings

3. **"Less secure app access" error**
   - This is normal and expected - use App Passwords instead

### Gmail Security Settings

- **Less secure app access**: Keep this OFF
- **2-Step Verification**: Must be ON
- **App Passwords**: Use these for the `EMAIL_HOST_PASSWORD`

## Email Service Features

The updated email service now:

- ✅ Uses Gmail SMTP backend instead of console backend
- ✅ Loads all configuration from environment variables
- ✅ Supports both TLS and SSL connections
- ✅ Includes comprehensive error handling and logging
- ✅ Sends actual emails via Gmail SMTP
- ✅ Maintains the same API for OTP and fraud alert emails

## Security Notes

- Never commit your `.env` file to version control
- Use App Passwords instead of your main Gmail password
- Regularly rotate your App Passwords
- Monitor your Gmail account for unusual activity

## Support

If you encounter issues:
1. Check the logs in `backend/logs/`
2. Run the test script: `python test_email_config.py`
3. Verify your Gmail settings and App Password
4. Check network connectivity to Gmail SMTP servers
