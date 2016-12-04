import os
import traceback

from mailpile.mail_source import BaseMailSource
from mailpile.mailboxes import pop3
from mailpile.mailutils import FormatMbxId, MBX_ID_LEN
from mailpile.i18n import gettext as _
from mailpile.i18n import ngettext as _n
from mailpile.util import *


def _open_pop3_mailbox(event, host, port, username, password, protocol, debug):
    cev = event.data['connection'] = {
        'live': False,
        'error': [False, _('Nothing is wrong')]
    }
    try:
        return pop3.MailpileMailbox(host,
                                    port=port,
                                    user=username,
                                    password=password,
                                    use_ssl=('ssl' in protocol),
                                    debug=debug)
    except AccessError:
        cev['error'] = ['auth', _('Invalid username or password')]
    except (IOError, OSError):
        cev['error'] = ['network', _('A network error occurred')]
        event.data['traceback'] = traceback.format_exc()
    return None


class Pop3MailSource(BaseMailSource):
    """
    This is a mail source that watches over one or more POP3 mailboxes.
    """
    # This is a helper for the events.
    __classname__ = 'mailpile.mail_source.pop3.Pop3MailSource'

    def __init__(self, *args, **kwargs):
        BaseMailSource.__init__(self, *args, **kwargs)
        self.watching = -1

    def close(self):
        mbx = self.my_config.mailbox.values()[0]
        if mbx:
            pop3 = self.session.config.open_mailbox(self.session,
                                                    FormatMbxId(mbx._key),
                                                    prefer_local=False,
                                                    from_cache=True)
            if pop3:
                pop3.close() 

    def _sleep(self, *args, **kwargs):
        self.close()
        return BaseMailSource._sleep(self, *args, **kwargs)

    def open(self):
        with self._lock:
            mailboxes = self.my_config.mailbox.values()
            if self.watching == len(mailboxes):
                return True
            else:
                self.watching = len(mailboxes)

            for d in ('mailbox_state', ):
                if d not in self.event.data:
                    self.event.data[d] = {}
            self.event.data['connection'] = {
                'live': False,
                'error': [False, _('Nothing is wrong')]
            }

        self._log_status(_('Watching %d POP3 mailboxes') % self.watching)
        return True

    def _has_mailbox_changed(self, mbx, state):
        pop3 = self.session.config.open_mailbox(self.session,
                                                FormatMbxId(mbx._key),
                                                prefer_local=False)
        state['stat'] = stat = '%s' % (pop3.stat(), )
        return (self.event.data.get('mailbox_state', {}).get(mbx._key) != stat)

    def _mark_mailbox_rescanned(self, mbx, state):
        if 'mailbox_state' in self.event.data:
            self.event.data['mailbox_state'][mbx._key] = state['stat']
        else:
            self.event.data['mailbox_state'] = {mbx._key: state['stat']}

    def _fmt_path(self):
        return 'src:%s' % (self.my_config._key,)

    def open_mailbox(self, mbx_id, mfn):
        my_cfg = self.my_config
        if 'src:' in mfn[:5] and FormatMbxId(mbx_id) in my_cfg.mailbox:
            debug = ('pop3' in self.session.config.sys.debug) and 99 or 0
            return _open_pop3_mailbox(self.event,
                                      my_cfg.host, my_cfg.port,
                                      my_cfg.username, my_cfg.password,
                                      my_cfg.protocol, debug)
        return None

    def discover_mailboxes(self, paths=None):
        config = self.session.config
        existing = self._existing_mailboxes()
        if self._fmt_path() not in existing:
            idx = config.sys.mailbox.append(self._fmt_path())
            self.take_over_mailbox(idx)
            return 1
        return 0

    def is_mailbox(self, fn):
        return False


def TestPop3Settings(session, settings, event):
    conn = _open_pop3_mailbox(event,
                              settings['host'],
                              int(settings['port']),
                              settings['username'],
                              settings['password'],
                              settings['protocol'],
                              True)
    if conn:
        conn.close()
        return True
    return False
