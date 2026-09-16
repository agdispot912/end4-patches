#!/usr/bin/env bash
# Reapply the VPN toggle patch independently from the display-mode helper.

set -euo pipefail

repo="$HOME/.config/quickshell/end4-pC"
patch="$(dirname "$(readlink -f "$0")")/vpn-toggle.patch"

usage() {
    printf 'Usage: %s {apply|remove|update}\n' "${0##*/}"
}

apply_patch() {
    git -C "$repo" apply --3way -p2 "$patch"
}

remove_patch() {
    git -C "$repo" apply --reverse -p2 "$patch"
}

case "${1:-apply}" in
    apply)
        apply_patch
        ;;
    remove)
        remove_patch
        ;;
    update)
        remove_patch
        if ! git -C "$repo" pull --ff-only; then
            apply_patch
            exit 1
        fi
        apply_patch
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
