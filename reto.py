#!/usr/bin/python3
import random
import os


def create_board(length):
    '''CREA DOS MATRICES, UNA CON EL TABLERO CUADRADO DE LA LONGITUD DE LADO INTRODUCIDO, Y OTRA MATRIZ QUE REFLEJA
    SI LAS CARTAS ESTAN REVELADAS, OCULTAS, O ELIMINADAS, ESTABLECIENDOLAS COMO OCULTAS POR DEFECTO'''

    card_pairs = int((length**2) / 2)
    number_list = [x for x in range(1, (card_pairs + 1))] * 2
    random.shuffle(number_list)

    board = []  # Donde van a ir guardados los números de las cartas
    board_status = []  # Donde van a ir guardados el estado actual de cada carta
    # None == Eliminada
    # True == Revelada
    # False == Oculta

    # Indice para avanzar en la lista numérica aleatoria
    index = 0

    for i in range(length):
        board.append([])
        board_status.append([])

        for j in range(length):
            board[i].append(number_list[index])
            board_status[i].append(False)  # Por defecto las cartas están ocultas
            index += 1

    return board, board_status, card_pairs


def print_board(board_cards, board_status):
    '''MUESTRA EL TABLERO EN LA PANTALLA'''
    os.system('cls')
    side_length = len(board_cards)

    # Estas dos variables se usan para ajustar y alinear el tablero
    max_card_len = len(str(int((side_length**2) / 2)))
    max_row_number_len = len(str(side_length - 1))

    # Imprime la primera fila
    print('{} '.format(' ' * max_row_number_len), end='')
    for i in range(0, side_length):
        print('{}{} '.format(i, ' ' * (max_card_len - len(str(i)))), end='')
    print()

    # Imprime cada fila
    for i in range(side_length):
        print('\n{}{}'.format(i, ' ' * (max_row_number_len - len(str(i)))),
              end='')

        for j in range(side_length):
            card_number_len = len(str(board_cards[i][j]))

            # Si la carta ya fue eliminada
            if board_status[i][j] is None:
                print(' {}'.format(' ' * max_card_len), end='')

            # Si la carta esta revelada
            elif board_status[i][j]:
                print((' ' + ' ' * (max_card_len - card_number_len)) +
                      str(board_cards[i][j]),
                      end='')

            # Si la carta esta oculta
            else:
                print(' ' + '-' * max_card_len, end='')

        # Nueva línea
        print()


def is_int(string):
    ''''DETERMINA SI UN VALOR DADO PUEDE SER CONVERTIDO A ENTERO O NO'''
    try:
        int(string)
    except ValueError:
        return False
    else:
        return True


def ask_for_coordinates(board, board_status, player_text):
    '''PIDE LOS VALORES DE COORDENADAS AL USUARIO'''
    previous_guess_invalid = False
    number_of_guesses = 0
    coords_list = []
    board_length = len(board)

    # Continua hasta que haya dos valores válidos para las coordenadas
    while number_of_guesses < 2:
        print_board(board, board_status)

        if previous_guess_invalid:
            print('\nVALOR INVALIDO, revisa los valores e intenta nuevamente')

        print('\nTURNO {}'.format(player_text))

        card_coords = input(
            'Introduce las coordenadas (x, y) de la carta a revelar: ')
        print()

        coords = card_coords.split(',')

        # Comprobar si las coordenadas introducidas no son validas
        # Si las coordenadas validas no estan en el formato correcto
        if len(coords) != 2 or (not is_int(coords[0]) or not is_int(coords[1])) or \
            (int(coords[0]) >= board_length or int(coords[1]) >= board_length):
            previous_guess_invalid = True

        # Si estan en el formato correcto
        else:
            # En una matriz en Python los valores se referencian primero en el eje y y despues en el x
            coords = [int(x) for x in coords]
            coords.reverse()
            card_status = board_status[coords[0]][coords[1]]

            # Si son las mismas coordenadas que acaban de ser introducidas o si la carta está eliminada
            if card_status == True or card_status is None:
                previous_guess_invalid = True

            else:
                previous_guess_invalid = False
                coords_list.append(coords)
                board_status[coords[0]][coords[1]] = True
                number_of_guesses += 1

    return coords_list


def main():
    ''''FUNCION PRINCIPAL QUE SE CORRE POR DEFECTO EN EL PROGRAMA'''
    os.system('cls')

    # Obtiene el valor para la longitud del tablero
    while True:
        board_length = input(
            'Escoge un numero par para el tamaño del tablero (deja en blanco para el valor por defecto): '
        )
        if board_length.strip() == '':
            board_length = 6  # Valor por defecto
            break
        elif not is_int(board_length) or (int(board_length) % 2) != 0:
            print('VALOR INVALIDO, elige un numero par valido')
        else:
            board_length = int(board_length)
            break

    # Obtiene el valor para el numero de rounds a jugar
    while True:
        number_of_rounds = input(
            'Elige un numero de rounds a jugar (deja en blanco para el valor por defecto): '
        )
        if number_of_rounds.strip() == '':
            number_of_rounds = 1  # Valor por defecto
            break
        elif not is_int(number_of_rounds):
            print('VALOR INVALIDO, elige un numero valido')
        else:
            number_of_rounds = int(number_of_rounds)
            break

    # Obtiene los valores de los nombres de los jugadores para mensajes personalizados
    player_strings = {'1': {}, '2': {}}
    for k in player_strings:
        player = input(
            'Introduce el nombre del jugador {}: '.format(k)).strip()
        if player == '':  # Valores por defecto
            player_strings[k]['normal'] = 'el jugador {}'.format(k)
            player_strings[k]['sentence_case'] = 'El jugador {}'.format(k)
            player_strings[k]['upper_case'] = 'DEL JUGADOR {}'.format(k)
        else:
            player_strings[k]['normal'], player_strings[k][
                'sentence_case'] = player, player
            player_strings[k]['upper_case'] = 'DE {}'.format(player.upper())

    # Obtiene si se decide borrar las cartas del tablero en lugar de solo mostrarlas una vez acertado un par
    hard_mode_enabled = input('Activar modo dificil (s/N): ')
    if hard_mode_enabled.lower() == 's':
        hard_mode_enabled = True

    # El jugador 1 empieza por defecto
    player_turn = 1
    won_rounds = {'1': 0, '2': 0}
    '''Ciclo principal, que pertenece el número de rounds escogidos'''
    for round in range(number_of_rounds):

        if number_of_rounds > 1:
            print()
            print('-' * 2 * board_length)
            print('ROUND #{}'.format(round + 1))
            print('-' * 2 * board_length)
        print()

        found_pairs = 0
        board, board_status, card_pairs = create_board(board_length)
        score = {'1': 0, '2': 0}
        '''Ciclo anidado #1, que pertenece a dejar que un jugador juegue su turno despues del otro hasta que se encuentren todos los pares'''
        while True:
            # Detecta si el texto dl jugador es el default, para imprimirlo en un formato correcto
            card_coords_guesses = ask_for_coordinates(
                board, board_status,
                player_strings[str(player_turn)]['upper_case'])
            card_value_guesses = []

            for i, coords in enumerate(card_coords_guesses):
                card_value_guesses.append(board[coords[0]][coords[1]])

            print_board(board, board_status)

            # Si la eleccion es correcta
            if card_value_guesses[0] == card_value_guesses[1]:

                # Si se han encontrado todos los pares, DETIENE el ciclo de turnos
                if found_pairs == (card_pairs - 1):
                    break

                else:
                    print(
                        '\nBien hecho, has encontrado un par. Vuelve a ser tu turno.'
                    )
                    if hard_mode_enabled:
                        new_card_status = None
                    else:
                        new_card_status = True

                    score[str(player_turn)] += 1
                    found_pairs += 1

            # Si la eleccion es incorrecta
            else:
                print(
                    '\nLo siento, no has encontrado un par valido. Es el turno del siguiente jugador.'
                )
                if player_turn == 1:
                    player_turn = 2
                else:
                    player_turn = 1
                new_card_status = False

            # Establece el estado de las cartas de regreso a ocultas, o a eliminadas
            for i, coords in enumerate(card_coords_guesses):
                board_status[coords[0]][coords[1]] = new_card_status

            input('Presiona ENTER para continuar... ')
            print()

        # Si hay un empate, el jugador que empieza es al azar
        if score['1'] == score['2']:
            print('\n\nHa habido un empate de {} puntos.'.format(score['1'] +
                                                                 1))
            player_turn = random.randint(1, 2)

        # En el siguiente round empieza el perdedor ;)
        else:
            if score['1'] > score['2']:
                won_player = 1
                player_turn = 2

            else:
                won_player = 2
                player_turn = 1

            os.system('cls')
            print('{} ha ganado con {} puntos.'.format(
                player_strings[str(won_player)]['sentence_case'],
                score[str(won_player)] + 1))
            won_rounds[str(won_player)] += 1

        if number_of_rounds > 1 and round != (number_of_rounds - 1):
            input(
                'Presiona ENTER para continuar con el siguiente round, comenzando con {}...'
                .format(player_strings[str(player_turn)]['normal']))

    if number_of_rounds > 1:
        print()
        for i in player_strings:
            print('{} ganó {} ronda(s)'.format(
                player_strings[i]['sentence_case'], won_rounds['1']))


# Ciclo infinito que vuelve a comienza el juego hasta que se elija no continuar
while True:
    main()
    if input('\n\n¿Volver a jugar? (S/n): ').lower() == 'n':
        break
