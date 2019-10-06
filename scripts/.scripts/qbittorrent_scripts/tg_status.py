#!/usr/bin/env python3
import os
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import qbittorrent
import logging
import itertools
import pprint
import tg_helper


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

IP = "http://192.168.1.105:9001"


class Config:
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state

    def setup(self, filter="downloading", category="", sort="", reverse="false", limit=100,
              view_selects=None, qbit_client=None):
        self.torrents_filter = {
            "filter": filter,
            "category": category,
            "sort": sort,
            "reverse": reverse,
            "limit": limit,
        }
        self.views_select = view_selects or ["ratio", "tracker", "size", "dlspeed", "uploaded"]
        self.qbit_client = qbit_client


def info(update: telegram.Update, context: CallbackContext):
    """
    Return torrents that is actively downloading
    :param qb_client: qbit client
    :return: list containing torrent id
    """
    config = Config()
    torrents = config.qbit_client.torrents(**config.torrents_filter)
    pp = pprint.PrettyPrinter()
    msg = "Using configuration: \n"
    msg += f"{pp.pformat(config.torrents_filter)}\n"
    msg += "view_select: " + str(config.views_select) + "\n\n"
    for torrent in torrents:
        msg += f"{torrent['name']}:\n"
        for key in config.views_select:
           msg += f"    {key}: {torrent.get(key)}\n"
        msg += "\n"
    update.message.reply_text(msg)


config_handler = tg_helper.StateHandler("config")


@config_handler.message_handler()
@config_handler.end
def config_view_selects_apply(update: telegram.Update, context: CallbackContext):
    config = Config()
    config.views_select = list(update.message.text.split(" "))
    update.message.reply_text(f"Successfully update the views select to :{config.views_select}")


@config_handler.message_handler(Filters.regex(r"Views"))
@config_handler.goto(config_view_selects_apply)
def config_view_selects_query(update: telegram.Update, context: CallbackContext):
    update.message.reply_text("Type in the list of view to select")


@config_handler.message_handler()
@config_handler.end
def config_filters_apply(update: telegram.Update, context: CallbackContext):
    config = Config()
    config.torrents_filter[context.chat_data["filter_select"]] = update.message.text
    update.message.reply_text(f"Successfully set the filters for {context.chat_data['filter_select']} to {update.message.text}")


@config_handler.message_handler()
@config_handler.goto(config_filters_apply)
def config_filters_query_sub_filters(update: telegram.Update, context: CallbackContext):
    context.chat_data["filter_select"] = update.message.text
    update.message.reply_text("Please specify the value to modify")


@config_handler.message_handler(Filters.regex(r"filter"))
@config_handler.goto(config_filters_query_sub_filters)
def config_filters_query(update: telegram.Update, context: CallbackContext):

    def partitioner(lists, num_per_rows=4):
        """generate 4 items per row"""
        start = 0
        while start < len(lists):
            yield list(itertools.islice(lists, start, start+num_per_rows))
            start += num_per_rows

    config = Config()
    markup = telegram.ReplyKeyboardMarkup(list(partitioner(config.torrents_filter.keys())))
    update.message.reply_text("Please select the filters to modify", reply_markup=markup)


@config_handler.command_handler("config")
@config_handler.entry
@config_handler.goto(config_view_selects_query, config_filters_query)
def config_handler_init(update: telegram.Update, context: CallbackContext):
    markup = telegram.ReplyKeyboardMarkup([["Torrents filter", "Views select"]])
    update.message.reply_text("Please select the which config to changed.", reply_markup=markup)


@config_handler.command_handler("cancel")
@config_handler.fallback
def config_fail(update: telegram.Update, context: CallbackContext):
    update.message.reply_text("Error occured!")


def resume_all(update: telegram.Update, context: CallbackContext):
    config = Config()
    config.qbit_client.resume_all()


class Torznab:
    def search_torznab(self, update: telegram.Update, context: CallbackContext):
        update.message.text
        pass


if __name__ == '__main__':
    QBIT_LOGIN_ID = os.environ["QB_LOGIN_ID"]
    QBIT_LOGIN_PW = os.environ["QB_LOGIN_PW"]
    qb_client = qbittorrent.Client(IP)
    qb_client.login(QBIT_LOGIN_ID, QBIT_LOGIN_PW)
    Config().setup(qbit_client=qb_client)
    TOKEN = os.environ["TG_TOKEN"]
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("info", info))
    updater.dispatcher.add_handler(CommandHandler("resume", resume_all))
    updater.dispatcher.add_handler(config_handler.gen_conversation_handler())

    updater.start_polling()
    updater.idle()
