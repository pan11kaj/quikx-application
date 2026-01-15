import qrcode

data = "https://example.com"

img = qrcode.make(data)
img.save("qr.png")
