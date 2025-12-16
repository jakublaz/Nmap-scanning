import subprocess
import base64
import os

def send_email(sender, recipient, subject, body, attachment_path=None):
    boundary = "=====BOUNDARY====="
    msg = []

    msg.append(f"From: {sender}")
    msg.append(f"To: {recipient}")
    msg.append(f"Subject: {subject}")
    msg.append("MIME-Version: 1.0")

    if attachment_path:
        msg.append(f"Content-Type: multipart/mixed; boundary=\"{boundary}\"")
        msg.append("")
        msg.append(f"--{boundary}")
        msg.append("Content-Type: text/plain; charset=utf-8")
        msg.append("Content-Transfer-Encoding: 7bit")
        msg.append("")
        msg.append(body)

        # Attach file
        with open(attachment_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        filename = os.path.basename(attachment_path)

        msg.append(f"--{boundary}")
        msg.append(f"Content-Type: text/plain; name=\"{filename}\"")
        msg.append("Content-Transfer-Encoding: base64")
        msg.append(f"Content-Disposition: attachment; filename=\"{filename}\"")
        msg.append("")
        msg.append(encoded)
        msg.append(f"--{boundary}--")

    else:
        msg.append("Content-Type: text/plain; charset=utf-8")
        msg.append("")
        msg.append(body)

    # Send
    p = subprocess.Popen(["msmtp", recipient], stdin=subprocess.PIPE)
    p.communicate("\n".join(msg).encode("utf-8"))