# Selenium server

This server can be used to run selenium tests.

## Example Usage

See [test.py](test.py)

## Connect to a session

Access the web-ui at https://USERNAME:PASSWORD@selenium.dataforchange.org.il/ui

Click on the camera icon to connect to a session, the password is `secret`.

## Delete a Session

If a Session is "stuck" you can delete it using the following command:

```
curl -XDELETE 'https://USERNAME:PASSWORD@selenium.dataforchange.org.il/session/SESSION_ID'
```

To prevent this from happening, make sure to always call `driver.quit()`.
