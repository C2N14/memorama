#!/usr/bin/python3

import sys
import random

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


def display_row_separators(row, before):
    try:
        row.set_activatable(False)
        row.set_selectable(False)

    except:
        pass

    if before:
        row.set_header(Gtk.Separator())


def try_or_default(val, try_type, default_dict, val_key):
    try:
        if val.strip() == '':
            raise Exception
        return try_type(val)
    except:
        return default_dict[val_key]


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="mx.itesm.adrian.reto.tc1028",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self.main_window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.builder = Gtk.Builder()
        self.builder.add_from_file('memorama.glade')
        self.builder.set_application(self)
        self.builder.connect_signals(self)
        self.current_window = None

        self.settings = {}
        self.default_settings = {
            'length': 6,
            'rounds': 1,
            'player_strings': {},
            'font_size': 20
        }
        for i in range(1, 3):
            self.default_settings['player_strings'][str(i)] = {}
            self.default_settings['player_strings'][str(
                i)]['normal'] = 'el jugador {}'.format(i)
            self.default_settings['player_strings'][str(
                i)]['sentence_case'] = 'El jugador {}'.format(i)
            self.default_settings['player_strings'][str(
                i)]['upper_case'] = 'DEL JUGADOR {}'.format(i)

    def do_activate(self):
        if not self.current_window:
            self.set_current_window('settings_window')
            # self.main_window.set_icon_from_file(get_resource('automathemely.svg'))

            # sub_w_list = ['confirm_dialog', 'error_dialog']
            # self.sub_windows = dict()
            # for w in sub_w_list:
            #     self.sub_windows[w] = self.builder.get_object(w)
            #     self.sub_windows[w].set_transient_for(self.main_window)

        self.current_window.present()
        self.builder.get_object('settings_listbox').set_header_func(
            display_row_separators)
        self.board_grid = None

    def create_board(self, length):
        board_grid = Gtk.Grid.new()
        buttons = []

        card_pairs = int((length**2) / 2)
        number_list = [x for x in range(1, (card_pairs + 1))] * 2
        random.shuffle(number_list)

        board = []  # Donde van a ir guardados los números de las cartas

        # Indice para avanzar en la lista numérica aleatoria
        index = 0

        for i in range(length):
            board.append([])
            buttons.append([])

            for j in range(length):
                board[i].append(number_list[index])
                index += 1

                buttons[i].append(Gtk.Button.new_with_label(''))
                buttons[i][j].get_child().set_markup(
                    '<span font="Monospace {}">'.format(
                        self.settings['font_size']) +
                    ' ' * len(str(card_pairs)) + '</span>')
                board_grid.attach(buttons[i][j], j, i, 1, 1)
                buttons[i][j].set_visible(True)
                buttons[i][j].set_name('card_{},{}'.format(i, j))
                buttons[i][j].connect('clicked', self.on_card_click)

        return board, card_pairs, board_grid, buttons

    def on_card_click(self, card, *args):
        coords = [int(x) for x in card.get_name().lstrip('card_').split(',')]
        coords.reverse()
        card_value = self.board[coords[0]][coords[1]]
        card.get_child().set_markup(
            '<span font="Monospace {}">{}</span>'.format(
                self.settings['font_size'],
                ' ' * (len(str(self.card_pairs)) - len(str(card_value))) +
                str(card_value)))
        card.set_sensitive(False)

        self.current_player_guesses.append(coords)

        if len(self.current_player_guesses) > 1:
            self.make_a_guess()

        # DEBUG
        print(self.current_player_guesses)

    def on_start_new_game(self, *args):
        if self.board_grid:
            self.board_grid.destroy()

        self.settings['length'] = try_or_default(
            self.get_entry_text('board_size'), int, self.default_settings,
            'length')
        self.settings['rounds'] = try_or_default(
            self.get_entry_text('number_of_rounds'), int,
            self.default_settings, 'rounds')
        self.settings['font_size'] = try_or_default(
            self.get_entry_text('font_size'), int, self.default_settings,
            'font_size')

        self.settings['player_strings'] = {}
        for i in range(1, 3):
            self.settings['player_strings'][str(i)] = {}
            self.settings['player_strings'][str(i)]['normal'] = try_or_default(
                self.get_entry_text('player_{}_name'.format(i)), str,
                self.default_settings['player_strings'][str(i)], 'normal')
            self.settings['player_strings'][str(
                i)]['sentence'] = try_or_default(
                    self.get_entry_text('player_{}_name'.format(i)), str,
                    self.default_settings['player_strings'][str(i)], 'normal')
            self.settings['player_strings'][str(
                i)]['upper_case'] = try_or_default(
                    self.get_entry_text('player_{}_name'.format(i)).upper(),
                    str, self.default_settings['player_strings'][str(i)],
                    'upper_case')
            if self.settings['player_strings'][str(i)][
                    'upper_case'] != self.default_settings['player_strings'][
                        str(i)]['upper_case']:
                self.settings['player_strings'][str(i)][
                    'upper_case'] = 'DE ' + self.settings['player_strings'][
                        str(i)]['upper_case']

        self.current_window.hide()
        self.set_current_window('board_window')
        self.current_window.set_sensitive(True)

        self.current_round = 0
        self.current_player_turn = 0
        self.players_score = {}
        self.players_score['rounds'] = {'1': 0, '2': 0}
        self.builder.get_object('round_alignment').set_visible(False)
        self.start_new_round()

    def make_a_guess(self):
        coords_list = self.current_player_guesses
        if not self.board[coords_list[0][0]][coords_list[0][1]] == self.board[
                coords_list[1][0]][coords_list[1][1]]:
            end_turn_dialog = self.builder.get_object('end_turn_dialog')
            self.current_window.set_sensitive(False)
            end_turn_dialog.run()
        else:
            self.players_score['pairs'][str(self.current_player_turn)] += 1
            print(self.current_player_turn)
            print(self.players_score)

        self.current_player_guesses = []

        if (self.players_score['pairs']['1'] +
                self.players_score['pairs']['2']) == self.card_pairs:
            self.end_round()

    def on_end_turn(self, button, *args):
        card_pairs = int((len(self.board)**2) / 2)

        for coord in self.current_player_guesses:
            button = self.board_grid.get_child_at(coord[0], coord[1])
            button.get_child().set_markup('<span font="Monospace {}">'.format(
                self.settings['font_size']) + ' ' * len(str(card_pairs)) +
                                          '</span>')
            button.set_sensitive(True)

        dialog = self.builder.get_object('end_turn_dialog')
        dialog.hide()
        self.current_window.set_sensitive(True)

        self.start_new_turn()

    def on_next_round(self, *args):
        self.builder.get_object('end_round_dialog').hide()
        self.current_window.set_sensitive(True)
        self.board_grid.destroy()
        self.start_new_round()

    def on_next_game(self, *args):
        self.builder.get_object('end_round_dialog').hide()
        self.current_window.hide()
        self.set_current_window('settings_window')

    def start_new_turn(self, *args):
        if self.current_player_turn == 1:
            new_player_turn = 2
        else:
            new_player_turn = 1

        self.current_player_turn = new_player_turn
        self.builder.get_object('player_turn_label').set_markup(
            '<span font="Arial {}">TURNO {}</span>'.format(
                self.settings['font_size'] / 2,
                self.settings['player_strings'][str(
                    self.current_player_turn)]['upper_case']))

    def start_new_round(self, *args):
        self.board, self.card_pairs, self.board_grid, self.grid_buttons = self.create_board(
            self.settings['length'])

        self.builder.get_object('grid_alignment').add(self.board_grid)
        self.board_grid.set_visible(True)

        self.current_round += 1

        self.players_score['pairs'] = {'1': 0, '2': 0}

        if self.settings['rounds'] > 1:
            self.builder.get_object('round_label').set_markup(
                '<span font="Arial {}">ROUND {}</span>'.format(
                    self.settings['font_size'] / 2, self.current_round))
            self.builder.get_object('round_alignment').set_visible(True)

        self.current_player_guesses = []

        self.start_new_turn()

    def end_round(self):
        self.players_score['rounds'][str(self.current_player_turn)] += 1

        self.current_window.set_sensitive(False)
        end_round_dialog = self.builder.get_object('end_round_dialog')
        end_round_dialog.set_transient_for(self.current_window)
        end_round_dialog.show()

        for i in range(2):
            pairs_label = self.builder.get_object('player_{}_pairs'.format(i +
                                                                           1))
            pairs_label.set_label('{} pares'.format(
                self.players_score['pairs'][str(i + 1)]))

            rounds_label = self.builder.get_object(
                'player_{}_rounds'.format(i + 1))
            if self.settings['rounds'] > 1:
                rounds_label.set_visible(True)
                rounds_label.set_label('{} rounds'.format(
                    self.players_score['rounds'][str(i + 1)]))
            else:
                rounds_label.set_visible(False)

        print(self.settings['rounds'], self.current_round)
        if self.settings['rounds'] > 1 and self.current_round < self.settings[
                'rounds']:
            self.builder.get_object('next_round_button').set_sensitive(True)
        else:
            self.builder.get_object('next_round_button').set_sensitive(False)

    def set_current_window(self, window_id):
        self.current_window = self.builder.get_object(window_id)
        self.current_window.set_application(self)
        self.current_window.set_title('Memorama')
        self.current_window.present()

    def get_entry_text(self, entry_id):
        return self.builder.get_object(entry_id).get_text()

    def do_shutdown(self):
        print('Saliendo...')
        Gtk.Application.do_shutdown(self)


app = App()
app.run()
