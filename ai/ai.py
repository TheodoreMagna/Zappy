"""
This module contains the AI logic for the game.
"""

import threading
from connection import ServerConnection
from messages import Logger
from ai_class import AI

NB_THREAD = 0  # (Temporary) Global variable to limit the number of AI on map

def connect_new_thread(ai_instance: AI, args, logger: Logger, threads: list):
    """
    This function connects a new thread.

    Parameters:
    args (argparse.Namespace): The command line arguments.
    """
    global NB_THREAD # (Temporary) Global variable to limit the number of AI on map pylint: disable=global-statement
    NB_THREAD += 1
    if not ai_instance.net.multi_threading:
        ai_instance.net.logger.info("Mutli threading is disabled, manually connect an AI", ai_instance.id)
    else:
        threads.append(threading.Thread(target=make_new_ai, args=(args, logger)))
        threads[-1].start()

def make_ai_actions(ai_instance: AI, threads: list, args, logger: Logger):
    """
    This function defines the actions of the AI.

    Parameters:
    ai_instance (AI): The AI instance.
    threads (list): The list of threads.
    args (argparse.Namespace): The command line arguments.
    logger (Logger): The logger.
    """

    if NB_THREAD < 9 and ai_instance.get_unused_slots() > 0:
        connect_new_thread(ai_instance, args, logger, threads)
    if not ai_instance.king and ai_instance.random and ai_instance.get_food_nbr() < 25:
        ai_instance.go_to_obj("food")
        ai_instance.take_all_food()
        if ai_instance.random and ai_instance.lvl == 1:
            ai_instance.go_to_obj("linemate")
            ai_instance.incantation()
    else:
        if not ai_instance.king and not ai_instance.choosen_ones:
            if ai_instance.get_unused_slots() == 0 and NB_THREAD < 9:
                ai_instance.fork()

        if not ai_instance.king and ai_instance.random and ai_instance.is_enought_for_lvl():
            ai_instance.king = True

        if ai_instance.king:
            if ai_instance.get_nb_player_on_tile() >= 6:
                ai_instance.broadcast("elevate")
                ai_instance.drop_all()
                ai_instance.incantation()
            else:
                ai_instance.broadcast("lvl6")
                ai_instance.turn_right()
                ai_instance.turn_right()
                ai_instance.turn_right()  # To delay broadcast
                ai_instance.turn_right()
                ai_instance.turn_right()
        else:
            if ai_instance.random and ai_instance.lvl == 1:
                ai_instance.go_to_obj("linemate")
                ai_instance.incantation()

            if ai_instance.random and ai_instance.lvl == 2:
                ai_instance.go_to_needs()


def start_ai_logic(ai_instance: AI, threads: list, args, logger: Logger):
    """
    This function starts the AI logic.

    Parameters:
    ai_instance (AI): The AI instance.
    threads (list): The list of threads.
    args (argparse.Namespace): The command line arguments.
    logger (Logger): The logger.
    """
    while not ai_instance.dead and ai_instance.lvl < 8:
        ai_instance.net.empty_buffer(ai_instance)
        if ai_instance.dead:
            break
        if ai_instance.is_elevating:
            continue

        make_ai_actions(ai_instance, threads, args, logger)

        ai_instance.net.send_buffer(ai_instance)


def make_new_ai(args, logger: Logger):
    """
    This function creates a new AI.

    Parameters:
    args (argparse.Namespace): The command line arguments.
    logger (Logger): The logger.
    ai_id (int): The ID of the AI.

    Returns:
    int: The exit code.
    """
    global NB_THREAD # (Temporary) Global variable to limit the number of AI on map pylint: disable=global-statement

    threads: list = []
    net: ServerConnection = ServerConnection(logger, args.h, args.p)  # AI Connection to Server
    if not net.connect():
        return 84
    net.multi_threading = args.t

    ai_instance: AI = AI(args.n, net)  # AI Creation
    start_ai_logic(ai_instance, threads, args, logger)  # AI Logic
    net.close_connection(ai_instance)  # End of the AI
    NB_THREAD -= 1
    for thread in threads:
        thread.join()
    return 0
