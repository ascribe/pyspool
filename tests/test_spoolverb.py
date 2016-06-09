# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest


def test_spoolverb_init():
    from spool import Spoolverb
    spoolverb = Spoolverb(
        num_editions=10, edition_num=5, loan_start='150526', loan_end='150528')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions == 10
    assert spoolverb.edition_number == 5
    assert spoolverb.loan_start == '150526'
    assert spoolverb.loan_end == '150528'
    assert spoolverb.action is None


def test_spoolverb_piece_property():
    from spool import Spoolverb
    spoolverb = Spoolverb()
    assert spoolverb.piece == 'ASCRIBESPOOL01PIECE'


def test_spoolverb_register_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(edition_num=3)
    assert spoolverb.register == 'ASCRIBESPOOL01REGISTER3'


def test_spoolverb_editions_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(num_editions=7)
    assert spoolverb.editions == 'ASCRIBESPOOL01EDITIONS7'


def test_spoolverb_transafer_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(edition_num=9)
    assert spoolverb.transfer == 'ASCRIBESPOOL01TRANSFER9'


def test_spoolverb_consign_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(edition_num=3)
    assert spoolverb.consign == 'ASCRIBESPOOL01CONSIGN3'


def test_spoolverb_unconsign_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(edition_num=8)
    assert spoolverb.unconsign == 'ASCRIBESPOOL01UNCONSIGN8'


def test_spoolverb_loan_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(
        edition_num=4, loan_start='150526', loan_end='150528')
    assert spoolverb.loan == 'ASCRIBESPOOL01LOAN4/150526150528'


def test_spoolverb_migrate_property():
    from spool import Spoolverb
    spoolverb = Spoolverb(edition_num=5)
    assert spoolverb.migrate == 'ASCRIBESPOOL01MIGRATE5'


def test_spoolverb_consigned_registration_property():
    from spool import Spoolverb
    spoolverb = Spoolverb()
    assert (spoolverb.consigned_registration ==
            'ASCRIBESPOOL01CONSIGNEDREGISTRATION')


def test_spoolverb_fuel_property():
    from spool import Spoolverb
    spoolverb = Spoolverb()
    assert spoolverb.fuel == 'ASCRIBESPOOL01FUEL'


def test_from_verb_with_invalid_verb():
    from spool import Spoolverb
    from spool.spoolverb import SpoolverbError
    with pytest.raises(SpoolverbError) as exc:
        Spoolverb.from_verb('verbverbverb')
    assert exc.value.message == 'Invalid spoolverb: verbverbverb'


def test_from_verb_for_loans():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01LOAN5/150526150528')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 5
    assert spoolverb.loan_start == '150526'
    assert spoolverb.loan_end == '150528'
    assert spoolverb.action == 'LOAN'


def test_from_verb_for_editions():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01EDITIONS10')
    assert spoolverb.num_editions == 10


def test_from_verb_fuel():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01FUEL')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == ''
    assert spoolverb.action == 'FUEL'


def test_from_verb_piece():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01PIECE')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == ''
    assert spoolverb.action == 'PIECE'


def test_from_verb_consigned_registration():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01CONSIGNEDREGISTRATION')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == ''
    assert spoolverb.action == 'CONSIGNEDREGISTRATION'


def test_from_verb_register():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01REGISTER420')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 420
    assert spoolverb.action == 'REGISTER'


def test_from_verb_transfer():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01TRANSFER1729')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 1729
    assert spoolverb.action == 'TRANSFER'


def test_from_verb_consign():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01CONSIGN3')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 3
    assert spoolverb.action == 'CONSIGN'


def test_from_verb_unconsign():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01UNCONSIGN3')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 3
    assert spoolverb.action == 'UNCONSIGN'


def test_from_verb_migrate():
    from spool import Spoolverb
    spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01MIGRATE28')
    assert spoolverb.meta == 'ASCRIBESPOOL'
    assert spoolverb.version == '01'
    assert spoolverb.num_editions is None
    assert spoolverb.edition_number == 28
    assert spoolverb.action == 'MIGRATE'
