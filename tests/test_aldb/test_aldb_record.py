"""Test the ALDB record data type."""
from random import randint
from unittest import TestCase

from pyinsteon.address import Address
from pyinsteon.aldb.aldb_record import ALDBRecord
from tests.utils import random_address


def _compare(
    rec: ALDBRecord,
    mem_addr: int,
    controller: bool,
    group: int,
    target: Address,
    data1: int,
    data2: int,
    data3: int,
    in_use: bool = True,
    hwm: bool = False,
    bit5: bool = False,
    bit4: bool = False,
):
    """Compare an ALDBRecord to a set of data."""
    assert rec.mem_addr == mem_addr
    assert rec.is_controller == controller
    assert rec.is_responder != controller
    assert rec.group == group
    assert rec.target == target
    assert rec.data1 == data1
    assert rec.data2 == data2
    assert rec.data3 == data3
    assert rec.is_in_use == in_use
    assert rec.is_high_water_mark == hwm
    assert rec.is_bit5_set == bit5
    assert rec.is_bit4_set == bit4


class TestAldbRecord(TestCase):
    """Test the ALDB record data type."""

    def test_create_with_all_values(self):
        """Test creating a new record with all values ."""
        mem_addr = randint(0, 0xFFFF)
        controller = bool(randint(0, 1))
        group = randint(0, 254)
        target = random_address()
        data1 = randint(0, 254)
        data2 = randint(0, 254)
        data3 = randint(0, 254)
        in_use = bool(randint(0, 1))
        hwm = bool(randint(0, 1))
        bit5 = bool(randint(0, 1))
        bit4 = bool(randint(0, 1))

        rec = ALDBRecord(
            memory=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            high_water_mark=hwm,
            bit4=bit4,
            bit5=bit5,
        )
        _compare(
            rec=rec,
            mem_addr=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            hwm=hwm,
            bit4=bit4,
            bit5=bit5,
        )

    def test_create_with_default_data(self):
        """Test creating a new record with default values ."""
        mem_addr = randint(0, 0xFFFF)
        controller = bool(randint(0, 1))
        group = randint(0, 254)
        target = random_address()
        data1 = randint(0, 254)
        data2 = randint(0, 254)
        data3 = randint(0, 254)

        rec = ALDBRecord(
            memory=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        _compare(
            rec=rec,
            mem_addr=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

    def test_eq(self):
        """Test if two records are equal."""
        mem_addr = randint(0, 0xFFFF)
        controller = bool(randint(0, 1))
        group = randint(0, 100)
        target = random_address()
        data1 = randint(0, 100)
        data2 = randint(0, 100)
        data3 = randint(0, 100)

        base_rec = ALDBRecord(
            memory=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

        eq_rec = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=controller,
            group=group,
            target=target,
            data1=randint(101, 254),
            data2=randint(101, 254),
            data3=data3,
            in_use=False,
            high_water_mark=True,
            bit4=True,
            bit5=True,
        )

        eq_rec_controller = ALDBRecord(
            memory=None,
            controller=controller,
            group=None,
            target=None,
            data1=None,
            data2=None,
            data3=None,
        )

        eq_rec_group = ALDBRecord(
            memory=None,
            controller=None,
            group=group,
            target=None,
            data1=None,
            data2=None,
            data3=None,
        )
        eq_rec_target = ALDBRecord(
            memory=None,
            controller=None,
            group=None,
            target=target,
            data1=None,
            data2=None,
            data3=None,
        )

        assert base_rec == eq_rec
        assert base_rec == eq_rec_controller
        assert base_rec == eq_rec_group
        assert base_rec == eq_rec_target

        base_data_3 = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=False,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        eq_rec_data3 = ALDBRecord(
            memory=None,
            controller=False,
            group=None,
            target=None,
            data1=None,
            data2=None,
            data3=data3,
        )
        ne_rec_data3 = ALDBRecord(
            memory=None,
            controller=False,
            group=None,
            target=None,
            data1=None,
            data2=None,
            data3=randint(101, 254),
        )
        assert base_data_3 == eq_rec_data3
        assert base_data_3 != ne_rec_data3

        base_data_3_contr = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=True,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        eq_rec_data3_contr = ALDBRecord(
            memory=None,
            controller=True,
            group=None,
            target=None,
            data1=None,
            data2=None,
            data3=randint(101, 255),
        )
        assert base_data_3_contr == eq_rec_data3_contr

        ne_rec_controller = ALDBRecord(
            memory=None,
            controller=not controller,
            group=None,
            target=None,
            data1=None,
            data2=None,
            data3=None,
        )

        ne_rec_group = ALDBRecord(
            memory=None,
            controller=None,
            group=randint(101, 255),
            target=None,
            data1=None,
            data2=None,
            data3=None,
        )
        ne_rec_target = ALDBRecord(
            memory=None,
            controller=None,
            group=None,
            target=random_address(),
            data1=None,
            data2=None,
            data3=None,
        )

        assert base_rec != ne_rec_controller
        assert base_rec != ne_rec_group
        assert base_rec != ne_rec_target

        ne_rec_controller = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=not controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

        ne_rec_group = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=controller,
            group=randint(101, 254),
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

        ne_rec_target = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=controller,
            group=group,
            target=random_address(),
            data1=data1,
            data2=data2,
            data3=data3,
        )

        ne_rec_data3 = ALDBRecord(
            memory=randint(0, 0xFFFF),
            controller=not controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=randint(101, 254),
        )

        assert base_rec != ne_rec_controller
        assert base_rec != ne_rec_group
        assert base_rec != ne_rec_target
        assert base_rec != ne_rec_data3
