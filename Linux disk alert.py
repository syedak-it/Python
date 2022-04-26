import os
import socket
from collections import namedtuple
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

disk_ntuple = namedtuple('partition',  'device mountpoint fstype')
usage_ntuple = namedtuple('usage',  'total used free percent')

def disk_partitions(all=False):
    phydevs = []
    f = open("/proc/filesystems", "r")
    for line in f:
        if not line.startswith("nodev"):
            phydevs.append(line.strip())

    retlist = []
    f = open('/etc/mtab', "r")
    for line in f:
        if not all and line.startswith('none'):
            continue
        fields = line.split()
        device = fields[0]
        mountpoint = fields[1]
        fstype = fields[2]
        if not all and fstype not in phydevs:
            continue
        if device == 'none':
            device = ''
        if '/dev/' in device:
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
    return retlist

def disk_usage(path):
    """Return disk usage associated with path."""
    st = os.statvfs(path)
    free = round((st.f_bavail * st.f_frsize)/1024/1024/1024,2)
    total = round((st.f_blocks * st.f_frsize)/1024/1024/1024,0)
    used = round((st.f_blocks - st.f_bfree) * st.f_frsize/1024/1024/1024,2)
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    return usage_ntuple(total, used, free, round(percent, 1))

myhost = socket.gethostname()
myip = socket.gethostbyname(myhost)

if __name__ == '__main__':
    threshold = ""
    table_html = 'Hi Team,<p>This is a disk alert for the host '+ str(myhost) + '. Kindly perform housekeeping for highlighted mount point</p>';
    table_html += '<table style="border:2px solid black;border-collapse:collapse;">';
    table_html += '<tbody>';
    table_html += '<th style="font-size:13px;border:1px solid black;background-color:#A9A9A9;border-collapse:collapse;">Mount Point</th>';
    table_html += '<th style="font-size:13px;border:1px solid black;background-color:#A9A9A9;border-collapse:collapse;">Total Disk (GB)</th>';
    table_html += '<th style="font-size:13px;border:1px solid black;background-color:#A9A9A9;border-collapse:collapse;">Used Disk(GB)</th>';
    table_html += '<th style="font-size:13px;border:1px solid black;background-color:#A9A9A9;border-collapse:collapse;">Free Space(GB)</th>';
    table_html += '<th style="font-size:13px;border:1px solid black;background-color:#A9A9A9;border-collapse:collapse;">Used %</th>';
    for part in disk_partitions():
        if "/dev/" in part.device:
            mount_point = str(part.mountpoint)
            mp_tdisk = str(round(disk_usage(part.mountpoint).total,0))
            mp_udisk = str(round(disk_usage(part.mountpoint).used,1))
            mp_fdisk = str(round(disk_usage(part.mountpoint).free,1))
            mp_pdisk = str(disk_usage(part.mountpoint).percent)
            if (disk_usage(part.mountpoint).percent) >=90:
                threshold = "Critial"
                table_html += '<tr style="border:1px solid black;border-collapse:collapse;">';
                table_html += '<td style="font-size:13px;border:1px solid black;background-color:#FF0000;border-collapse:collapse;">'+mount_point+'</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FF0000;border-collapse:collapse;">'+  mp_tdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FF0000;border-collapse:collapse;">'+  mp_udisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FF0000;border-collapse:collapse;">'+  mp_fdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FF0000;border-collapse:collapse;">'+  mp_pdisk + '</td>';

            if (disk_usage(part.mountpoint).percent) >=80:
                threshold = "Warning"
                table_html += '<tr style="border:1px solid;border-collapse:collapse;">';
                table_html += '<td style="font-size:12px;border:1px solid black;background-color:#FFA500;border-collapse:collapse;">'+mount_point+'</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FFA500;border-collapse:collapse;">'+  mp_tdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FFA500;border-collapse:collapse;">'+  mp_udisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FFA500;border-collapse:collapse;">'+  mp_fdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;background-color:#FFA500;border-collapse:collapse;">'+  mp_pdisk+ '</td>';

            if (disk_usage(part.mountpoint).percent) <80:
                table_html += '<tr style="border:1px solid black;border-collapse:collapse;">';
                table_html += '<td style="font-size:12px;border:1px solid black;border-collapse:collapse;">'+mount_point+'</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;border-collapse:collapse;">'+  mp_tdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;border-collapse:collapse;">'+  mp_udisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;border-collapse:collapse;">'+  mp_fdisk + '</td>';
                table_html += '<td align = "center" style="font-size:12px;border:1px solid black;border-collapse:collapse;">'+  mp_pdisk + '</td>';
            table_html += '<span>';
            table_html += '</span>';
            table_html += '</td>';
            table_html += '</tr>';
    table_html += '</tbody>';
    table_html += '</table>';
    table_html += '<p>Regards <br> IT</p>'
    myhost = socket.gethostname()
    myip = socket.gethostbyname(myhost)
    from_addr = 'sender@smtpserver.com'
    to_addr = ['receiver@smtpserver.com']
    to = ",".join(to_addr)
    cc_addr = "receivercc@smtpserver.com"
    message = MIMEMultipart("alternative")
    message["Subject"] = "[%s]: Disk alert for %s | %s" % (threshold, myhost, myip)
    message["From"] = from_addr
    message["To"] = to
    message["Cc"] = cc_addr
    html = table_html
    html_msg = MIMEText(html, "html")
    message.attach(html_msg)
    context = ssl.create_default_context()
    with smtplib.SMTP('smtpserver.com', 587)as server:
        server.ehlo()
        server.starttls()
        server.ehlo
        server.login('sender@smtpserver.com','Password')
        server.sendmail(
            from_addr, to, message.as_string()
        )
