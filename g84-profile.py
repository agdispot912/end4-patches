#!/usr/bin/env python3

import argparse
import fcntl
import os
import time


DEFAULT_DEVICE = "/dev/input/by-id/usb-_G84_HE-if02-hidraw"
HIDIOCSFEATURE = lambda length: 0xC0000000 | (length << 16) | (ord("H") << 8) | 0x06
HIDIOCGFEATURE = lambda length: 0xC0000000 | (length << 16) | (ord("H") << 8) | 0x07


parser = argparse.ArgumentParser(description="Switch an EPOMAKER G84 HE onboard profile.")
parser.add_argument("profile", nargs="?", type=int, choices=range(4))
parser.add_argument("--device", default=DEFAULT_DEVICE, help="vendor hidraw interface")
parser.add_argument("--current", action="store_true", help="print the active profile")
args = parser.parse_args()

if (args.profile is None) == (not args.current):
    parser.error("provide a profile or use --current")


def packet(command, value=0):
    # hidraw feature-report buffers include the report ID first. The G84 uses ID 0.
    result = bytearray(65)
    result[1] = command
    result[2] = value
    result[8] = ~(result[1] + result[2]) & 0xFF
    return result


def read_profile(fd):
    fcntl.ioctl(fd, HIDIOCSFEATURE(65), packet(0x84))
    response = bytearray(65)
    fcntl.ioctl(fd, HIDIOCGFEATURE(len(response)), response)
    if response[1] != 0x84 or response[2] not in range(4):
        raise RuntimeError(f"unexpected profile response: {response[:9].hex(' ')}")
    return response[2]


try:
    fd = os.open(args.device, os.O_RDWR)
    try:
        if args.current:
            print(read_profile(fd))
        else:
            fcntl.ioctl(fd, HIDIOCSFEATURE(65), packet(0x04, args.profile))
            # The Hub waits 250 ms for the firmware to commit the profile change.
            time.sleep(0.25)
    finally:
        os.close(fd)
except (OSError, RuntimeError) as error:
    parser.exit(1, f"Could not communicate with {args.device}: {error}\n")

if not args.current:
    print(f"Switched G84 HE to profile {args.profile}.")
