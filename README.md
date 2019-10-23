# Distributer Android and iOS internally

## What

Very basic service to store mobile applications for testing.

If you are a lone developer this is unlikely to serve any purpose. On the
other hand, if you need to distribute your applications across a reasonably
large team it may be very helpful.

## Installation

```
pip install --user git+https://github.com/grilo/nativeapps.git
nativeapps
```

Point your browser to the service's IP address and port (default: 10000).

You may now deploy your applications (IPA and APK supported) by using the REST
API or using the built-in form.

```
curl -X PUT -T "/path/to/file.ipa" "http://localhost:1000/application"
```

Connect to the service with your mobile phone (iOS, for example) and click the
apple icon. Assuming your provisioning profile is valid for that specific
device, it should start installing and you can now test it.
