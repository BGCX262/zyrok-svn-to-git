#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Multimedia player writed in python
# by Mateus Zenaide Henriques

import sys, os, thread, time
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class Zyrok:
    name = "Zyrok"
    description = "Multimedia Player"
    developer = "by Mateus Zenaide Henriques"
    website = "http://zyrok.com"
    version = "0.1.0"
    resulution = width, weight = 800, 480

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.name + " - " + self.description)
        self.window.set_default_size(self.width, self.weight)
        self.window.connect("destroy", gtk.main_quit, "WM destroy")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(True)
        
        self.menu_bar = self.create_menu()

        self.entry = gtk.Entry()

        self.twitter_button = gtk.Button()        
        self.twitter_button.set_label("Send Twitter")

        self.vbox = gtk.VBox(False, 0)
        self.vbox.pack_start(self.menu_bar, False)
        self.vbox.pack_start(self.entry, False)
        self.window.add(self.vbox)

        self.buttonbox = gtk.HButtonBox()
        self.hbox = gtk.HBox()
        self.vbox.add(self.hbox)
        self.hbox.pack_start(self.buttonbox, False)
        self.play_stop_button = gtk.Button("Play")
        self.rewind_button = gtk.Button("Rewind")
        self.forward_button = gtk.Button("Forward")

        self.buttonbox.add(self.rewind_button)
        self.buttonbox.add(self.play_stop_button)
        self.buttonbox.add(self.forward_button)        
        self.buttonbox.add(self.twitter_button)

        self.play_stop_button.connect("clicked", self.play_stop)
        self.rewind_button.connect("clicked", self.rewind_callback)
        self.forward_button.connect("clicked", self.forward_callback)
        self.twitter_button.connect("clicked", self.twitter)  

        self.time_label = gtk.Label()
        self.time_label.set_text("00:00 / 00:00")
        self.hbox.add(self.time_label)
        self.window.show_all()
        ##########################################
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("filesrc", "file-source")
        demuxer = gst.element_factory_make("oggdemux", "demuxer")
        demuxer.connect("pad-added", self.demuxer_callback)
        self.audio_decoder = gst.element_factory_make("vorbisdec", "vorbis-decoder")
        audioconv = gst.element_factory_make("audioconvert", "converter")
        audiosink = gst.element_factory_make("autoaudiosink", "audio-output")
        self.player.add(source, demuxer, self.audio_decoder, audioconv, audiosink)
        gst.element_link_many(source, demuxer)
        gst.element_link_many(self.audio_decoder, audioconv, audiosink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        self.time_format = gst.Format(gst.FORMAT_TIME)
        ##########################################

    def create_menu(self):
        self.menu_file = gtk.Menu()
        self.menu_audio = gtk.Menu()
        self.menu_video = gtk.Menu()
        self.menu_help = gtk.Menu()

        # Menu
        self.menuItemFile = gtk.MenuItem("File")
        self.menuItemAudio = gtk.MenuItem("Audio")
        self.menuItemVideo = gtk.MenuItem("Video")
        self.menuItemHelp = gtk.MenuItem("Help")

        # File
        self.menuItemOpen = gtk.MenuItem("Open")
        self.menuItemPreferences = gtk.MenuItem("Preferences")
        self.separator = gtk.SeparatorMenuItem()
        self.menuItemExit = gtk.MenuItem("Exit")
        
        self.menuItemOpen.connect("activate", self.file_selection, None)
        self.menuItemPreferences.connect("activate", self.preferences, None)
        self.menuItemExit.connect_object("activate", gtk.Widget.destroy, self.window)

        self.menu_file.append(self.menuItemOpen)
        self.menu_file.append(self.menuItemPreferences)
        self.menu_file.append(self.separator)
        self.menu_file.append(self.menuItemExit)

        self.menuItemFile.set_submenu(self.menu_file)
        ###################################################

        # Audio
        self.menuItemAudio.set_submenu(self.menu_audio)
        ###################################################

        # Video
        self.menuItemVideo.set_submenu(self.menu_video)
        ###################################################

        # Help
        self.menuItemAbout = gtk.MenuItem("About")
        self.menuItemAbout.connect("activate", self.about, None)
        self.menu_help.append(self.menuItemAbout)
        self.menuItemHelp.set_submenu(self.menu_help)
        ###################################################     

        self.menu_bar = gtk.MenuBar()
        self.menu_bar.append(self.menuItemFile)
        self.menu_bar.append(self.menuItemAudio)
        self.menu_bar.append(self.menuItemVideo)
        self.menu_bar.append(self.menuItemHelp)

        return self.menu_bar

    def play_stop(self, w):
        if self.play_stop_button.get_label() == "Play":
            filepath = self.entry.get_text()
            if os.path.isfile(filepath):
                self.play_stop_button.set_label("Stop")
                self.player.get_by_name("file-source").set_property("location", filepath)
                self.player.set_state(gst.STATE_PLAYING)
                self.play_thread_id = thread.start_new_thread(self.play_thread, ())
        else:
            self.play_thread_id = None
            self.player.set_state(gst.STATE_NULL)
            self.play_stop_button.set_label("Play")
            self.time_label.set_text("00:00 / 00:00")

    def play_thread(self):
        play_thread_id = self.play_thread_id
        gtk.gdk.threads_enter()
        self.time_label.set_text("00:00 / 00:00")
        gtk.gdk.threads_leave()

        while play_thread_id == self.play_thread_id:
            try:
                time.sleep(0.2)
                dur_int = self.player.query_duration(self.time_format, None)[0]
                dur_str = self.convert_ns(dur_int)
                gtk.gdk.threads_enter()
                self.time_label.set_text("00:00 / " + dur_str)
                gtk.gdk.threads_leave()
                break
            except:
                pass

        time.sleep(0.2)
        while play_thread_id == self.play_thread_id:
            pos_int = self.player.query_position(self.time_format, None)[0]
            pos_str = self.convert_ns(pos_int)
            if play_thread_id == self.play_thread_id:
                gtk.gdk.threads_enter()
                self.time_label.set_text(pos_str + " / " + dur_str)
                gtk.gdk.threads_leave()
            time.sleep(1)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.play_thread_id = None
            self.player.set_state(gst.STATE_NULL)
            self.play_stop_button.set_label("Play")
            self.time_label.set_text("00:00 / 00:00")
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.play_thread_id = None
            self.player.set_state(gst.STATE_NULL)
            self.play_stop_button.set_label("Play")
            self.time_label.set_text("00:00 / 00:00")

    def demuxer_callback(self, demuxer, pad):
        adec_pad = self.audio_decoder.get_pad("sink")
        pad.link(adec_pad)

    def rewind_callback(self, w):
        pos_int = self.player.query_position(self.time_format, None)[0]
        seek_ns = pos_int - (10 * 1000000000)
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)

    def forward_callback(self, w):
        pos_int = self.player.query_position(self.time_format, None)[0]
        seek_ns = pos_int + (10 * 1000000000)
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)

    def twitter(self, w):
        pass

    def convert_ns(self, time_int):
        time_int = time_int / 1000000000
        time_str = ""
        if time_int >= 3600:
            _hours = time_int / 3600
            time_int = time_int - (_hours * 3600)
            time_str = str(_hours) + ":"
        if time_int >= 600:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + str(_mins) + ":"
        elif time_int >= 60:
            _mins = time_int / 60
            time_int = time_int - (_mins * 60)
            time_str = time_str + "0" + str(_mins) + ":"
        else:
            time_str = time_str + "00:"
        if time_int > 9:
            time_str = time_str + str(time_int)
        else:
            time_str = time_str + "0" + str(time_int)

        return time_str

    #########ORGANIZAR CODIGO###########
    def file_selection(self, widget, data = None):
        self.filew = gtk.FileChooserDialog("Zyrok - File Selection", None, gtk.FILE_CHOOSER_ACTION_OPEN,
                                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        self.filew.set_default_response(gtk.RESPONSE_OK)
        self.filew.set_position(gtk.WIN_POS_CENTER)
        self.filew.set_default_size(350, 350)

        response = self.filew.run()

        if response == gtk.RESPONSE_OK:
            self.entry.set_text(self.filew.get_filename())
            self.filew.destroy()
                    
        elif response == gtk.RESPONSE_CANCEL:
            self.filew.destroy()

    def about(self, widget, data = None):
        self.dialog = gtk.AboutDialog()
        self.dialog.set_name(self.name)
        self.dialog.set_version(self.version)
        self.dialog.set_comments(self.description + "\n" + self.developer)
        self.dialog.set_website(self.website)
        self.dialog.run()
        self.dialog.destroy()

    def preferences(self, widget, data = None):
        self.preferences_dialog = gtk.Dialog(self.name + " - " + "Preferences", self.window,
                                 gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT |
                                 gtk.DIALOG_NO_SEPARATOR, (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.preferences_dialog.set_position(gtk.WIN_POS_CENTER)
        self.preferences_dialog.set_default_size(350, 350)
        
        abas = gtk.Notebook()
        titulo_abas = gtk.Label("Titulo")

        twitter_label = gtk.Label("Twitter")
        twitter_content = gtk.Label("Twitter Preferences")

        lastfm_label = gtk.Label("Lastfm")
        lastfm_content = gtk.Label("Lastfm Preferences")

        abas.append_page(twitter_content, twitter_label)
        abas.append_page(lastfm_content, lastfm_label)
        self.preferences_dialog.vbox.pack_start(titulo_abas, False)
        self.preferences_dialog.vbox.pack_start(abas)
        self.preferences_dialog.vbox.show_all()
        self.preferences_dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("Royal Blue"))
        resposta = self.preferences_dialog.run()
        self.preferences_dialog.destroy()
    
Zyrok()
gtk.gdk.threads_init()
gtk.main()

