#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
import hermes_python.ontology.dialogue as dialogue
import io
from todolist import TodoList


USERNAME_INTENTS = "raph"


def user_intent(intentname):
    return USERNAME_INTENTS + ":" + intentname


def read_configuration_file(configuration_file):
    try:
        cp = configparser.ConfigParser()
        with io.open(configuration_file, encoding="utf-8") as f:
            cp.read_file(f)
        return {section: {option_name: option for option_name, option in cp.items(section)}
                for section in cp.sections()}
    except (IOError, configparser.Error):
        return dict()


def intent_callback(hermes, intent_message):
    # conf = read_configuration_file(CONFIG_INI)
    intentname = intent_message.intent.intent_name
    if intentname == user_intent("addTodoListItem"):
        result_sentence = todolist.add_item(intent_message)
        hermes.publish_end_session(intent_message.session_id, result_sentence)

    elif intentname == user_intent("removeTodoListItem"):
        result_sentence = todolist.remove_item(intent_message)
        hermes.publish_end_session(intent_message.session_id, result_sentence)

    elif intentname == user_intent("isItemOnTodoList"):
        result_sentence = todolist.is_item(intent_message)
        hermes.publish_end_session(intent_message.session_id, result_sentence)

    elif intentname == user_intent("clearTodoList"):
        result_sentence = todolist.try_clear()
        if result_sentence == "empty":
            result_sentence = "Die Tuhduh-Liste ist schon leer."
            hermes.publish_end_session(intent_message.session_id, result_sentence)
        else:
            todolist.wanted_intents = [user_intent("confirmTodoList")]
            configure_message = dialogue.DialogueConfiguration().enable_intent(user_intent("confirmTodoList"))
            hermes.configure_dialogue(configure_message)
            hermes.publish_continue_session(intent_message.session_id, result_sentence,
                                            todolist.wanted_intents)
        
    elif intentname == user_intent("confirmTodoList"):
        todolist.wanted_intents = []
        result_sentence = todolist.clear_confirmed(intent_message)
        hermes.publish_end_session(intent_message.session_id, result_sentence)
    
    elif intentname == user_intent("showTodoList"):
        result_sentence = todolist.show()
        hermes.publish_end_session(intent_message.session_id, result_sentence)

    elif intentname == user_intent("sendTodoList"):
        result_sentence = todolist.send()
        hermes.publish_end_session(intent_message.session_id, result_sentence)


def intent_not_recognized_callback(hermes, intent_message):
    configure_message = dialogue.DialogueConfiguration().disable_intent(user_intent("confirmTodoList"))
    hermes.configure_dialogue(configure_message)
    todolist.wanted_intents = []
    hermes.publish_end_session({'sessionId': intent_message.session_id,
                                'text': "Die Tuhduh-Liste wurde nicht gelöscht."})


if __name__ == "__main__":
    config = read_configuration_file("config.ini")
    todolist = TodoList(config)
    with Hermes("localhost:1883") as h:
        h.subscribe_intents(intent_callback)
        h.subscribe_intent_not_recognized(intent_not_recognized_callback)
        h.start()
