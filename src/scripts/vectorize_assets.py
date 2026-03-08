#!/usr/bin/env python3
"""
Synthesis-Dark Asset Vectorization Pipeline

Converts PNG source assets into SVG authority files, while also producing
repo-wide migration manifests and prioritized reports.

Usage:
    python3 vectorize_assets.py --input assets/ --output src/assets/gtk3-4/
    python3 vectorize_assets.py --input . --output /tmp/sd-vectorized-repo --recursive --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from shutil import which

from raster_wrapper_preferences import preferred_authority_for


DEFAULT_WORKERS = max(1, min(6, os.cpu_count() or 1))
MATE_ICON_CATEGORIES = {
    'actions',
    'animations',
    'categories',
    'emblems',
    'emotes',
    'status',
}
TELA_ICON_CATEGORIES = {
    'apps',
    'devices',
    'mimetypes',
    'places',
}
GNOME_SHELL_SIMPLE_UI = {
    'corner-ripple-ltr',
    'corner-ripple-rtl',
    'ws-switch-arrow-down',
    'ws-switch-arrow-up',
}
CINNAMON_SIMPLE_UI = {
    'overview',
    'overview-hover',
}
ICON_SEMANTIC_ALIASES = {
    'add': [('actions', 'list-add')],
    'appointment': [('actions', 'appointment-new')],
    'audio-volume-off': [('status', 'audio-volume-muted')],
    'back': [('actions', 'go-previous')],
    'bookmark_add': [('actions', 'bookmark-add')],
    'bookmarks_list_add': [('actions', 'bookmark-add')],
    'bottom': [('actions', 'go-bottom')],
    'centrejust': [('actions', 'format-justify-center')],
    'connect_creating': [('status', 'network-wireless-acquiring')],
    'connect_established': [('status', 'network-wireless-connected')],
    'connect_no': [('status', 'network-offline')],
    'down': [('actions', 'go-down')],
    'editclear': [('actions', 'edit-clear')],
    'edittrash': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'emblem-noread': [('emblems', 'emblem-unreadable')],
    'emblem-nowrite': [('emblems', 'emblem-readonly')],
    'error': [('status', 'dialog-error')],
    'folder_open': [('status', 'folder-open')],
    'folder_new': [('actions', 'folder-new')],
    'forward': [('actions', 'go-next')],
    'gnome-dev-wavelan-encrypted': [('status', 'network-wireless-encrypted')],
    'gnome-fs-directory-accept': [('status', 'folder-drag-accept')],
    'gnome-fs-loading-icon': [('status', 'folder-visiting')],
    'gnome-fs-trash-full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'gnome-fs-directory-visiting': [('status', 'folder-visiting')],
    'gnome-lockscreen': [('status', 'system-lock-screen')],
    'gnome-logout': [('actions', 'application-exit')],
    'gnome-run': [('actions', 'system-run')],
    'gnome-searchtool': [('actions', 'system-search')],
    'gnome-shutdown': [('actions', 'system-shutdown')],
    'gnome-stock-mail-new': [('actions', 'mail-message-new')],
    'gnome-stock-mail-snd': [('actions', 'mail-send')],
    'gnome-stock-trash-full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'gtk-dialog-error': [('status', 'dialog-error')],
    'gtk-dialog-info': [('status', 'dialog-information')],
    'gtk-dialog-question': [('status', 'dialog-question')],
    'gtk-dialog-warning': [('status', 'dialog-warning')],
    'gtk-delete': [('actions', 'edit-delete')],
    'gtk-find': [('actions', 'edit-find')],
    'gtk-find-and-replace': [('actions', 'edit-find-replace')],
    'gtk-go-back-ltr': [('actions', 'go-previous')],
    'gtk-go-back-rtl': [('actions', 'go-previous')],
    'gtk-go-forward-ltr': [('actions', 'go-next')],
    'gtk-go-forward-rtl': [('actions', 'go-next')],
    'gtk-goto-first-ltr': [('actions', 'go-first')],
    'gtk-goto-first-rtl': [('actions', 'go-first')],
    'gtk-goto-last-ltr': [('actions', 'go-last')],
    'gtk-goto-last-rtl': [('actions', 'go-last')],
    'gtk-jump-to-ltr': [('actions', 'go-jump')],
    'gtk-jump-to-rtl': [('actions', 'go-jump')],
    'gtk-missing-image': [('apps', 'image-missing')],
    'gtk-new': [('actions', 'document-new')],
    'gtk-open': [('actions', 'document-open')],
    'gtk-print': [('actions', 'document-print')],
    'gtk-print-preview': [('actions', 'document-print-preview')],
    'gtk-properties': [('actions', 'document-properties')],
    'gtk-refresh': [('actions', 'view-refresh')],
    'gtk-revert-to-saved-ltr': [('actions', 'edit-undo')],
    'gtk-revert-to-saved-rtl': [('actions', 'edit-undo')],
    'gtk-save': [('actions', 'document-save')],
    'gtk-save-as': [('actions', 'document-save-as')],
    'gtk-select-all': [('actions', 'edit-select-all')],
    'gtk-stop': [('actions', 'process-stop')],
    'image-missing': [('apps', 'image-missing')],
    'important': [('emblems', 'emblem-important')],
    'info': [('status', 'dialog-information')],
    'kfind': [('actions', 'edit-find')],
    'left': [('actions', 'go-previous')],
    'lock': [('status', 'system-lock-screen')],
    'mail_send': [('actions', 'mail-send')],
    'mail_new': [('actions', 'mail-message-new')],
    'messagebox_critical': [('status', 'dialog-error')],
    'messagebox_info': [('status', 'dialog-information')],
    'messagebox_warning': [('status', 'dialog-warning')],
    'nm-adhoc': [('status', 'network-wireless-hotspot')],
    'nm-device-wireless': [('status', 'network-wireless-connected')],
    'nm-no-connection': [('status', 'network-offline')],
    'next': [('actions', 'go-next')],
    'previous': [('actions', 'go-previous')],
    'reload': [('actions', 'view-refresh')],
    'reload3': [('actions', 'view-refresh')],
    'reload_all_tabs': [('actions', 'view-refresh')],
    'reload_page': [('actions', 'view-refresh')],
    'revert': [('actions', 'document-revert')],
    'right': [('actions', 'go-next')],
    'sunny': [('status', 'weather-clear')],
    'search': [('actions', 'system-search')],
    'start': [('actions', 'media-playback-start')],
    'stock_attach': [('status', 'mail-attachment')],
    'stock_appointment-reminder': [('status', 'appointment-soon')],
    'stock_appointment-reminder-excl': [('status', 'appointment-missed')],
    'stock_delete': [('actions', 'edit-delete')],
    'stock_dialog-error': [('status', 'dialog-error')],
    'stock_dialog-info': [('apps', 'stock_dialog-info'), ('actions', 'dialog-information'), ('status', 'dialog-information')],
    'stock_dialog-question': [('status', 'dialog-question')],
    'stock_dialog-warning': [('actions', 'dialog-warning'), ('status', 'dialog-warning')],
    'stock_file-properites': [('actions', 'document-properties')],
    'stock_first': [('actions', 'go-first')],
    'stock_last': [('actions', 'go-last')],
    'stock_left': [('actions', 'go-previous')],
    'stock_lock': [('status', 'system-lock-screen')],
    'stock_lock-broken': [('status', 'channel-insecure')],
    'stock_lock-ok': [('status', 'channel-secure')],
    'stock_lock-open': [('status', 'changes-allow')],
    'stock_mail-compose': [('actions', 'mail-send')],
    'stock_mail-open': [('status', 'mail-read')],
    'stock_mail-send': [('actions', 'mail-send')],
    'stock_new-address-book': [('actions', 'address-book-new')],
    'stock_new-appointment': [('actions', 'appointment-new')],
    'stock_new-dir': [('actions', 'folder-new')],
    'stock_new-text': [('actions', 'document-new')],
    'stock_open': [('status', 'folder-open')],
    'stock_print': [('actions', 'document-print')],
    'stock_print-preview': [('actions', 'document-print-preview')],
    'stock_print-setup': [('actions', 'document-page-setup')],
    'stock_properties': [('actions', 'document-properties')],
    'stock_refresh': [('actions', 'view-refresh')],
    'stock_right': [('actions', 'go-next')],
    'stock_save': [('actions', 'document-save')],
    'stock_save-as': [('actions', 'document-save-as')],
    'stock_search': [('actions', 'system-search')],
    'stock_search-and-replace': [('actions', 'edit-find-replace')],
    'stock_select-all': [('actions', 'edit-select-all')],
    'stock_stop': [('actions', 'process-stop')],
    'stock_shuffle': [('status', 'media-playlist-shuffle')],
    'stock_repeat': [('status', 'media-playlist-repeat')],
    'stock_mail-replied': [('status', 'mail-replied')],
    'stock_mail-unread': [('status', 'mail-unread')],
    'stock_trash_full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'stock_volume': [('status', 'audio-volume-medium')],
    'stock_volume-0': [('panel', 'audio-volume-off'), ('actions', 'audio-volume-muted'), ('status', 'audio-volume-muted')],
    'stock_volume-max': [('panel', 'audio-volume-high'), ('actions', 'audio-volume-high'), ('status', 'audio-volume-high')],
    'stock_volume-med': [('panel', 'audio-volume-medium'), ('actions', 'audio-volume-medium'), ('status', 'audio-volume-medium')],
    'stock_volume-min': [('panel', 'audio-volume-low'), ('actions', 'audio-volume-low'), ('status', 'audio-volume-low')],
    'stock_volume-mute': [('panel', 'audio-volume-off'), ('actions', 'audio-volume-muted'), ('status', 'audio-volume-muted')],
    'stock_weather-cloudy': [('status', 'weather-overcast'), ('status', 'weather-cloudy')],
    'stock_weather-few-clouds': [('status', 'weather-few-clouds')],
    'stock_weather-fog': [('status', 'weather-fog')],
    'stock_weather-night-clear': [('status', 'weather-clear-night')],
    'stock_weather-night-few-clouds': [('status', 'weather-few-clouds-night')],
    'stock_weather-showers': [('status', 'weather-showers')],
    'stock_weather-snow': [('status', 'weather-snow')],
    'stock_weather-storm': [('status', 'weather-storm')],
    'stock_weather-sunny': [('status', 'weather-clear')],
    'stop': [('actions', 'media-playback-stop')],
    'tab_new': [('actions', 'tab-new')],
    'text_bold': [('actions', 'format-text-bold')],
    'text_italic': [('actions', 'format-text-italic')],
    'text_strike': [('actions', 'format-text-strikethrough')],
    'text_under': [('actions', 'format-text-underline')],
    'top': [('actions', 'go-top')],
    'trashcan_full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'up': [('actions', 'go-up')],
    'user-trash-full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'undo': [('actions', 'edit-undo')],
    'viewmag+': [('actions', 'zoom-in')],
    'viewmag-': [('actions', 'zoom-out')],
    'viewmag1': [('actions', 'zoom-original')],
    'viewmagfit': [('actions', 'zoom-fit-best')],
    'xfce-system-exit': [('actions', 'application-exit')],
    'xfce-system-lock': [('status', 'system-lock-screen')],
    'xfce-trash_full': [('status', 'user-trash-full'), ('places', 'user-trash-full')],
    'access': [('apps', 'preferences-desktop-accessibility')],
    'application-pgp-encrypted': [('apps', 'pgp-keys')],
    'application-x-gnome-saved-search': [('places', 'folder-saved-search')],
    'application-x-homebank': [('apps', 'homebank')],
    'application-x-javascript': [('mimetypes', 'text-x-javascript')],
    'application-x-keepass': [('apps', 'keepass')],
    'application-x-package-list': [('mimetypes', 'application-x-archive')],
    'application-x-php': [('mimetypes', 'text-x-php')],
    'application-x-planner': [('mimetypes', 'x-office-calendar')],
    'application-x-python-bytecode': [('mimetypes', 'text-x-python')],
    'application-x-remote-connection': [('apps', 'remote-desktop')],
    'application-x-vnc': [('apps', 'remote-desktop')],
    'ascii': [('mimetypes', 'text-x-generic')],
    'background': [('apps', 'cs-backgrounds')],
    'binary': [('mimetypes', 'application-x-executable')],
    'camera': [('devices', 'camera-photo')],
    'cdrom_unmount': [('devices', 'drive-optical')],
    'cdwriter_unmount': [('devices', 'media-optical')],
    'chardevice': [('devices', 'computer')],
    'config-language': [('apps', 'preferences-desktop-locale')],
    'config-users': [('apps', 'system-users')],
    'contents2': [('mimetypes', 'text-x-generic')],
    'deb': [('mimetypes', 'application-x-deb')],
    'desktop': [('places', 'user-desktop')],
    'distributor-logo': [('apps', 'distributor-logo')],
    'document': [('mimetypes', 'text-x-generic')],
    'dvd_unmount': [('devices', 'media-optical-dvd')],
    'editcopy': [('actions', 'edit-copy')],
    'editcut': [('actions', 'edit-cut')],
    'editdelete': [('actions', 'edit-delete')],
    'editpaste': [('actions', 'edit-paste')],
    'empty': [('mimetypes', 'text-x-generic')],
    'emptytrash': [('places', 'user-trash')],
    'emblem-desktop': [('emblems', 'emblem-system')],
    'exec': [('mimetypes', 'application-x-executable')],
    'exit': [('actions', 'application-exit')],
    'filefind': [('actions', 'edit-find')],
    'filenew': [('actions', 'document-new')],
    'fileopen': [('actions', 'document-open')],
    'fileprint': [('actions', 'document-print')],
    'filequickprint': [('actions', 'document-print-preview')],
    'filesave': [('actions', 'document-save')],
    'find': [('actions', 'edit-find')],
    'folder_home': [('places', 'user-home')],
    'folder_tar': [('mimetypes', 'application-x-archive')],
    'font': [('mimetypes', 'font-x-generic')],
    'font_bitmap': [('mimetypes', 'font-x-generic')],
    'font_truetype': [('mimetypes', 'font-x-generic')],
    'font_type1': [('mimetypes', 'font-x-generic')],
    'gnome-applications': [('categories', 'applications-all')],
    'gnome-character-map': [('apps', 'accessories-character-map')],
    'gnome-control-center': [('categories', 'preferences-system')],
    'gnome-devel': [('categories', 'applications-development')],
    'gnome-dev-battery': [('devices', 'battery')],
    'gnome-dev-cdrom': [('devices', 'drive-optical')],
    'gnome-dev-cdrom-audio': [('devices', 'media-optical-cd-audio')],
    'gnome-dev-computer': [('devices', 'computer')],
    'gnome-dev-disc-cdr': [('devices', 'media-optical')],
    'gnome-dev-disc-cdrw': [('devices', 'media-optical')],
    'gnome-dev-disc-dvdr': [('devices', 'media-optical-dvd')],
    'gnome-dev-disc-dvdr-plus': [('devices', 'media-optical-dvd')],
    'gnome-dev-disc-dvdram': [('devices', 'media-optical-dvd')],
    'gnome-dev-disc-dvdrom': [('devices', 'media-optical-dvd')],
    'gnome-dev-disc-dvdrw': [('devices', 'media-optical-dvd')],
    'gnome-dev-dvd': [('devices', 'media-optical-dvd')],
    'gnome-dev-ethernet': [('devices', 'network-wired')],
    'gnome-dev-floppy': [('devices', 'media-floppy')],
    'gnome-dev-harddisk': [('devices', 'drive-harddisk')],
    'gnome-dev-harddisk-1394': [('devices', 'drive-harddisk-ieee1394')],
    'gnome-dev-harddisk-usb': [('devices', 'drive-harddisk-usb')],
    'gnome-dev-ipod': [('devices', 'multimedia-player-apple-ipod-touch')],
    'gnome-dev-keyboard': [('devices', 'input-keyboard')],
    'gnome-dev-media-cf': [('devices', 'media-memory')],
    'gnome-dev-media-ms': [('devices', 'media-flash-memory-stick')],
    'gnome-dev-media-sdmmc': [('devices', 'media-flash-sd-mmc')],
    'gnome-dev-media-sm': [('devices', 'media-memory')],
    'gnome-dev-mouse-ball': [('devices', 'input-mouse')],
    'gnome-dev-mouse-optical': [('devices', 'input-mouse')],
    'gnome-dev-printer': [('devices', 'printer')],
    'gnome-dev-removable': [('devices', 'drive-removable-media')],
    'gnome-dev-removable-1394': [('devices', 'drive-removable-media')],
    'gnome-dev-removable-usb': [('devices', 'drive-removable-media-usb')],
    'gnome-dev-wavelan': [('devices', 'network-wireless')],
    'gnome-fs-desktop': [('places', 'user-desktop')],
    'gnome-fs-directory': [('places', 'folder')],
    'gnome-fs-executable': [('mimetypes', 'application-x-executable')],
    'gnome-fs-ftp': [('places', 'folder-remote')],
    'gnome-fs-home': [('places', 'user-home')],
    'gnome-fs-network': [('places', 'network-workgroup')],
    'gnome-fs-nfs': [('places', 'folder-remote')],
    'gnome-fs-regular': [('mimetypes', 'text-x-generic')],
    'gnome-fs-server': [('places', 'network-server')],
    'gnome-fs-share': [('places', 'folder-publicshare')],
    'gnome-fs-smb': [('places', 'folder-remote')],
    'gnome-fs-ssh': [('places', 'folder-remote')],
    'gnome-fs-trash-empty': [('places', 'user-trash')],
    'gnome-globe': [('categories', 'applications-internet')],
    'gnome-graphics': [('categories', 'applications-graphics')],
    'gnome-help': [('apps', 'help-browser')],
    'gnome-main-menu': [('places', 'start-here')],
    'gnome-mixer': [('apps', 'multimedia-volume-control')],
    'gnome-monitor': [('apps', 'utilities-system-monitor')],
    'gnome-modem': [('devices', 'network-modem')],
    'gnome-multimedia': [('categories', 'applications-multimedia')],
    'gnome-netstatus-disconn': [('status', 'network-disconnected')],
    'gnome-netstatus-error': [('status', 'network-error')],
    'gnome-netstatus-idle': [('status', 'network-idle')],
    'gnome-netstatus-rx': [('status', 'network-receive')],
    'gnome-netstatus-tx': [('status', 'network-transmit')],
    'gnome-netstatus-txrx': [('status', 'network-transmit-receive')],
    'gnome-other': [('categories', 'applications-other')],
    'gnome-remote-desktop': [('apps', 'remote-desktop')],
    'gnome-settings': [('categories', 'preferences-system')],
    'gnome-settings-accessibility-technologies': [('apps', 'preferences-desktop-accessibility')],
    'gnome-settings-background': [('apps', 'cs-backgrounds')],
    'gnome-settings-font': [('apps', 'fonts')],
    'gnome-settings-keybindings': [('apps', 'preferences-desktop-keyboard-shortcuts')],
    'gnome-settings-theme': [('apps', 'preferences-desktop-theme-global')],
    'gnome-terminal': [('apps', 'utilities-terminal')],
    'gnome-stock-mail-fwd': [('actions', 'mail-forward')],
    'gnome-stock-mail-rpl': [('actions', 'mail-reply')],
    'gnome-stock-text-indent': [('actions', 'format-indent-more')],
    'gnome-stock-text-unindent': [('actions', 'format-indent-less')],
    'gnome-system': [('categories', 'applications-system')],
    'gnome-util': [('categories', 'applications-utilities')],
    'gtk-about': [('actions', 'help-about')],
    'gtk-add': [('actions', 'list-add')],
    'gtk-bold': [('actions', 'format-text-bold')],
    'gtk-cancel': [('actions', 'window-close')],
    'gtk-clear': [('actions', 'edit-clear')],
    'gtk-close': [('actions', 'window-close')],
    'gtk-copy': [('actions', 'edit-copy')],
    'gtk-cut': [('actions', 'edit-cut')],
    'gtk-dnd-multiple': [('actions', 'tab-new')],
    'gtk-execute': [('actions', 'system-run')],
    'gtk-fullscreen': [('actions', 'view-fullscreen')],
    'gtk-go-down': [('actions', 'go-down')],
    'gtk-go-up': [('actions', 'go-up')],
    'gtk-goto-bottom': [('actions', 'go-bottom')],
    'gtk-goto-top': [('actions', 'go-top')],
    'gtk-help': [('categories', 'system-help')],
    'gtk-home': [('actions', 'go-home')],
    'gtk-indent-ltr': [('actions', 'format-indent-more')],
    'gtk-indent-rtl': [('actions', 'format-indent-more')],
    'gtk-italic': [('actions', 'format-text-italic')],
    'gtk-justify-center': [('actions', 'format-justify-center')],
    'gtk-justify-fill': [('actions', 'format-justify-fill')],
    'gtk-justify-left': [('actions', 'format-justify-left')],
    'gtk-justify-right': [('actions', 'format-justify-right')],
    'gtk-leave-fullscreen': [('actions', 'view-restore')],
    'gtk-media-forward-ltr': [('actions', 'media-seek-forward')],
    'gtk-media-forward-rtl': [('actions', 'media-seek-forward')],
    'gtk-media-next-ltr': [('actions', 'go-next')],
    'gtk-media-next-rtl': [('actions', 'go-next')],
    'gtk-media-pause': [('actions', 'media-playback-pause')],
    'gtk-media-play-ltr': [('actions', 'media-playback-start')],
    'gtk-media-previous-ltr': [('actions', 'go-previous')],
    'gtk-media-previous-rtl': [('actions', 'go-previous')],
    'gtk-media-record': [('actions', 'media-record')],
    'gtk-media-rewind-ltr': [('actions', 'media-seek-backward')],
    'gtk-media-rewind-rtl': [('actions', 'media-seek-backward')],
    'gtk-media-stop': [('actions', 'media-playback-stop')],
    'gtk-paste': [('actions', 'edit-paste')],
    'gtk-preferences': [('categories', 'preferences-system')],
    'gtk-quit': [('actions', 'application-exit')],
    'gtk-redo-ltr': [('actions', 'edit-redo')],
    'gtk-remove': [('actions', 'list-remove')],
    'gtk-sort-ascending': [('actions', 'view-sort-ascending')],
    'gtk-sort-descending': [('actions', 'view-sort-descending')],
    'gtk-spell-check': [('actions', 'tools-check-spelling')],
    'gtk-strikethrough': [('actions', 'format-text-strikethrough')],
    'gtk-underline': [('actions', 'format-text-underline')],
    'gtk-undo-ltr': [('actions', 'edit-undo')],
    'gtk-unindent-ltr': [('actions', 'format-indent-less')],
    'gtk-unindent-rtl': [('actions', 'format-indent-less')],
    'gtk-zoom-100': [('actions', 'zoom-original')],
    'gtk-zoom-fit': [('actions', 'zoom-fit-best')],
    'gtk-zoom-in': [('actions', 'zoom-in')],
    'gtk-zoom-out': [('actions', 'zoom-out')],
    'gucharmap': [('apps', 'accessories-character-map')],
    'harddrive': [('devices', 'drive-harddisk')],
    'help': [('categories', 'system-help')],
    'help-faq': [('categories', 'system-help')],
    'html': [('mimetypes', 'text-html')],
    'image': [('mimetypes', 'image-x-generic')],
    'image-svg+xml-compressed': [('mimetypes', 'image-x-generic')],
    'inode-directory': [('places', 'folder')],
    'input_devices_settings': [('categories', 'preferences-other')],
    'ipod_mount': [('devices', 'multimedia-player-apple-ipod-touch')],
    'kcharselect': [('apps', 'accessories-character-map')],
    'kcmkwm': [('apps', 'preferences-desktop-theme-windowdecorations')],
    'kcmsound': [('apps', 'multimedia-volume-control')],
    'kcontrol': [('categories', 'preferences-system')],
    'kedit': [('apps', 'accessories-text-editor')],
    'kfm': [('apps', 'filemanager-actions')],
    'kfm_home': [('actions', 'go-home')],
    'khelpcenter': [('apps', 'help-browser')],
    'kjobviewer': [('devices', 'printer')],
    'konsole': [('apps', 'utilities-terminal')],
    'krfb': [('apps', 'remote-desktop')],
    'kscreensaver': [('apps', 'preferences-desktop-screensaver')],
    'ksysguard': [('apps', 'utilities-system-monitor')],
    'kuser': [('apps', 'system-users')],
    'kwin': [('apps', 'preferences-desktop-theme-windowdecorations')],
    'leftjust': [('actions', 'format-justify-left')],
    'locale': [('apps', 'preferences-desktop-locale')],
    'logviewer': [('apps', 'utilities-log-viewer')],
    'mail-signed': [('actions', 'mail-signed-full')],
    'mail-signed-verified': [('actions', 'mail-signed-full')],
    'misc': [('mimetypes', 'text-x-generic')],
    'network': [('places', 'network-workgroup')],
    'network_local': [('places', 'network-workgroup')],
    'novell-button': [('places', 'distributor-logo')],
    'openterm': [('apps', 'utilities-terminal')],
    'package_development': [('categories', 'applications-development')],
    'package_games': [('categories', 'applications-games')],
    'package_graphics': [('categories', 'applications-graphics')],
    'package_multimedia': [('categories', 'applications-multimedia')],
    'package_network': [('categories', 'applications-network')],
    'package_office': [('categories', 'applications-office')],
    'package_settings': [('categories', 'preferences-system')],
    'package_system': [('categories', 'applications-system')],
    'package_utilities': [('categories', 'applications-utilities')],
    'plan': [('mimetypes', 'x-office-calendar')],
    'preferences-desktop': [('categories', 'preferences-other')],
    'preferences-desktop-font': [('apps', 'fonts')],
    'preferences-desktop-keybindings': [('apps', 'preferences-desktop-keyboard-shortcuts')],
    'preferences-desktop-peripherals': [('categories', 'preferences-other')],
    'preferences-desktop-personal': [('categories', 'preferences-other')],
    'preferences-desktop-theme': [('apps', 'preferences-desktop-theme-global')],
    'preferences-system-network': [('categories', 'applications-network')],
    'printer-remote': [('devices', 'printer-network')],
    'printmgr': [('devices', 'printer')],
    'redhat-accessories': [('categories', 'applications-utilities')],
    'redhat-filemanager': [('apps', 'filemanager-actions')],
    'redhat-games': [('categories', 'applications-games')],
    'redhat-graphics': [('categories', 'applications-graphics')],
    'redhat-internet': [('categories', 'applications-internet')],
    'redhat-office': [('categories', 'applications-office')],
    'redhat-preferences': [('categories', 'preferences-system')],
    'redhat-programming': [('categories', 'applications-development')],
    'redhat-sound_video': [('categories', 'applications-multimedia')],
    'redhat-system_settings': [('categories', 'preferences-system')],
    'redhat-system_tools': [('categories', 'applications-system')],
    'screensaver': [('apps', 'preferences-desktop-screensaver')],
    'server': [('places', 'network-server')],
    'shellscript': [('mimetypes', 'application-x-shellscript')],
    'sound': [('mimetypes', 'audio-x-generic')],
    'spreadsheet': [('mimetypes', 'x-office-spreadsheet')],
    'stock_addressbook': [('mimetypes', 'x-office-address-book')],
    'stock_calendar': [('mimetypes', 'x-office-calendar')],
    'stock_certificate': [('mimetypes', 'application-pgp-encrypted')],
    'stock_internet': [('categories', 'applications-internet')],
    'stock_media-rew': [('actions', 'media-seek-backward')],
    'stock_media-stop': [('actions', 'media-playback-stop')],
    'stock_new-bcard': [('actions', 'address-book-new')],
    'stock_new-window': [('actions', 'window-new')],
    'stock_paste': [('actions', 'edit-paste')],
    'stock_redo': [('actions', 'edit-redo')],
    'stock_script': [('mimetypes', 'application-x-shellscript')],
    'stock_spam': [('actions', 'mail-mark-junk')],
    'stock_spellcheck': [('actions', 'tools-check-spelling')],
    'stock_text_bold': [('actions', 'format-text-bold')],
    'stock_text_center': [('actions', 'format-justify-center')],
    'stock_text_indent': [('actions', 'format-indent-more')],
    'stock_text_italic': [('actions', 'format-text-italic')],
    'stock_text_justify': [('actions', 'format-justify-fill')],
    'stock_text_left': [('actions', 'format-justify-left')],
    'stock_text_right': [('actions', 'format-justify-right')],
    'stock_text_underlined': [('actions', 'format-text-underline')],
    'stock_text_unindent': [('actions', 'format-indent-less')],
    'stock_text-strikethrough': [('actions', 'format-text-strikethrough')],
    'stock_top': [('actions', 'go-top')],
    'stock_undo': [('actions', 'edit-undo')],
    'stock_up': [('actions', 'go-up')],
    'stock_zoom-1': [('actions', 'zoom-original')],
    'stock_zoom-in': [('actions', 'zoom-in')],
    'stock_zoom-out': [('actions', 'zoom-out')],
    'stock_zoom-page': [('actions', 'zoom-fit-best')],
    'style': [('apps', 'theme-config')],
    'system': [('devices', 'computer')],
    'system-config-keyboard': [('apps', 'preferences-desktop-keyboard')],
    'system-config-users': [('apps', 'system-users')],
    'text-x-vcard': [('mimetypes', 'x-office-address-book')],
    'txt': [('mimetypes', 'text-x-generic')],
    'txt2': [('mimetypes', 'text-x-generic')],
    'update-manager': [('apps', 'system-software-update')],
    'usbpendrive_unmount': [('devices', 'drive-removable-media-usb-pendrive')],
    'vcalendar': [('mimetypes', 'x-office-calendar')],
    'vcard': [('mimetypes', 'x-office-address-book')],
    'video': [('mimetypes', 'video-x-generic')],
    'wallpaper': [('apps', 'preferences-desktop-wallpaper')],
    'window_fullscreen': [('actions', 'view-fullscreen')],
    'window_nofullscreen': [('actions', 'view-restore')],
    'wordprocessing': [('mimetypes', 'x-office-document')],
    'xfce-filemanager': [('apps', 'filemanager-actions')],
    'xfce-games': [('categories', 'applications-games')],
    'xfce-graphics': [('categories', 'applications-graphics')],
    'xfce-internet': [('categories', 'applications-internet')],
    'xfce-multimedia': [('categories', 'applications-multimedia')],
    'xfce-office': [('categories', 'applications-office')],
    'xfce-printer': [('devices', 'printer')],
    'xfce-system-settings': [('categories', 'preferences-system')],
    'xfce-terminal': [('apps', 'utilities-terminal')],
    'xfce-trash_empty': [('places', 'user-trash')],
    'xfce-utils': [('categories', 'applications-utilities')],
    'xfce4-backdrop': [('apps', 'cs-backgrounds')],
    'xfce4-display': [('devices', 'video-display')],
    'xfce4-keyboard': [('devices', 'input-keyboard')],
    'xfce4-mixer': [('apps', 'multimedia-volume-control')],
    'xfce4-mouse': [('devices', 'input-mouse')],
    'xfce4-settings': [('categories', 'preferences-system')],
    'xfwm4': [('apps', 'preferences-desktop-theme-windowdecorations')],
    'xscreensaver': [('apps', 'preferences-desktop-screensaver')],
    'yast_HD': [('devices', 'drive-harddisk')],
    'yast_mouse': [('devices', 'input-mouse')],
    'yast_printer': [('devices', 'printer')],
    'yast_soundcard': [('devices', 'audio-card')],
    'zen-icon': [('apps', 'zen-browser')],
    'zoom-best-fit': [('actions', 'zoom-fit-best')],
    '3floppy_unmount': [('devices', 'media-floppy')],
    'accessibility-directory': [('apps', 'preferences-desktop-accessibility')],
    'arts': [('categories', 'applications-multimedia')],
    'camera_unmount': [('devices', 'camera-photo')],
    'display': [('devices', 'video-display')],
    'dnd-multiple': [('actions', 'tab-new')],
    'drive-cdrom': [('devices', 'drive-optical')],
    'finish': [('actions', 'dialog-ok-apply')],
    'gnome-joystick': [('categories', 'preferences-other')],
    'gnome-mime-audio': [('mimetypes', 'audio-x-generic')],
    'gnome-mime-image': [('mimetypes', 'image-x-generic')],
    'gnome-mime-text': [('mimetypes', 'text-x-generic')],
    'gnome-mime-text-vnd.wap.wml': [('mimetypes', 'text-html')],
    'gnome-mime-text-x-csh': [('mimetypes', 'application-x-shellscript')],
    'gnome-mime-text-x-sh': [('mimetypes', 'application-x-shellscript')],
    'gnome-mime-text-x-vcalendar': [('mimetypes', 'x-office-calendar')],
    'gnome-mime-text-x-vcard': [('mimetypes', 'x-office-address-book')],
    'gtk-cdrom': [('devices', 'drive-optical')],
    'gtk-directory': [('places', 'folder')],
    'gtk-file': [('mimetypes', 'text-x-generic')],
    'gtk-floppy': [('devices', 'media-floppy')],
    'gtk-harddisk': [('devices', 'drive-harddisk')],
    'gtk-network': [('places', 'network-workgroup')],
    'gohome': [('actions', 'go-home')],
    'go-first-rtl': [('actions', 'go-first')],
    'go-last-rtl': [('actions', 'go-last')],
    'go-next-rtl': [('actions', 'go-next')],
    'go-previous-rtl': [('actions', 'go-previous')],
    'gnome-spinner': [('status', 'process-working')],
    'gnome-stock-mic': [('devices', 'audio-input-microphone')],
    'gnome-stock-trash': [('places', 'user-trash')],
    'gnome-mime-x-directory-nfs-server': [('places', 'network-server')],
    'gnome-mime-x-directory-smb-server': [('places', 'network-server')],
    'gnome-mime-x-directory-smb-share': [('places', 'folder-publicshare')],
    'gnome-mime-x-directory-smb-workgroup': [('places', 'network-workgroup')],
    'key_bindings': [('apps', 'preferences-desktop-keyboard-shortcuts')],
    'keyboard': [('devices', 'input-keyboard')],
    'kxkb': [('devices', 'input-keyboard')],
    'mail_replyall': [('actions', 'mail-reply-all')],
    'mail_spam': [('actions', 'mail-mark-junk')],
    'media-cdrom': [('devices', 'drive-optical')],
    'mime_ascii': [('mimetypes', 'text-x-generic')],
    'multimedia': [('categories', 'applications-multimedia')],
    'mouse': [('devices', 'input-mouse')],
    'openofficeorg-extension': [('mimetypes', 'application-x-archive')],
    'openofficeorg3-extension': [('mimetypes', 'application-x-archive')],
    'package': [('mimetypes', 'application-x-archive')],
    'package_editors': [('mimetypes', 'text-x-generic')],
    'package_wordprocessing': [('mimetypes', 'x-office-document')],
    'player_eject': [('actions', 'media-eject')],
    'player_end': [('actions', 'go-last')],
    'player_fwd': [('actions', 'media-seek-forward')],
    'player_pause': [('actions', 'media-playback-pause')],
    'player_play': [('actions', 'media-playback-start')],
    'player_record': [('actions', 'media-record')],
    'player_rew': [('actions', 'media-seek-backward')],
    'player_start': [('actions', 'go-first')],
    'player_stop': [('actions', 'media-playback-stop')],
    'redo': [('actions', 'edit-redo')],
    'redhat-home': [('actions', 'go-home')],
    'remove': [('actions', 'list-remove')],
    'rightjust': [('actions', 'format-justify-right')],
    'rpm': [('mimetypes', 'application-x-rpm')],
    'stock_about': [('actions', 'help-about')],
    'stock_add-bookmark': [('actions', 'bookmark-add')],
    'stock_bottom': [('actions', 'go-bottom')],
    'stock_close': [('actions', 'window-close')],
    'stock_copy': [('actions', 'edit-copy')],
    'stock_cut': [('actions', 'edit-cut')],
    'stock_down': [('actions', 'go-down')],
    'stock_fullscreen': [('actions', 'view-fullscreen')],
    'stock_help': [('categories', 'system-help')],
    'stock_help-add-bookmark': [('actions', 'bookmark-add')],
    'stock_home': [('actions', 'go-home')],
    'stock_leave-fullscreen': [('actions', 'view-restore')],
    'stock_mail-forward': [('actions', 'mail-forward')],
    'stock_mail-reply': [('actions', 'mail-reply')],
    'stock_mail-reply-to-all': [('actions', 'mail-reply-all')],
    'stock_mail-send-receive': [('actions', 'mail-send-receive')],
    'stock_media-fwd': [('actions', 'media-seek-forward')],
    'stock_media-next': [('actions', 'go-next')],
    'stock_media-pause': [('actions', 'media-playback-pause')],
    'stock_media-play': [('actions', 'media-playback-start')],
    'stock_media-prev': [('actions', 'go-previous')],
    'stock_media-rec': [('actions', 'media-record')],
    'stock_new-tab': [('actions', 'tab-new')],
    'stock_printers': [('devices', 'printer')],
    'stock_mic': [('devices', 'audio-input-microphone')],
    'stock_cell-phone': [('devices', 'smartphone')],
    'susehelpcenter': [('apps', 'help-browser')],
    'system-floppy': [('devices', 'media-floppy')],
    'tar': [('mimetypes', 'application-x-tar')],
    'text-csv': [('mimetypes', 'x-office-spreadsheet')],
    'text-x-boo': [('mimetypes', 'text-x-generic')],
    'text-x-c++src': [('mimetypes', 'text-x-cpp')],
    'text-x-csrc': [('mimetypes', 'text-x-c')],
    'text-x-generic-template': [('mimetypes', 'text-x-generic')],
    'text-x-log': [('mimetypes', 'text-x-generic')],
    'text-x-makefile': [('mimetypes', 'text-x-script')],
    'text-x-opml+xml': [('mimetypes', 'text-x-generic')],
    'template_source': [('mimetypes', 'text-x-generic')],
    'tgz': [('mimetypes', 'application-x-compressed-tar')],
    'trashcan_empty': [('places', 'user-trash')],
    'volume-knob': [('apps', 'multimedia-volume-control')],
    'www': [('mimetypes', 'text-html')],
    'x-firmware': [('mimetypes', 'application-x-executable')],
    'x-office-document-template': [('mimetypes', 'x-office-document')],
    'x-office-drawing-template': [('mimetypes', 'x-office-drawing')],
    'x-office-presentation-template': [('mimetypes', 'x-office-presentation')],
    'x-office-spreadsheet-template': [('mimetypes', 'x-office-spreadsheet')],
    'x-package-repository': [('mimetypes', 'application-x-archive')],
    'gnome-fs-client': [('devices', 'computer')],
    'gcolor2': [('actions', 'color-select')],
    'gnome-mime-application-x-jar': [('mimetypes', 'application-x-java-archive')],
    'gnome-mime-application-x-killustrator': [('mimetypes', 'x-office-drawing')],
    'gnome-mime-application-x-php': [('mimetypes', 'text-x-php')],
    'gnome-mime-application-x-python-bytecode': [('mimetypes', 'text-x-python')],
    'gnome-package': [('mimetypes', 'application-x-archive')],
    'gnome-window-manager': [('apps', 'preferences-desktop-theme-windowdecorations')],
    'hdd_unmount': [('devices', 'drive-harddisk')],
    'joystick': [('devices', 'input-gaming')],
    'novell-button': [('apps', 'distributor-logo')],
    'printer1': [('devices', 'printer')],
    'process-working': [('status', 'process-working')],
    'application-x-mono-develop-xib': [('mimetypes', 'text-x-generic')],
    'application-vnd.openofficeorg.extension': [('mimetypes', 'application-x-archive')],
    'application-pgp-encrypted': [('mimetypes', 'application-pgp')],
    'redhat-network-server': [('places', 'network-server')],
    'stock_certificate': [('mimetypes', 'application-certificate')],
    'visor': [('apps', 'utilities-terminal')],
    'yast_idetude': [('devices', 'drive-harddisk')],
    'yast_joystick': [('devices', 'input-gaming')],
    'zip': [('mimetypes', 'application-x-zip')],
}


def semantic_alias_pairs(category: str, stem: str) -> list[tuple[str, str]]:
    """Return explicit and rule-derived semantic alias pairs."""
    pairs = [(category, stem)]
    pairs.extend(ICON_SEMANTIC_ALIASES.get(stem, []))
    if category == 'mimetypes':
        pairs.extend(mimetype_alias_pairs(stem))

    deduped = []
    seen = set()
    for pair in pairs:
        if pair not in seen:
            seen.add(pair)
            deduped.append(pair)
    return deduped


def office_family_aliases(stem: str) -> list[tuple[str, str]]:
    """Collapse office-related MIME stems onto canonical office icons."""
    if any(token in stem for token in ('spreadsheet', 'excel', 'calc', 'lotus-1-2-3', 'kspread', 'gnumeric', 'applix-spreadsheet')):
        return [('mimetypes', 'x-office-spreadsheet')]
    if any(token in stem for token in ('presentation', 'powerpoint', 'impress', 'magicpoint', 'kpresenter')):
        return [('mimetypes', 'x-office-presentation')]
    if any(token in stem for token in ('drawing', 'draw', 'graphics')):
        return [('mimetypes', 'x-office-drawing')]
    if any(token in stem for token in ('address-book', 'vcard')):
        return [('mimetypes', 'x-office-address-book')]
    if any(token in stem for token in ('calendar', 'planner')):
        return [('mimetypes', 'x-office-calendar')]
    if any(token in stem for token in (
        'document',
        'word',
        'writer',
        'wordprocessing',
        'text',
        'rtf',
        'postscript',
        'pdf',
        'msword',
        'wordperfect',
        'abiword',
        'kword',
        'applix-word',
    )):
        return [('mimetypes', 'x-office-document')]
    return []


def mimetype_alias_pairs(stem: str) -> list[tuple[str, str]]:
    """Return rule-derived aliases for legacy or family MIME icon names."""
    pairs = []
    gnome_prefix = 'gnome-mime-'
    if stem.startswith(gnome_prefix):
        stripped = stem[len(gnome_prefix):]
        pairs.append(('mimetypes', stripped))
        if stripped != stem:
            pairs.extend(mimetype_alias_pairs(stripped))

    pairs.extend(office_family_aliases(stem))

    if stem.startswith('openofficeorg-') or stem.startswith('openofficeorg3-'):
        pairs.extend(office_family_aliases(stem.split('-', 1)[1]))

    office_prefixes = (
        'application-vnd.openxmlformats-officedocument.',
        'application-vnd.ms-',
        'application-vnd.oasis.opendocument.',
        'application-vnd.stardivision.',
        'application-vnd.sun.xml.',
    )
    if any(stem.startswith(prefix) for prefix in office_prefixes):
        pairs.extend(office_family_aliases(stem))

    if any(token in stem for token in ('7z', 'zip', 'stuffit', 'lha', 'lhz', 'lzma', 'cpio', 'compress')):
        pairs.append(('mimetypes', 'application-x-archive'))
    if any(token in stem for token in ('realmedia', 'video', 'flash')):
        pairs.append(('mimetypes', 'video-x-generic'))
    if any(token in stem for token in ('font', 'afm', 'ttf', 'pcf', 'psf', 'bdf')):
        pairs.append(('mimetypes', 'font-x-generic'))
    if 'xhtml+xml' in stem:
        pairs.append(('mimetypes', 'text-html'))
    if any(token in stem for token in ('tex', 'dvi')):
        pairs.append(('mimetypes', 'text-x-tex'))
    if 'zsh' in stem:
        pairs.append(('mimetypes', 'application-x-shellscript'))
    if 'xcf' in stem:
        pairs.append(('mimetypes', 'image-x-compressed-xcf'))
    if 'scribus' in stem:
        pairs.append(('apps', 'scribus'))
    if 'desktop' in stem:
        pairs.append(('places', 'user-desktop'))

    return pairs


def _path_to_str(path: Path) -> str:
    """Return a stable POSIX path string for manifests and reports."""
    return path.as_posix()


def _relative_to_known_roots(path: Path, *roots: Path) -> str:
    """Serialize a path relative to an input/output root when possible."""
    for root in roots:
        try:
            return _path_to_str(path.relative_to(root))
        except ValueError:
            continue
    return _path_to_str(path)


def detect_cuda_fastpath() -> dict:
    """Detect whether the OpenCV CUDA preprocessing fastpath is usable."""
    info = {
        'available': False,
        'backend': 'cpu',
        'device_name': None,
        'device_count': 0,
        'reason': 'CUDA preprocessing unavailable',
    }

    try:
        import cv2
    except Exception as exc:
        info['reason'] = f'cv2 import failed: {exc}'
        return info

    try:
        device_count = cv2.cuda.getCudaEnabledDeviceCount()
    except Exception as exc:
        info['reason'] = f'cv2.cuda probe failed: {exc}'
        return info

    if device_count < 1:
        info['reason'] = 'No CUDA devices visible to OpenCV'
        return info

    info['available'] = True
    info['backend'] = 'opencv-cuda'
    info['device_count'] = device_count
    info['reason'] = 'OpenCV CUDA preprocessing available'

    try:
        import cupy as cp

        props = cp.cuda.runtime.getDeviceProperties(0)
        device_name = props['name']
        if isinstance(device_name, bytes):
            device_name = device_name.decode()
        info['device_name'] = device_name
    except Exception:
        info['device_name'] = 'CUDA device 0'

    return info


def resolve_preprocess_backend(requested_backend: str, cuda_info: dict) -> str:
    """Resolve the preprocessing backend for this run."""
    if requested_backend == 'cpu':
        return 'cpu'
    if requested_backend == 'cuda':
        if not cuda_info['available']:
            raise RuntimeError(cuda_info['reason'])
        return 'cuda'
    if cuda_info['available']:
        return 'cuda'
    return 'cpu'


def preprocess_png_cpu(input_png: Path, temp_bitmap: Path) -> bool:
    """Convert PNG to a thresholded grayscale bitmap using ImageMagick."""
    try:
        subprocess.run([
            'convert', str(input_png),
            '-colorspace', 'Gray',
            '-threshold', '50%',
            '-negate',
            str(temp_bitmap),
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ERROR preprocessing {input_png.name}: {exc}", file=sys.stderr)
        return False


def preprocess_png_cuda(input_png: Path, temp_bitmap: Path) -> bool:
    """Convert PNG to a thresholded grayscale bitmap with OpenCV CUDA."""
    try:
        import cv2
        import numpy as np
    except Exception as exc:
        print(f"  ERROR enabling CUDA preprocessing for {input_png.name}: {exc}", file=sys.stderr)
        return False

    image = cv2.imread(str(input_png), cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"  ERROR preprocessing {input_png.name}: could not read image", file=sys.stderr)
        return False

    try:
        gpu = cv2.cuda_GpuMat()
        gpu.upload(image)

        if image.ndim == 2:
            gray = gpu
        elif image.shape[2] == 4:
            gray = cv2.cuda.cvtColor(gpu, cv2.COLOR_BGRA2GRAY)
        else:
            gray = cv2.cuda.cvtColor(gpu, cv2.COLOR_BGR2GRAY)

        _, thresholded = cv2.cuda.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        inverted = cv2.cuda.bitwise_not(thresholded)
        bitmap = inverted.download()
        bitmap = np.ascontiguousarray(bitmap)
        if not cv2.imwrite(str(temp_bitmap), bitmap):
            print(f"  ERROR preprocessing {input_png.name}: could not write bitmap", file=sys.stderr)
            return False
        return True
    except Exception as exc:
        print(f"  ERROR CUDA preprocessing {input_png.name}: {exc}", file=sys.stderr)
        return False


def preprocess_png(input_png: Path, temp_bitmap: Path, backend: str) -> bool:
    """Convert a PNG into a bitmap input that potrace can consume."""
    if backend == 'cuda':
        return preprocess_png_cuda(input_png, temp_bitmap)
    return preprocess_png_cpu(input_png, temp_bitmap)


def vectorize_to_svg(temp_bitmap: Path, output_svg: Path, original_png: Path) -> bool:
    """Convert a temporary bitmap into SVG with potrace."""
    try:
        result = subprocess.run([
            'identify', '-format', '%w %h', str(original_png)
        ], check=True, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split())

        subprocess.run([
            'potrace',
            str(temp_bitmap),
            '-s',
            '-t', '1',
            '-a', '1.5',
            '-O', '0.1',
            '--group',
            '-W', str(width),
            '-H', str(height),
            '-o', str(output_svg),
        ], check=True, capture_output=True)

        svgo = which('svgo')
        if svgo:
            subprocess.run([
                svgo, str(output_svg),
                '-o', str(output_svg),
                '--multipass',
            ], check=True, capture_output=True)

        return True
    except subprocess.CalledProcessError as exc:
        print(f"  ERROR vectorizing {temp_bitmap.name}: {exc}", file=sys.stderr)
        return False


def discover_pngs(input_dir: Path, recursive: bool) -> list[Path]:
    """Return PNG files discovered under the input directory."""
    if recursive:
        return sorted(path for path in input_dir.rglob('*.png') if path.is_file())
    return sorted(path for path in input_dir.glob('*.png') if path.is_file())


def infer_icon_category(relative_png: Path) -> str | None:
    """Infer the icon category from a path inside the installed icon tree."""
    parts = relative_png.parts
    if 'Synthesis-Dark-Icons' not in parts:
        return None

    idx = parts.index('Synthesis-Dark-Icons')
    if len(parts) <= idx + 2:
        return None

    if parts[idx + 1] == 'scalable':
        return parts[idx + 2] if len(parts) > idx + 2 else None
    return parts[idx + 2] if len(parts) > idx + 2 else None


def infer_style_skin(relative_png: Path) -> str:
    """Infer the universal art skin owner for an asset."""
    category = infer_icon_category(relative_png)
    if category in MATE_ICON_CATEGORIES:
        return 'mate'
    if category in TELA_ICON_CATEGORIES:
        return 'tela'
    return 'n/a'


def infer_semantic_id(relative_png: Path) -> str:
    """Infer a stable semantic identifier from a PNG path."""
    category = infer_icon_category(relative_png)
    if category is not None:
        return f"icon/{category}/{relative_png.stem}"
    if relative_png.parts[:3] == ('kde', 'cursors', 'build'):
        return f"cursor/{relative_png.stem}"
    return _path_to_str(relative_png.with_suffix(''))


def is_reference_raster(relative_png: Path) -> bool:
    """Return whether a PNG is preview/reference art rather than source authority."""
    parts = relative_png.parts
    name = relative_png.name

    if name == 'thumbnail.png':
        return True

    if parts[:2] == ('upstream', 'eggwm'):
        return True

    if parts[:2] == ('upstream', 'tela-circle') and name in {'preview.png', 'preview-light.png'}:
        return True

    if parts[:2] == ('kde', 'cursors') and name == 'preview.png':
        return True

    if len(parts) >= 3 and parts[:2] == ('kde', 'sddm') and name == 'preview.png':
        return True

    if 'previews' in parts and name in {'preview.png', 'splash.png', 'fullscreenpreview.png'}:
        return True

    if parts[:2] == ('gnome-shell', 'assets') and name == 'noise-texture.png':
        return True

    return False


def is_simple_runtime_ui(relative_png: Path) -> bool:
    """Return whether a complex-ui path is safe for early SVG promotion."""
    parts = relative_png.parts
    if parts[:2] == ('gnome-shell', 'assets') and relative_png.stem in GNOME_SHELL_SIMPLE_UI:
        return True
    if parts[:3] == ('cinnamon', 'common-assets', 'misc') and relative_png.stem in CINNAMON_SIMPLE_UI:
        return True
    return False


def icon_authority_candidates(repo_root: Path, category: str, stem: str) -> list[Path]:
    """Return prioritized icon SVG candidates for a semantic icon concept."""
    candidates = []
    seen = set()

    def add(path: Path):
        key = _path_to_str(path)
        if key not in seen:
            seen.add(key)
            candidates.append(path)

    search_pairs = semantic_alias_pairs(category, stem)

    for search_category, search_stem in search_pairs:
        search_stems = {
            search_stem,
            search_stem.replace('_', '-'),
            search_stem.replace('-', '_'),
        }
        for normalized_stem in search_stems:
            add(repo_root / 'icons' / 'Synthesis-Dark-Icons' / 'scalable' / search_category / f'{normalized_stem}.svg')
            add(repo_root / 'icons' / 'Synthesis-Dark-Icons' / 'scalable' / search_category / f'{normalized_stem}-symbolic.svg')
            add(repo_root / 'icons' / 'Synthesis-Dark-Icons' / 'scalable' / search_category / f'{normalized_stem}_symbolic.svg')
            add(repo_root / 'upstream' / 'tela-circle' / 'src' / 'scalable' / search_category / f'{normalized_stem}.svg')
            add(repo_root / 'upstream' / 'tela-circle' / 'links' / 'scalable' / search_category / f'{normalized_stem}.svg')
            add(repo_root / 'upstream' / 'tela-circle' / 'src' / 'symbolic' / search_category / f'{normalized_stem}-symbolic.svg')
            add(repo_root / 'upstream' / 'tela-circle' / 'src' / 'symbolic' / search_category / f'{normalized_stem}.svg')
            if search_category == 'places':
                add(repo_root / 'upstream' / 'tela-circle' / 'src' / 'scalable' / 'places-normal' / f'{normalized_stem}.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'src' / 'scalable' / 'places-circle' / f'{normalized_stem}.svg')
            for size in ('16', '22', '24', '32'):
                add(repo_root / 'upstream' / 'tela-circle' / 'src' / size / search_category / f'{normalized_stem}.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'src' / size / search_category / f'{normalized_stem}-symbolic.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'src' / size / search_category / f'{normalized_stem}_symbolic.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'links' / size / search_category / f'{normalized_stem}.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'links' / size / search_category / f'{normalized_stem}-symbolic.svg')
                add(repo_root / 'upstream' / 'tela-circle' / 'links' / size / search_category / f'{normalized_stem}_symbolic.svg')

    return candidates


def canonical_output_svg_path(output_root: Path, relative_png: Path) -> Path:
    """Map repo rasters onto their canonical SVG authority location."""
    parts = relative_png.parts
    if parts[:1] == ('xfwm4',) and len(parts) == 2:
        return output_root / 'xfwm4' / 'assets' / f'{relative_png.stem}.svg'
    if parts[:1] == ('metacity-1',) and len(parts) == 2:
        return output_root / 'metacity-1' / 'assets' / f'{relative_png.stem}.svg'
    return (output_root / relative_png).with_suffix('.svg')


def find_authoritative_svg(input_dir: Path, relative_png: Path, output_dir: Path) -> Path | None:
    """Find an existing SVG authority for a PNG if one already exists."""
    preferred_authority = preferred_authority_for(input_dir, relative_png)
    if preferred_authority is not None:
        return preferred_authority

    input_png = input_dir / relative_png
    sibling_svg = input_png.with_suffix('.svg')
    if sibling_svg.exists():
        return sibling_svg

    known_authority = find_known_source_authority(input_dir, relative_png)
    if known_authority is not None:
        return known_authority

    parts = relative_png.parts
    if 'Synthesis-Dark-Icons' in parts:
        category = infer_icon_category(relative_png)
        if category is not None:
            idx = parts.index('Synthesis-Dark-Icons')
            theme_root = input_dir.joinpath(*parts[:idx + 1])
            candidate = theme_root / 'scalable' / category / f"{relative_png.stem}.svg"
            if candidate.exists():
                return candidate

    output_svg = canonical_output_svg_path(output_dir, relative_png)
    if output_svg.exists():
        return output_svg
    return None


def find_known_source_authority(input_dir: Path, relative_png: Path) -> Path | None:
    """Resolve known repo-specific SVG authorities for raster outputs."""
    parts = relative_png.parts
    if not parts:
        return None

    top = parts[0]
    repo_root = input_dir
    raster_wrapper = repo_root / 'src' / 'raster_wrappers' / relative_png.with_suffix('.svg')
    if raster_wrapper.exists():
        return raster_wrapper

    if top == 'icons':
        category = infer_icon_category(relative_png)
        if category is not None:
            candidate = repo_root / 'src' / 'icons_backend' / 'geometry' / category / f"{relative_png.stem}.svg"
            if candidate.exists():
                return candidate
            for candidate in icon_authority_candidates(repo_root, category, relative_png.stem):
                if candidate.exists():
                    return candidate

    if top == 'assets':
        candidate = repo_root / 'src' / 'assets' / 'gtk3-4' / f"{relative_png.stem}.svg"
        if candidate.exists():
            return candidate

    if parts[:2] == ('gnome-shell', 'assets') and relative_png.name in {
        'corner-ripple-ltr.png',
        'corner-ripple-rtl.png',
    }:
        candidate = repo_root / 'gnome-shell' / 'assets' / 'corner-ripple.svg'
        if candidate.exists():
            return candidate

    if top == 'gtk-2.0' and len(parts) >= 2 and parts[1] == 'assets':
        candidate = repo_root / 'src' / 'assets' / 'gtk2' / 'assets.svg'
        if candidate.exists():
            return candidate

    if top == 'xfwm4':
        candidate = repo_root / 'xfwm4' / 'assets' / f"{relative_png.stem}.svg"
        if candidate.exists():
            return candidate

    if top == 'metacity-1':
        assets_dir = repo_root / 'metacity-1' / 'assets'
        stem = relative_png.stem
        for base in ('close', 'maximize', 'menu', 'minimize', 'unmaximize'):
            if stem.startswith(base):
                if 'prelight' in stem:
                    candidate = assets_dir / f"{base}-hover.svg"
                    if candidate.exists():
                        return candidate
                candidate = assets_dir / f"{base}.svg"
                if candidate.exists():
                    return candidate
        candidate = assets_dir / f"{stem}.svg"
        if candidate.exists():
            return candidate

    if top == 'kde' and parts[:3] == ('kde', 'cursors', 'preview.png'):
        candidate = repo_root / 'kde' / 'cursors' / 'src' / 'cursors.svg'
        if candidate.exists():
            return candidate

    return None


def classify_asset(
    input_dir: Path,
    relative_png: Path,
    output_dir: Path,
    include_existing_svg: bool,
) -> dict:
    """Classify a PNG into an execution/reporting queue."""
    input_png = input_dir / relative_png
    output_svg = (output_dir / relative_png).with_suffix('.svg')
    style_skin = infer_style_skin(relative_png)
    semantic_id = infer_semantic_id(relative_png)
    authoritative_svg = find_authoritative_svg(input_dir, relative_png, output_dir)
    top = relative_png.parts[0] if relative_png.parts else '.'

    source_class = 'complex_ui_source'
    batch_priority = 'review-later'
    reason = 'Needs review'
    source_authority = None

    if is_reference_raster(relative_png):
        source_class = 'reference_raster'
        batch_priority = 'review-later'
        reason = 'Preview, screenshot, upstream reference, or external-resource raster'
    elif '@2' in input_png.name:
        source_class = 'derived_hidpi'
        batch_priority = 'exclude-derived'
        reason = 'HiDPI raster derived from a base asset'
    elif relative_png.parts[:3] == ('kde', 'cursors', 'build'):
        source_class = 'generated_raster'
        batch_priority = 'exclude-derived'
        reason = 'Generated by the cursor build pipeline'
        source_authority = 'kde/cursors/src/cursors.svg'
    elif top == 'xfwm4' and any(part.endswith('hdpi') or part.endswith('xhdpi') for part in relative_png.parts):
        source_class = 'generated_raster'
        batch_priority = 'exclude-derived'
        reason = 'Rendered XFWM size variant'
        source_authority = 'xfwm4/render-assets.sh'
    elif authoritative_svg is not None and not include_existing_svg:
        source_class = 'already_has_authoritative_svg'
        batch_priority = 'safe-batch-generation'
        reason = 'Authoritative SVG already exists'
        source_authority = _relative_to_known_roots(authoritative_svg, input_dir, output_dir)
    elif top == 'icons':
        source_class = 'complex_icon_source'
        batch_priority = 'icon-family-reconciliation'
        reason = 'Raster icon without authoritative scalable source'
    elif is_simple_runtime_ui(relative_png):
        source_class = 'simple_ui_source'
        batch_priority = 'non-icon-first'
        reason = 'Runtime UI raster suitable for direct SVG promotion'
    elif top in {'gtk-2.0', 'assets', 'xfwm4', 'metacity-1'}:
        source_class = 'simple_ui_source'
        batch_priority = 'non-icon-first'
        reason = 'Theme UI raster suitable for early SVG authority work'
    elif top in {'gnome-shell', 'cinnamon', 'kde', 'upstream'}:
        source_class = 'complex_ui_source'
        batch_priority = 'non-icon-first'
        reason = 'Non-icon raster that needs source review before conversion'
    elif top in {'Art', 'docs'} or input_png.name == 'thumbnail.png':
        source_class = 'reference_raster'
        batch_priority = 'review-later'
        reason = 'Reference, preview, or documentation raster'

    output_svg = canonical_output_svg_path(output_dir, relative_png)

    return {
        'input_png': _path_to_str(input_png),
        'relative_png': _path_to_str(relative_png),
        'output_svg': _path_to_str(output_svg),
        'status': 'pending' if batch_priority != 'exclude-derived' else 'skipped',
        'reason': reason,
        'source_class': source_class,
        'batch_priority': batch_priority,
        'family': 'icon' if top == 'icons' else top,
        'style_skin': style_skin,
        'semantic_id': semantic_id,
        'source_authority': source_authority,
    }


def build_asset_manifest(
    input_dir: Path,
    output_dir: Path,
    recursive: bool,
    include_existing_svg: bool,
) -> list[dict]:
    """Classify PNG files into migration queues."""
    manifest = []
    for input_png in discover_pngs(input_dir, recursive):
        relative_png = input_png.relative_to(input_dir)
        manifest.append(
            classify_asset(input_dir, relative_png, output_dir, include_existing_svg)
        )
    return manifest


def build_priority_summary(manifest: list[dict]) -> dict:
    """Summarize the manifest for CLI and Markdown reporting."""
    return {
        'total': len(manifest),
        'by_priority': Counter(entry['batch_priority'] for entry in manifest),
        'by_source_class': Counter(entry['source_class'] for entry in manifest),
        'pending_non_icon_top_level': Counter(
            Path(entry['relative_png']).parts[0]
            for entry in manifest
            if entry['batch_priority'] == 'non-icon-first'
        ),
        'icon_skin_counts': Counter(
            entry['style_skin']
            for entry in manifest
            if entry['batch_priority'] == 'icon-family-reconciliation'
        ),
    }


def render_priority_report(
    manifest: list[dict],
    input_dir: Path,
    output_dir: Path,
    workers: int,
    cuda_info: dict,
) -> str:
    """Render a concise Markdown migration report from the manifest."""
    summary = build_priority_summary(manifest)
    lines = [
        "# SVG Migration Report",
        "",
        "## Summary",
        f"- Input root: `{input_dir}`",
        f"- Output root: `{output_dir}`",
        f"- Default worker plan: `{workers}` CPU process workers",
        f"- Total PNG files discovered: `{summary['total']}`",
        f"- `non-icon-first`: `{summary['by_priority'].get('non-icon-first', 0)}`",
        f"- `icon-family-reconciliation`: `{summary['by_priority'].get('icon-family-reconciliation', 0)}`",
        f"- `safe-batch-generation`: `{summary['by_priority'].get('safe-batch-generation', 0)}`",
        f"- `exclude-derived`: `{summary['by_priority'].get('exclude-derived', 0)}`",
        f"- `review-later`: `{summary['by_priority'].get('review-later', 0)}`",
        "",
        "## Priority 1: Non-Icon First",
    ]

    non_icon_counts = summary['pending_non_icon_top_level']
    if non_icon_counts:
        for top_level, count in non_icon_counts.most_common():
            lines.append(f"- `{top_level}`: `{count}`")
    else:
        lines.append("- None")

    lines.extend([
        "",
        "## Priority 2: Icon-Family Reconciliation",
        (
            f"- Pending icon rasters without authoritative scalable SVG: "
            f"`{summary['by_priority'].get('icon-family-reconciliation', 0)}`"
        ),
        f"- `mate` skin queue: `{summary['icon_skin_counts'].get('mate', 0)}`",
        f"- `tela` skin queue: `{summary['icon_skin_counts'].get('tela', 0)}`",
        "- Reconcile by `semantic_id` and shared geometry, not by basename alone.",
        "",
        "## Priority 3: Safe Batch Generation",
        (
            f"- PNGs that already have authoritative SVGs and can move straight to render-only handling: "
            f"`{summary['by_priority'].get('safe-batch-generation', 0)}`"
        ),
        "",
        "## Derived Or Excluded",
        (
            f"- Generated or derived rasters already explained by build scripts or higher-resolution outputs: "
            f"`{summary['by_priority'].get('exclude-derived', 0)}`"
        ),
        "",
        "## Execution Defaults",
        f"- CPU-first execution on the local host with `{workers}` process workers.",
        "- Baseline toolchain: Inkscape, ImageMagick, potrace, and svgo.",
    ])

    if cuda_info['available']:
        lines.append(
            f"- CUDA preprocessing fastpath available via `{cuda_info['backend']}` on `{cuda_info['device_name']}`."
        )
    else:
        lines.append(f"- CUDA preprocessing fastpath unavailable: {cuda_info['reason']}.")

    lines.append(
        "- Optional future fastpath: add `resvg` or `rsvg-convert` for faster CPU-side raster generation."
    )

    return "\n".join(lines) + "\n"


def build_icon_registry(manifest: list[dict]) -> list[dict]:
    """Aggregate icon entries into semantic reconciliation groups."""
    registry = {}

    for entry in manifest:
        if entry['family'] != 'icon':
            continue

        semantic_id = entry['semantic_id']
        record = registry.setdefault(semantic_id, {
            'semantic_id': semantic_id,
            'style_skin': entry['style_skin'],
            'category': semantic_id.split('/')[1] if semantic_id.count('/') >= 2 else 'unknown',
            'installed_outputs': [],
            'authoritative_svg_candidates': set(),
            'batch_priorities': Counter(),
            'source_classes': Counter(),
        })

        record['installed_outputs'].append(entry['relative_png'])
        record['batch_priorities'][entry['batch_priority']] += 1
        record['source_classes'][entry['source_class']] += 1
        if entry['source_authority']:
            record['authoritative_svg_candidates'].add(entry['source_authority'])

    serialized = []
    for semantic_id, record in sorted(registry.items()):
        serialized.append({
            'semantic_id': semantic_id,
            'style_skin': record['style_skin'],
            'category': record['category'],
            'installed_outputs': sorted(record['installed_outputs']),
            'installed_output_count': len(record['installed_outputs']),
            'authoritative_svg_candidates': sorted(record['authoritative_svg_candidates']),
            'has_authoritative_svg': bool(record['authoritative_svg_candidates']),
            'batch_priorities': dict(record['batch_priorities']),
            'source_classes': dict(record['source_classes']),
        })
    return serialized


def build_icon_stem_collisions(manifest: list[dict]) -> list[dict]:
    """Group icon outputs by stem to highlight high-fanout merge candidates."""
    collisions = {}

    for entry in manifest:
        if entry['family'] != 'icon':
            continue

        stem = Path(entry['relative_png']).stem
        category = infer_icon_category(Path(entry['relative_png'])) or 'unknown'
        record = collisions.setdefault(stem, {
            'stem': stem,
            'semantic_ids': set(),
            'categories': set(),
            'style_skins': set(),
            'installed_outputs': [],
            'authoritative_svg_candidates': set(),
        })
        record['semantic_ids'].add(entry['semantic_id'])
        record['categories'].add(category)
        record['style_skins'].add(entry['style_skin'])
        record['installed_outputs'].append(entry['relative_png'])
        if entry['source_authority']:
            record['authoritative_svg_candidates'].add(entry['source_authority'])

    serialized = []
    for stem, record in collisions.items():
        if len(record['installed_outputs']) < 2:
            continue
        serialized.append({
            'stem': stem,
            'semantic_ids': sorted(record['semantic_ids']),
            'categories': sorted(record['categories']),
            'style_skins': sorted(record['style_skins']),
            'installed_outputs': sorted(record['installed_outputs']),
            'installed_output_count': len(record['installed_outputs']),
            'authoritative_svg_candidates': sorted(record['authoritative_svg_candidates']),
        })

    serialized.sort(key=lambda item: (-item['installed_output_count'], item['stem']))
    return serialized


def render_icon_reconciliation_report(manifest: list[dict], icon_registry: list[dict]) -> str:
    """Render a Markdown report focused on icon dedupe and shared-backend work."""
    icon_entries = [entry for entry in manifest if entry['family'] == 'icon']
    by_skin = Counter(entry['style_skin'] for entry in icon_entries)
    by_priority = Counter(entry['batch_priority'] for entry in icon_entries)
    collisions = build_icon_stem_collisions(manifest)
    safe_ids = sum(1 for item in icon_registry if item['has_authoritative_svg'])
    unresolved_ids = sum(1 for item in icon_registry if not item['has_authoritative_svg'])
    unresolved_registry = [
        item for item in icon_registry if not item['has_authoritative_svg']
    ]
    unresolved_registry.sort(
        key=lambda item: (-item['installed_output_count'], item['semantic_id'])
    )

    lines = [
        "# Icon Reconciliation Report",
        "",
        "## Summary",
        f"- Icon PNG outputs discovered: `{len(icon_entries)}`",
        f"- Unique icon semantic IDs: `{len(icon_registry)}`",
        f"- Semantic IDs with authoritative SVG candidates: `{safe_ids}`",
        f"- Semantic IDs still needing shared-backend reconciliation: `{unresolved_ids}`",
        f"- `mate` skin outputs: `{by_skin.get('mate', 0)}`",
        f"- `tela` skin outputs: `{by_skin.get('tela', 0)}`",
        f"- `safe-batch-generation` outputs: `{by_priority.get('safe-batch-generation', 0)}`",
        f"- `icon-family-reconciliation` outputs: `{by_priority.get('icon-family-reconciliation', 0)}`",
        "",
        "## Shared Backend Priorities",
        "- Promote semantic IDs with authoritative scalable SVGs into the shared backend first.",
        "- Use unresolved semantic IDs as the redraw and reconciliation queue.",
        "- Keep backend output ownership by semantic ID, not by installed filename.",
        "",
        "## Highest-Fanout Geometry Candidates",
    ]

    for collision in collisions[:25]:
        lines.append(
            f"- `{collision['stem']}`: `{collision['installed_output_count']}` outputs, "
            f"categories=`{', '.join(collision['categories'])}`, skins=`{', '.join(collision['style_skins'])}`"
        )
    if not collisions:
        lines.append("- None")

    lines.extend([
        "",
        "## First Shared-Backend Tranche",
        "- Start with semantic IDs that already have authoritative SVG candidates and many installed outputs.",
        "- After those are backend-owned, reconcile unresolved `mate` and `tela` IDs into shared geometry plus skin layers.",
        "",
        "## Sample Unresolved Semantic IDs",
    ])

    for item in unresolved_registry[:20]:
        lines.append(
            f"- `{item['semantic_id']}`: `{item['installed_output_count']}` outputs, skin=`{item['style_skin']}`"
        )
    if not unresolved_registry:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def select_execution_candidates(
    manifest: list[dict],
    allow_complex_ui: bool,
    allow_icon_raster: bool,
) -> list[dict]:
    """Return the manifest entries that should be vectorized in this run."""
    allowed_classes = {'simple_ui_source'}
    if allow_complex_ui:
        allowed_classes.add('complex_ui_source')
    if allow_icon_raster:
        allowed_classes.add('complex_icon_source')

    return [
        entry
        for entry in manifest
        if entry['source_class'] in allowed_classes
    ]


def process_asset(input_png: Path, input_root: Path, output_dir: Path, preprocess_backend: str) -> tuple:
    """Process a single PNG asset to an SVG path that mirrors the input tree."""
    if '@2' in input_png.name:
        return (str(input_png), 'skipped', 'HiDPI variant')

    relative_png = input_png.relative_to(input_root)
    output_svg = canonical_output_svg_path(output_dir, relative_png)
    temp_bitmap = output_svg.with_suffix('.pgm')

    try:
        output_svg.parent.mkdir(parents=True, exist_ok=True)
        if not preprocess_png(input_png, temp_bitmap, preprocess_backend):
            return (str(input_png), 'failed', 'preprocessing')

        if not vectorize_to_svg(temp_bitmap, output_svg, input_png):
            return (str(input_png), 'failed', 'vectorization')

        if temp_bitmap.exists():
            temp_bitmap.unlink()

        return (str(input_png), 'success', str(output_svg))
    except Exception as exc:
        return (str(input_png), 'failed', str(exc))


def main():
    parser = argparse.ArgumentParser(
        description='Vectorize PNG assets to SVG sources'
    )
    parser.add_argument('--input', required=True, help='Input directory with PNGs')
    parser.add_argument('--output', required=True, help='Output directory for SVGs')
    parser.add_argument(
        '--workers',
        type=int,
        default=DEFAULT_WORKERS,
        help=f'Parallel workers (default: {DEFAULT_WORKERS})',
    )
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Scan subdirectories recursively and preserve the relative directory layout',
    )
    parser.add_argument(
        '--manifest',
        type=Path,
        default=None,
        help='Write a JSON manifest describing each discovered PNG and its migration classification',
    )
    parser.add_argument(
        '--report-markdown',
        type=Path,
        default=None,
        help='Write a Markdown migration report summarizing the manifest priorities',
    )
    parser.add_argument(
        '--icon-report-markdown',
        type=Path,
        default=None,
        help='Write a Markdown report focused on icon reconciliation and dedupe',
    )
    parser.add_argument(
        '--icon-registry-json',
        type=Path,
        default=None,
        help='Write a machine-readable JSON registry of icon semantic IDs and current outputs',
    )
    parser.add_argument(
        '--include-existing-svg',
        action='store_true',
        help='Include PNGs even when a sibling or authoritative SVG already exists',
    )
    parser.add_argument(
        '--allow-complex-ui',
        action='store_true',
        help='Allow execution against complex non-icon UI assets after review',
    )
    parser.add_argument(
        '--allow-icon-raster',
        action='store_true',
        help='Allow execution against raster icons without authoritative scalable SVGs',
    )
    parser.add_argument(
        '--preprocess-backend',
        choices=('auto', 'cpu', 'cuda'),
        default='auto',
        help='Bitmap preprocessing backend before potrace (default: auto)',
    )

    args = parser.parse_args()
    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"ERROR: Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    cuda_info = detect_cuda_fastpath()
    manifest = build_asset_manifest(
        input_dir,
        output_dir,
        recursive=args.recursive,
        include_existing_svg=args.include_existing_svg,
    )
    execution_candidates = select_execution_candidates(
        manifest,
        allow_complex_ui=args.allow_complex_ui,
        allow_icon_raster=args.allow_icon_raster,
    )
    summary = build_priority_summary(manifest)

    print("=== Synthesis-Dark Asset Vectorization ===")
    print(f"Input:  {input_dir} ({len(manifest)} PNG files discovered)")
    print(f"Output: {output_dir}")
    print(f"Non-icon-first: {summary['by_priority'].get('non-icon-first', 0)}")
    print(f"Icon reconciliation: {summary['by_priority'].get('icon-family-reconciliation', 0)}")
    print(f"Safe batch generation: {summary['by_priority'].get('safe-batch-generation', 0)}")
    print(f"Derived/excluded: {summary['by_priority'].get('exclude-derived', 0)}")
    print(f"Execution candidates for this run: {len(execution_candidates)}")
    if cuda_info['available']:
        print(f"CUDA fastpath: available ({cuda_info['device_name']})")
    else:
        print(f"CUDA fastpath: unavailable ({cuda_info['reason']})")
    print()

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f"Wrote manifest: {args.manifest}")
        print()

    if args.report_markdown:
        args.report_markdown.parent.mkdir(parents=True, exist_ok=True)
        report = render_priority_report(
            manifest,
            input_dir,
            output_dir,
            args.workers,
            cuda_info,
        )
        args.report_markdown.write_text(report, encoding='utf-8')
        print(f"Wrote report: {args.report_markdown}")
        print()

    icon_registry = build_icon_registry(manifest)

    if args.icon_registry_json:
        args.icon_registry_json.parent.mkdir(parents=True, exist_ok=True)
        args.icon_registry_json.write_text(json.dumps(icon_registry, indent=2), encoding='utf-8')
        print(f"Wrote icon registry: {args.icon_registry_json}")
        print()

    if args.icon_report_markdown:
        args.icon_report_markdown.parent.mkdir(parents=True, exist_ok=True)
        icon_report = render_icon_reconciliation_report(manifest, icon_registry)
        args.icon_report_markdown.write_text(icon_report, encoding='utf-8')
        print(f"Wrote icon report: {args.icon_report_markdown}")
        print()

    if args.dry_run:
        for entry in manifest[:10]:
            print(
                f"  {entry['batch_priority']}: {entry['relative_png']} -> "
                f"{Path(entry['output_svg']).relative_to(output_dir)}"
            )
        if len(manifest) > 10:
            print(f"  ... and {len(manifest) - 10} more")
        return

    try:
        preprocess_backend = resolve_preprocess_backend(args.preprocess_backend, cuda_info)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Using preprocess backend: {preprocess_backend}")

    success = 0
    failed = 0
    skipped_count = summary['by_priority'].get('exclude-derived', 0)

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                process_asset,
                Path(entry['input_png']),
                input_dir,
                output_dir,
                preprocess_backend,
            ): entry
            for entry in execution_candidates
        }

        for future in as_completed(futures):
            name, status, detail = future.result()
            if status == 'success':
                print(f"  [OK] {name}")
                success += 1
            else:
                print(f"  [FAIL] {name}: {detail}")
                failed += 1

    print()
    print("=== Complete ===")
    print(f"Success: {success}, Skipped: {skipped_count}, Failed: {failed}")


if __name__ == "__main__":
    main()
