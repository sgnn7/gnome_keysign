import logger

from monkeysign.gpg import Keyring

def parse_sig_list(text, log = logger.get_instance()):
    '''Parses GnuPG's signature list (i.e. list-sigs)

    The format is described in the GnuPG man page'''
    sigslist = []
    for block in text.split("\n"):
        if block.startswith("sig"):
            record = block.split(":")
            log.debug("sig record (%d) %s", len(record), record)
            keyid, timestamp, uid = record[4], record[5], record[9]
            sigslist.append((keyid, timestamp, uid))

    return sigslist

# This is a cache for a keyring object, so that we do not need
# to create a new object every single time we parse signatures
# XXX Uberbad
_keyring = None
def signatures_for_keyid(keyid, keyring = None):
    '''Returns the list of signatures for a given key id

    This will call out to GnuPG list-sigs, using Monkeysign,
    and parse the resulting string into a list of signatures.

    A default Keyring will be used unless you pass an instance
    as keyring argument.
    '''
    # Retrieving a cached instance of a keyring,
    # unless we were being passed a keyring
    global _keyring
    if keyring:
        kr = keyring
    else:
        if not _keyring:
            _keyring = Keyring()
        kr = _keyring

    # FIXME: this would be better if it was done in monkeysign
    kr.context.call_command(['list-sigs', keyid])

    siglist = parse_sig_list(kr.context.stdout)

    return siglist