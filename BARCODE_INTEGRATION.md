# Barcode Integration Guide 📱

Complete guide for integrating QR code barcode scanning with Ace Check-in.

## Overview

The Ace Check-in system supports barcode scanning through QR codes. Since most barcode scanners can only perform GET requests (by following links), we've optimized the API with dedicated GET endpoints for barcode scanning.

## Key Endpoints for Barcode Scanning

### Entry Check-in (GET)

**URL Format:**
```
GET /api/entry/checkin/{member_id}
GET /api/entry/checkin/{member_id}?notes={notes}
```

**Examples:**
```
https://yourdomain.com/api/entry/checkin/M001
https://yourdomain.com/api/entry/checkin/M001?notes=Court+A
https://yourdomain.com/api/entry/checkin/M001?notes=Morning+session
```

### Payment Recording (GET)

**URL Format:**
```
GET /api/payment/checkin/{member_id}?amount={amount}
GET /api/payment/checkin/{member_id}?amount={amount}&notes={notes}
```

**Examples:**
```
https://yourdomain.com/api/payment/checkin/M001?amount=25.50
https://yourdomain.com/api/payment/checkin/M001?amount=25.50&notes=Monthly+fee
https://yourdomain.com/api/payment/checkin/M001?amount=100&notes=Court+rental
```

## QR Code Generation

### Using Python

```python
import qrcode

# Generate entry QR code
entry_url = "https://yourdomain.com/api/entry/checkin/M001?notes=Court+A"
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(entry_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("entry_qr_M001.png")

# Generate payment QR code
payment_url = "https://yourdomain.com/api/payment/checkin/M001?amount=25.50"
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(payment_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("payment_qr_M001.png")
```

### Using Online Tools

- [QR Code Generator](https://www.qr-code-generator.com/)
- [QR Code Monkey](https://www.qrcode-monkey.com/)
- [ZXing Demo](http://zxing.org/w/decode.jspx)

Just paste the URL in the "Content" field and generate the QR code.

## How It Works

1. **Create QR Code** - Generate QR code with entry/payment URL
2. **Print/Display** - Print on court sign or display on tablet
3. **Member Scans** - Member scans QR with their phone
4. **Browser Opens** - Phone opens the URL
5. **Instant Log** - Entry/payment is automatically logged
6. **Success Response** - Member sees confirmation with timestamp

## Setup Examples

### Example 1: Court Entry QR Code

Create a QR code that logs court entry:
```
https://yourdomain.com/api/entry/checkin/M001?notes=Court+1
```

Place this QR code at the court entrance. When a member scans it, their entry is automatically logged.

### Example 2: Payment Collection QR Code

Create a QR code for payment collection:
```
https://yourdomain.com/api/payment/checkin/M001?amount=50&notes=Court+rental
```

Display this when collecting payment. Scanning logs the payment immediately.

### Example 3: Dynamic QR Codes Per Session

For recurring sessions with fixed amounts:
```
Morning Session Entry:
https://yourdomain.com/api/entry/checkin/{member_id}?notes=Morning+session

Evening Session Payment:
https://yourdomain.com/api/payment/checkin/{member_id}?amount=25&notes=Evening+court
```

Replace `{member_id}` with actual member IDs.

## Response Format

When a barcode is scanned, the member receives a JSON response:

**Entry Response:**
```json
{
  "id": 1,
  "member_id": "M001",
  "timestamp": "2024-01-15T10:45:30",
  "notes": "Court A"
}
```

**Payment Response:**
```json
{
  "id": 1,
  "member_id": "M001",
  "amount": 2550,
  "timestamp": "2024-01-15T11:00:00",
  "notes": "Monthly fee"
}
```

## Hardware Setup

### Option 1: Mobile Device (Recommended)

**Equipment:**
- Tablet or smartphone
- Stand or wall mount
- QR code printed or displayed

**Setup:**
1. Install barcode scanner app (e.g., Barcode Scanner, QR Code Scanner)
2. Point at QR code
3. App opens the URL automatically
4. Entry/payment is logged

### Option 2: Dedicated Barcode Scanner

**Equipment:**
- USB barcode scanner
- Computer/tablet
- Display showing QR codes

**Setup:**
1. Scanner configured to append URL
2. Computer displays QR codes
3. Scanner reads code
4. URL is sent to browser automatically

### Option 3: iPad/Tablet at Court

**Equipment:**
- iPad or Android tablet
- Wall mount
- QR codes printed on paper or displayed on screen

**Setup:**
1. Open Safari/Chrome browser
2. Create bookmarks for QR codes
3. Tap bookmark to scan entry/payment
4. Instant logging

## Integration with Management System

### Generate QR Codes for All Members

```python
import qrcode
from your_app import get_all_members  # Your member list

members = get_all_members()

for member in members:
    # Entry QR Code
    entry_url = f"https://yourdomain.com/api/entry/checkin/{member.member_id}"
    qr = qrcode.QRCode(version=1, box_size=10)
    qr.add_data(entry_url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(f"entry_{member.member_id}.png")

    # Payment QR Code (example amount)
    payment_url = f"https://yourdomain.com/api/payment/checkin/{member.member_id}?amount=25.50"
    qr = qrcode.QRCode(version=1, box_size=10)
    qr.add_data(payment_url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(f"payment_{member.member_id}.png")
```

## Best Practices

### URL Encoding
- Spaces → `+` or `%20`
- Special characters → URL encode
- Example: "Court A" → "Court+A" or "Court%20A"

### QR Code Placement
- **Court Entry:** Place at court entrance
- **Payment:** Display on tablet at reception
- **Check-in:** At check-in desk
- **Multiple courts:** One QR per court with court name

### Member Communication
- Provide printed QR codes to members
- Display on court wall or entrance
- Include instructions: "Scan QR code to log entry"
- Test before deployment

### Testing
1. Generate test QR code
2. Scan with phone camera or barcode app
3. Verify member entry/payment is logged
4. Check API response
5. Confirm timestamp is correct

## Troubleshooting

### QR Code Won't Scan
- Ensure QR code is clearly printed/displayed
- Try different lighting conditions
- Clean scanner lens
- Test with phone camera app

### Entry/Payment Not Logging
- Check member_id exists in system
- Verify URL is correct
- Check network connectivity
- Review API response for errors

### Response Shows as Text
- Barcode scanner needs to open browser
- Configure scanner to append to URL
- Test with different scanner app
- Check if URL is valid

## API Alternatives

### If You Need POST (for applications/integrations)

Entry:
```bash
curl -X POST https://yourdomain.com/api/entry \
  -H "Content-Type: application/json" \
  -d '{"member_id":"M001","notes":"Court A"}'
```

Payment:
```bash
curl -X POST https://yourdomain.com/api/payment \
  -H "Content-Type: application/json" \
  -d '{"member_id":"M001","amount":25.50,"notes":"Monthly fee"}'
```

## Security Considerations

⚠️ **Important:** Since GET URLs are logged in browser history and server logs:

1. **Use HTTPS** - Always use HTTPS for production
2. **No Sensitive Data** - Don't include sensitive info in URLs
3. **Monitor Access** - Review server logs for suspicious access
4. **Rate Limit** - Consider rate limiting for barcode endpoints
5. **Audit Trail** - All actions are logged with timestamps

## QR Code Standards

- **Version:** 1-3 (for short URLs)
- **Error Correction:** M or H level
- **Size:** Print at least 1x1 inch for reliable scanning
- **Contrast:** High contrast (black on white)

## Examples with Real Data

### Example 1: Simple Entry

**URL:**
```
https://yourtennis.com/api/entry/checkin/ALICE_001
```

**When scanned:**
- Alice's entry is logged
- Timestamp is recorded
- JSON response shown

### Example 2: Payment with Amount

**URL:**
```
https://yourtennis.com/api/payment/checkin/BOB_002?amount=30&notes=Monthly+membership
```

**When scanned:**
- Bob's payment is recorded
- Amount: $30.00
- Notes: "Monthly membership"
- Timestamp: automatic

## Advanced: Multiple Court Setup

Create per-court QR codes:

```
Court 1 Entry:
https://yourdomain.com/api/entry/checkin/{member_id}?notes=Court+1

Court 2 Entry:
https://yourdomain.com/api/entry/checkin/{member_id}?notes=Court+2

Court 3 Entry:
https://yourdomain.com/api/entry/checkin/{member_id}?notes=Court+3
```

Print and place at each court.

## FAQ

**Q: Can I use the same QR code for multiple members?**
A: No, each member needs their own QR code. The member_id is embedded in the URL.

**Q: What happens if someone scans the wrong QR code?**
A: It logs the entry/payment for the member whose QR code was scanned. Ensure QR codes are clearly labeled.

**Q: Can I change the URL after creating the QR code?**
A: No, the URL is embedded in the QR code. You'll need to generate a new QR code.

**Q: Do I need internet for barcode scanning to work?**
A: Yes, the phone must have internet connectivity to reach your server.

**Q: How do I verify it's working?**
A: Check the API response and verify the entry/payment appears in the dashboard/database.

---

## Support

For questions or issues with barcode integration:
1. Check QUICKSTART.md
2. Review API_EXAMPLES.md
3. Check README.md Barcode Integration section
4. Test with curl to debug

---

**Ready to set up barcode scanning? Get started with the examples above!** 🎾
