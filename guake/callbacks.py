import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from guake.utils import FullscreenManager
from guake.utils import TabNameUtils
from guake.dialogs import RenameDialog
from guake.dialogs import SaveTerminalDialog
from guake.about import AboutDialog
from guake.prefs import PrefsDialog
from urllib.parse import quote_plus
from guake.utils import get_server_time


class TerminalContextMenuCallbacks():

    def __init__(self, terminal, window, settings, notebook):
        self.terminal = terminal
        self.window = window
        self.settings = settings
        self.notebook = notebook

    def on_copy_clipboard(self, *args):
        self.terminal.copy_clipboard()

    def on_copy_url_clipboard(self, *args):
        url = self.terminal.get_link_under_cursor()
        if url is not None:
            clipboard = Gtk.Clipboard.get_default(self.window.get_display())
            clipboard.set_text(url, len(url))

    def on_paste_clipboard(self, *args):
        self.terminal.paste_clipboard()

    def on_toggle_fullscreen(self, *args):
        FullscreenManager(self.window).toggle()

    def on_save_to_file(self, *args):
        SaveTerminalDialog(self.terminal, self.window).run()

    def on_reset_terminal(self, *args):
        self.terminal.reset(True, True)

    def on_find(self):
        # this is not implemented jet
        pass

    def on_new_tab(self, *args):
        self.notebook.new_page_with_focus(
            directory=self.terminal.get_current_directory()
        )

    def on_rename_tab(self, *args):
        page_num = self.notebook.find_page_index_by_terminal(self.terminal)
        tab_text = self.notebook.get_tab_text_index(page_num)
        dialog = RenameDialog(self.window, tab_text)
        r = dialog.run()
        if r == Gtk.ResponseType.ACCEPT:
            new_text = TabNameUtils.shorten(dialog.get_text(), self.settings)
            self.notebook.rename_page(page_num, new_text, True)
        dialog.destroy()

    def on_close_tab(self, *args):
        page_num = self.notebook.find_page_index_by_terminal(self.terminal)
        self.notebook.delete_page(page_num, False, True)

    def on_open_link(self, *args):
        self.terminal.browse_link_under_cursor()

    def on_search_on_web(self, *args):
        if self.terminal.get_has_selection():
            self.terminal.copy_clipboard()
            clipboard = Gtk.Clipboard.get_default(self.window.get_display())
            query = clipboard.wait_for_text()
            query = quote_plus(query)
            if query:
                search_url = "https://www.google.com/#q={!s}&safe=off".format(query)
                Gtk.show_uri(self.window.get_screen(), search_url, get_server_time(self.window))

    def on_quick_open(self, *args):
        if self.terminal.get_has_selection():
            self.terminal.quick_open()

    def on_command_selected(self, command):
        self.terminal.execute_command(command)

    def on_show_preferences(self, *args):
        self.notebook.guake.hide()
        PrefsDialog(self.settings).show()

    def on_show_about(self, *args):
        self.notebook.guake.hide()
        AboutDialog()

    def on_quit(self, *args):
        self.notebook.guake.accel_quit()
