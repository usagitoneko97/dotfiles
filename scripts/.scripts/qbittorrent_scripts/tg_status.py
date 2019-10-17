#!/usr/bin/env python3
import os
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
import qbittorrent
import logging
import pprint
import tg_helper


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

FILTER_OPTION = {"filter": ["all", "downloading", "completed", "paused", "active", "inactive"],
                 "reverse": ["true", "false"]}

VIEW_OPTION = ["ratio", "tracker", "size", "dlspeed", "uploaded"]

logger = logging.getLogger(__name__)

IP = "http://192.168.1.105:9001"


class Config:
    __state = {}

    def __init__(self):
        self.__dict__ = self.__state

    def setup(self, filter="downloading", category="", sort="", reverse="false", limit=100,
              view_selects=None):
        self.torrents_filter = {
            "filter": filter,
            "category": category,
            "sort": sort,
            "reverse": reverse,
            "limit": limit,
        }
        self.views_select = view_selects or VIEW_OPTION

    @property
    def qbit_client(self):
        qb_client = qbittorrent.Client(IP)
        qb_client.login(QBIT_LOGIN_ID, QBIT_LOGIN_PW)
        return qb_client


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
    if update.message.text == "default":
        config.views_select = VIEW_OPTION
    else:
        config.views_select = list(update.message.text.split(" "))
    update.message.reply_text(f"Successfully update the views select to :{config.views_select}")


@config_handler.message_handler(Filters.regex(r"Views"))
@config_handler.goto(config_view_selects_apply)
def config_view_selects_query(update: telegram.Update, context: CallbackContext):
    kb = telegram.ReplyKeyboardMarkup([["default"]], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Select view from {}. Or type 'default' to restore to default".format(VIEW_OPTION),
                              reply_markup=kb)


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
    kb = None
    if update.message.text in FILTER_OPTION:
        kb = telegram.ReplyKeyboardMarkup(list(tg_helper.partitioner(FILTER_OPTION[update.message.text])),
                                          one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Please specify the value to modify", reply_markup=kb)


@config_handler.message_handler(Filters.regex(r"filter"))
@config_handler.goto(config_filters_query_sub_filters)
def config_filters_query(update: telegram.Update, context: CallbackContext):
    config = Config()
    markup = telegram.ReplyKeyboardMarkup(list(tg_helper.partitioner(config.torrents_filter.keys())),
                                          one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Please select the filters to modify", reply_markup=markup)


@config_handler.command_handler("config")
@config_handler.entry
@config_handler.goto(config_view_selects_query, config_filters_query)
def config_handler_init(update: telegram.Update, context: CallbackContext):
    markup = telegram.ReplyKeyboardMarkup([["Torrents filter", "Views select"]], one_time_keyboard=True,
                                          resize_keyboard=True)
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
    Config().setup()
    TOKEN = os.environ["TG_TOKEN"]
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("info", info))
    updater.dispatcher.add_handler(CommandHandler("resume", resume_all))
    updater.dispatcher.add_handler(config_handler.gen_conversation_handler())

    updater.start_polling()
    updater.idle()
