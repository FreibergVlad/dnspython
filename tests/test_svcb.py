import unittest

import dns.rdata
import dns.rdtypes.svcbbase

class SVCBTestCase(unittest.TestCase):
    def check_valid_inputs(self, inputs):
        expected = inputs[0]
        for text in inputs:
            rr = dns.rdata.from_text('IN', 'SVCB', text)
            new_text = rr.to_text()
            self.assertEqual(expected, new_text)

    def check_invalid_inputs(self, inputs):
        for text in inputs:
            with self.assertRaises(dns.exception.SyntaxError):
                dns.rdata.from_text('IN', 'SVCB', text)

    def test_svcb_general_invalid(self):
        invalid_inputs = (
            # Duplicate keys
            "1 . alpn=h2 alpn=h3",
            "1 . alpn=h2 key1=h3",
            # Quoted keys
            "1 . \"alpn=h2\"",
            # Invalid space
            "1 . alpn= h2",
            "1 . alpn =h2",
            "1 . alpn = h2",
            "1 . alpn= \"h2\"",
            "1 . =alpn",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_mandatory(self):
        valid_inputs = (
            "1 . mandatory=\"alpn,no-default-alpn\" alpn=\"h2\" no-default-alpn",
            "1 . mandatory=alpn,no-default-alpn alpn=h2 no-default-alpn",
            "1 . mandatory=key1,key2 alpn=h2 no-default-alpn",
            "1 . mandatory=alpn,no-default-alpn key1=\\002h2 key2=\"\"",
            "1 . mandatory=alpn,no-default-alpn key1=\\002h2 key2",
            "1 . key0=\\000\\001\\000\\002 alpn=h2 no-default-alpn",
            "1 . alpn=h2 no-default-alpn mandatory=alpn,no-default-alpn",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            # unknown key
            "1 . mandatory=foo",
            # key 0
            "1 . mandatory=key0",
            "1 . mandatory=key0,alpn",
            # missing key
            "1 . mandatory=alpn",
            # duplicate
            "1 . mandatory=alpn,alpn alpn=h2",
            # invalid escaping
            "1 . mandatory=\\alpn alpn=h2",
            # 0 in wire format
            "1 . key0=\\000\\000",
            # invalid length in wire format
            "1 . key0=\\000",
            # out of order in wire format
            "1 . key0=\\000\\002\\000\\001 alpn=h2 no-default-alpn",
            # leading zeros
            "1 . mandatory=key1,key002 alpn=h2 no-default-alpn",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_alpn(self):
        valid_inputs_two_items = (
            "1 . alpn=\"h2,h3\"",
            "1 . alpn=h2,h3",
            "1 . alpn=h\\050,h3",
            "1 . alpn=\"h\\050,h3\"",
            "1 . alpn=\\h2,h3",
            "1 . key1=\\002h2\\002h3",
        )
        self.check_valid_inputs(valid_inputs_two_items)

        valid_inputs_one_item = (
            "1 . alpn=\"h2\\,h3\"",
            "1 . alpn=h2\\,h3",
            "1 . alpn=h2\\044h3",
        )
        self.check_valid_inputs(valid_inputs_one_item)

        invalid_inputs = (
            "1 . alpn=h2,,h3",
            "1 . alpn=01234567890abcdef01234567890abcdef01234567890abcdef"
                     "01234567890abcdef01234567890abcdef01234567890abcdef"
                     "01234567890abcdef01234567890abcdef01234567890abcdef"
                     "01234567890abcdef01234567890abcdef01234567890abcdef"
                     "01234567890abcdef01234567890abcdef01234567890abcdef"
                     "01234567890abcdef",
            "1 . key1=\\000",
            "1 . key1=\\002x",
            "1 . alpn=\",h2,h3\"",
            "1 . alpn=\"h2,h3,\"",
            "1 . alpn",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_no_default_alpn(self):
        valid_inputs = (
            "1 . no-default-alpn",
            "1 . no-default-alpn=\"\"",
            "1 . key2",
            "1 . key2=\"\"",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            "1 . no-default-alpn=foo",
            "1 . no-default-alpn=",
            "1 . key2=foo",
            "1 . key2=",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_port(self):
        valid_inputs = (
            "1 . port=\"53\"",
            "1 . port=53",
            "1 . key3=\\000\\053",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            "1 . port=",
            "1 . port=53x",
            "1 . port=x53",
            "1 . port=53,54",
            "1 . port=53\\,54",
            "1 . key3=\\000",
            "1 . port=65536",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_echconfig(self):
        valid_inputs = (
            "1 . echconfig=\"Zm9vMA==\"",
            "1 . echconfig=Zm9vMA==",
            "1 . key5=foo0",
            "1 . key5=\\102\\111\\111\\048",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            "1 . echconfig=",
            "1 . echconfig=Zm9vMA",
            "1 . echconfig=\\090m9vMA==",
            "1 . key5=",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_ipv4hint(self):
        valid_inputs = (
            "1 . ipv4hint=\"0.0.0.0,1.1.1.1\"",
            "1 . ipv4hint=0.0.0.0,1.1.1.1",
            "1 . key4=\\000\\000\\000\\000\\001\\001\\001\\001",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            "1 . ipv4hint=",
            "1 . ipv4hint=1234",
            "1 . ipv4hint=1\\.2.3.4",
            "1 . ipv4hint=1.2.3.4\\,2.3.4.5",
            "1 . ipv4hint",
            "1 . key4=",
            "1 . key4=123",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_ipv6hint(self):
        valid_inputs = (
            "1 . ipv6hint=\"::4,1::\"",
            "1 . ipv6hint=::4,1::",
            "1 . key6=\\000\\000\\000\\000\\000\\000\\000\\000"
                     "\\000\\000\\000\\000\\000\\000\\000\\004"
                     "\\000\\001\\000\\000\\000\\000\\000\\000"
                     "\\000\\000\\000\\000\\000\\000\\000\\000",
        )
        self.check_valid_inputs(valid_inputs)

        invalid_inputs = (
            "1 . ipv6hint=",
            "1 . ipv6hint=1234",
            "1 . ipv6hint=1\\::2",
            "1 . ipv6hint=::1\\,::2",
            "1 . ipv6hint",
            "1 . key6=",
            "1 . key6=123",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_unknown(self):
        valid_inputs_one_key = (
            "1 . key23=\"key45\"",
            "1 . key23=key45",
            "1 . key23=key\\052\\053",
            "1 . key23=\"key\\052\\053\"",
            "1 . key23=\\107\\101\\121\\052\\053",
        )
        self.check_valid_inputs(valid_inputs_one_key)

        valid_inputs_two_keys = (
            "1 . key24 key48",
            "1 . key24=\"\" key48",
        )
        self.check_valid_inputs(valid_inputs_two_keys)

        invalid_inputs = (
            "1 . key65536=foo",
            "1 . key24= key48",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_svcb_wire(self):
        valid_inputs = (
            "1 . mandatory=\"alpn,port\" alpn=\"h2\" port=\"257\"",
            "\\# 24 0001 00 0000000400010003 00010003026832 000300020101",
        )
        self.check_valid_inputs(valid_inputs)

        everything = \
            "100 foo.com. mandatory=\"alpn,port\" alpn=\"h2,h3\" " \
            "             no-default-alpn port=\"12345\" echconfig=\"abcd\" " \
            "             ipv4hint=1.2.3.4,4.3.2.1 ipv6hint=1::2,3::4" \
            "             key12345=\"foo\""
        rr = dns.rdata.from_text('IN', 'SVCB', everything)
        rr2 = dns.rdata.from_text('IN', 'SVCB', rr.to_generic().to_text())
        self.assertEqual(rr, rr2)

        invalid_inputs = (
            # As above, but the keys are out of order.
            "\\# 24 0001 00 0000000400010003 000300020101 00010003026832",
            # As above, but the mandatory keys don't match
            "\\# 24 0001 00 0000000400010002 000300020101 00010003026832",
            "\\# 24 0001 00 0000000400010004 000300020101 00010003026832",
        )
        self.check_invalid_inputs(invalid_inputs)

    def test_misc_escape(self):
        rdata = dns.rdata.from_text('in', 'svcb', '1 . alpn=\\010\\010')
        expected = '1 . alpn="\\010\\010"'
        self.assertEqual(rdata.to_text(), expected)
        with self.assertRaises(dns.exception.SyntaxError):
            dns.rdata.from_text('in', 'svcb', '1 . alpn=\\0')
        with self.assertRaises(dns.exception.SyntaxError):
            dns.rdata.from_text('in', 'svcb', '1 . alpn=\\00')
        with self.assertRaises(dns.exception.SyntaxError):
            dns.rdata.from_text('in', 'svcb', '1 . alpn=\\00q')
        # This doesn't usually get exercised, so we do it directly.
        gp = dns.rdtypes.svcbbase.GenericParam.from_value('\\001\\002')
        expected = '"\\001\\002"'
        self.assertEqual(gp.to_text(), expected)

    def test_alias_mode(self):
        rd = dns.rdata.from_text('in', 'svcb', '0 .')
        self.assertEqual(len(rd.params), 0)
        self.assertEqual(rd.target, dns.name.root)
        self.assertEqual(rd.to_text(), '0 .')
        rd = dns.rdata.from_text('in', 'svcb', '0 elsewhere.')
        self.assertEqual(rd.target, dns.name.from_text('elsewhere.'))
        self.assertEqual(len(rd.params), 0)
        # provoke 'parameters in AliasMode' from text.
        with self.assertRaises(dns.exception.SyntaxError):
            dns.rdata.from_text('in', 'svcb', '0 elsewhere. alpn=h2')
        # provoke 'parameters in AliasMode' from wire too.
        wire = bytes.fromhex('0000000000000400010003')
        with self.assertRaises(dns.exception.FormError):
            dns.rdata.from_wire('in', 'svcb', wire, 0, len(wire))

    def test_immutability(self):
        alpn = dns.rdtypes.svcbbase.ALPNParam.from_value(['h2', 'h3'])
        with self.assertRaises(TypeError):
            alpn.ids[0] = 'foo'
        with self.assertRaises(TypeError):
            del alpn.ids[0]
        with self.assertRaises(TypeError):
            alpn.ids = 'foo'
        with self.assertRaises(TypeError):
            del alpn.ids