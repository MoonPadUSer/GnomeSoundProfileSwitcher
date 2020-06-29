import os
import signal
import json
import subprocess
import pulsectl

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

APPINDICATOR_ID = 'soundprofileswitcher'
pulse = pulsectl.Pulse('soundprofileswitcher')

def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, "", appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    notify.init(APPINDICATOR_ID)
    gtk.main()
    
def build_menu():
    menu = gtk.Menu()
    
    for card in pulse.card_list():
        menu.append(gtk.SeparatorMenuItem())    
        
        radio_group = None
        for profile in card.profile_list:
            
            # create profile radio item (if group is none, profile_radio_item becomes a group, that's why I set radio_group to profile_radio_item afterwards
            profile_radio_item = gtk.RadioMenuItem(label=profile.description, group=radio_group)
            if radio_group == None: radio_group = profile_radio_item
            
            # select the active profile
            if profile == card.profile_active:
                profile_radio_item.set_active(True)

            # connect click event to set_active_profile
            profile_radio_item.connect('activate', set_active_profile, card.index, profile.name)
            # add to the menu
            menu.append(profile_radio_item)
       
    menu.append(gtk.SeparatorMenuItem())

    # add quit item
    quit_item = gtk.MenuItem(label='Quit')
    quit_item.connect('activate', quit)

    
    menu.append(quit_item)

    menu.show_all()
    return menu

def set_active_profile(_, card_idx, profile_name):
    pulse.card_profile_set_by_index(card_idx, profile_name)

def quit(_):
    notify.uninit()
    gtk.main_quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
