import collections
import itertools
import functools
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters


class StateHandler:
    """
    Contain sets of decorators to avoid having define the state yourself.
    >>> config_state = StateHandler("config")
    >>> @config_state.entry
    ... def config_init():
    ...     pass
    """
    def __init__(self, name=""):
        self.name = name
        self._state_val = 0
        self._state_mapping = collections.defaultdict(self._gen_state)
        self._entry_meth = []
        self._fall_back_meth = []
        self._func_handler_mapping = {}

    @staticmethod
    def _strip_decorators(func):
        try:
            return func.__wrapped__
        except AttributeError:
            return func

    def _gen_state(self):
        self._state_val += 1
        return self._state_val

    def message_handler(self, filter=Filters.all, *args, **kwargs):
        def _wrapper(f):
            self._func_handler_mapping[self._strip_decorators(f)] = MessageHandler(filter, f, *args, **kwargs)
            return f
        return _wrapper

    def command_handler(self, command, filter=Filters.all, *args, **kwargs):
        def _wrapper(f):
            self._func_handler_mapping[self._strip_decorators(f)] = CommandHandler(command, f, filter, *args, **kwargs)
            return f
        return _wrapper

    def goto(self, *goto_meth):
        # get the mapping first to register it into _state_mapping
        # strip goto_meth from any decorators
        goto_meth = {self._strip_decorators(meth) for meth in goto_meth}
        mapping_state = self._state_mapping[tuple(goto_meth)]

        def _wrapper(f):
            @functools.wraps(f)
            def _(*args, **kwargs):
                f(*args, **kwargs)
                return mapping_state
            return _
        return _wrapper

    def entry(self, entry_meth):
        self._entry_meth.append(self._strip_decorators(entry_meth))
        return entry_meth

    def fallback(self, fallback_meth):
        self._fall_back_meth.append(self._strip_decorators(fallback_meth))
        return fallback_meth

    def end(self, f):
        @functools.wraps(f)
        def _(*args, **kwargs):
            f(*args, **kwargs)
            return ConversationHandler.END
        return _

    def gen_conversation_handler(self):
        states = {}
        try:
            for func_tuple, state in self._state_mapping.items():
                states[state] = [self._func_handler_mapping[f] for f in func_tuple]
            conv = ConversationHandler(entry_points=[self._func_handler_mapping[self._strip_decorators(f)] for f in self._entry_meth], states=states,
                                       fallbacks=[self._func_handler_mapping[self._strip_decorators(f)] for f in self._fall_back_meth])
            return conv
        except KeyError:
            raise ValueError("did not register function as a handler yet!")


def partitioner(lists, num_per_rows=4):
    """partition list of buttons into multiple rows"""
    start = 0
    while start < len(lists):
        yield list(itertools.islice(lists, start, start+num_per_rows))
        start += num_per_rows

