package com.migration.generated.libcbor.decoder;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.memory.MemoryAllocator;
import com.migration.generated.libcbor.memory.BufferPool;
import com.migration.generated.libcbor.decoder.CborDecoder;

public class CborDecoderTest {

    private Object decodeFromBytes(byte[] input) {
        try {
            StreamsIo io = new StreamsIo(new ByteArrayInputStream(input), new ByteArrayOutputStream());
            MemoryAllocator mem = new MemoryAllocator(new BufferPool(1024));
            CborDecoder dec = new CborDecoder(io, mem);
            return dec.decode();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    public void testUnsignedImmediate0() {
        assertEquals(0L, decodeFromBytes(new byte[]{(byte)0x00}));
    }

    @Test
    public void testUnsignedImmediate1() {
        assertEquals(1L, decodeFromBytes(new byte[]{(byte)0x01}));
    }

    @Test
    public void testUnsignedImmediate2() {
        assertEquals(2L, decodeFromBytes(new byte[]{(byte)0x02}));
    }

    @Test
    public void testUnsignedImmediate3() {
        assertEquals(3L, decodeFromBytes(new byte[]{(byte)0x03}));
    }

    @Test
    public void testUnsignedImmediate4() {
        assertEquals(4L, decodeFromBytes(new byte[]{(byte)0x04}));
    }

    @Test
    public void testUnsignedImmediate5() {
        assertEquals(5L, decodeFromBytes(new byte[]{(byte)0x05}));
    }

    @Test
    public void testUnsignedImmediate6() {
        assertEquals(6L, decodeFromBytes(new byte[]{(byte)0x06}));
    }

    @Test
    public void testUnsignedImmediate7() {
        assertEquals(7L, decodeFromBytes(new byte[]{(byte)0x07}));
    }

    @Test
    public void testUnsignedImmediate8() {
        assertEquals(8L, decodeFromBytes(new byte[]{(byte)0x08}));
    }

    @Test
    public void testUnsignedImmediate9() {
        assertEquals(9L, decodeFromBytes(new byte[]{(byte)0x09}));
    }

    @Test
    public void testUnsignedImmediate10() {
        assertEquals(10L, decodeFromBytes(new byte[]{(byte)0x0A}));
    }

    @Test
    public void testUnsignedImmediate11() {
        assertEquals(11L, decodeFromBytes(new byte[]{(byte)0x0B}));
    }

    @Test
    public void testUnsignedImmediate12() {
        assertEquals(12L, decodeFromBytes(new byte[]{(byte)0x0C}));
    }

    @Test
    public void testUnsignedImmediate13() {
        assertEquals(13L, decodeFromBytes(new byte[]{(byte)0x0D}));
    }

    @Test
    public void testUnsignedImmediate14() {
        assertEquals(14L, decodeFromBytes(new byte[]{(byte)0x0E}));
    }

    @Test
    public void testUnsignedImmediate15() {
        assertEquals(15L, decodeFromBytes(new byte[]{(byte)0x0F}));
    }

    @Test
    public void testUnsignedImmediate16() {
        assertEquals(16L, decodeFromBytes(new byte[]{(byte)0x10}));
    }

    @Test
    public void testUnsignedImmediate17() {
        assertEquals(17L, decodeFromBytes(new byte[]{(byte)0x11}));
    }

    @Test
    public void testUnsignedImmediate18() {
        assertEquals(18L, decodeFromBytes(new byte[]{(byte)0x12}));
    }

    @Test
    public void testUnsignedImmediate19() {
        assertEquals(19L, decodeFromBytes(new byte[]{(byte)0x13}));
    }

    @Test
    public void testUnsignedImmediate20() {
        assertEquals(20L, decodeFromBytes(new byte[]{(byte)0x14}));
    }

    @Test
    public void testUnsignedImmediate21() {
        assertEquals(21L, decodeFromBytes(new byte[]{(byte)0x15}));
    }

    @Test
    public void testUnsignedImmediate22() {
        assertEquals(22L, decodeFromBytes(new byte[]{(byte)0x16}));
    }

    @Test
    public void testUnsignedImmediate23() {
        assertEquals(23L, decodeFromBytes(new byte[]{(byte)0x17}));
    }

    @Test
    public void testUnsignedOneByte24() {
        assertEquals(24L, decodeFromBytes(new byte[]{0x18, (byte)0x18}));
    }

    @Test
    public void testUnsignedOneByte25() {
        assertEquals(25L, decodeFromBytes(new byte[]{0x18, (byte)0x19}));
    }

    @Test
    public void testUnsignedOneByte26() {
        assertEquals(26L, decodeFromBytes(new byte[]{0x18, (byte)0x1A}));
    }

    @Test
    public void testUnsignedOneByte27() {
        assertEquals(27L, decodeFromBytes(new byte[]{0x18, (byte)0x1B}));
    }

    @Test
    public void testUnsignedOneByte28() {
        assertEquals(28L, decodeFromBytes(new byte[]{0x18, (byte)0x1C}));
    }

    @Test
    public void testUnsignedOneByte29() {
        assertEquals(29L, decodeFromBytes(new byte[]{0x18, (byte)0x1D}));
    }

    @Test
    public void testUnsignedOneByte30() {
        assertEquals(30L, decodeFromBytes(new byte[]{0x18, (byte)0x1E}));
    }

    @Test
    public void testUnsignedOneByte31() {
        assertEquals(31L, decodeFromBytes(new byte[]{0x18, (byte)0x1F}));
    }

    @Test
    public void testUnsignedOneByte32() {
        assertEquals(32L, decodeFromBytes(new byte[]{0x18, (byte)0x20}));
    }

    @Test
    public void testUnsignedOneByte33() {
        assertEquals(33L, decodeFromBytes(new byte[]{0x18, (byte)0x21}));
    }

    @Test
    public void testUnsignedOneByte34() {
        assertEquals(34L, decodeFromBytes(new byte[]{0x18, (byte)0x22}));
    }

    @Test
    public void testUnsignedOneByte35() {
        assertEquals(35L, decodeFromBytes(new byte[]{0x18, (byte)0x23}));
    }

    @Test
    public void testUnsignedOneByte36() {
        assertEquals(36L, decodeFromBytes(new byte[]{0x18, (byte)0x24}));
    }

    @Test
    public void testUnsignedOneByte37() {
        assertEquals(37L, decodeFromBytes(new byte[]{0x18, (byte)0x25}));
    }

    @Test
    public void testUnsignedOneByte38() {
        assertEquals(38L, decodeFromBytes(new byte[]{0x18, (byte)0x26}));
    }

    @Test
    public void testUnsignedOneByte39() {
        assertEquals(39L, decodeFromBytes(new byte[]{0x18, (byte)0x27}));
    }

    @Test
    public void testUnsignedOneByte40() {
        assertEquals(40L, decodeFromBytes(new byte[]{0x18, (byte)0x28}));
    }

    @Test
    public void testUnsignedOneByte41() {
        assertEquals(41L, decodeFromBytes(new byte[]{0x18, (byte)0x29}));
    }

    @Test
    public void testUnsignedOneByte42() {
        assertEquals(42L, decodeFromBytes(new byte[]{0x18, (byte)0x2A}));
    }

    @Test
    public void testUnsignedOneByte43() {
        assertEquals(43L, decodeFromBytes(new byte[]{0x18, (byte)0x2B}));
    }

    @Test
    public void testUnsignedOneByte44() {
        assertEquals(44L, decodeFromBytes(new byte[]{0x18, (byte)0x2C}));
    }

    @Test
    public void testUnsignedOneByte45() {
        assertEquals(45L, decodeFromBytes(new byte[]{0x18, (byte)0x2D}));
    }

    @Test
    public void testUnsignedOneByte46() {
        assertEquals(46L, decodeFromBytes(new byte[]{0x18, (byte)0x2E}));
    }

    @Test
    public void testUnsignedOneByte47() {
        assertEquals(47L, decodeFromBytes(new byte[]{0x18, (byte)0x2F}));
    }

    @Test
    public void testUnsignedOneByte48() {
        assertEquals(48L, decodeFromBytes(new byte[]{0x18, (byte)0x30}));
    }

    @Test
    public void testUnsignedOneByte49() {
        assertEquals(49L, decodeFromBytes(new byte[]{0x18, (byte)0x31}));
    }

    @Test
    public void testUnsignedOneByte50() {
        assertEquals(50L, decodeFromBytes(new byte[]{0x18, (byte)0x32}));
    }

    @Test
    public void testUnsignedOneByte51() {
        assertEquals(51L, decodeFromBytes(new byte[]{0x18, (byte)0x33}));
    }

    @Test
    public void testUnsignedOneByte52() {
        assertEquals(52L, decodeFromBytes(new byte[]{0x18, (byte)0x34}));
    }

    @Test
    public void testUnsignedOneByte53() {
        assertEquals(53L, decodeFromBytes(new byte[]{0x18, (byte)0x35}));
    }

    @Test
    public void testUnsignedOneByte54() {
        assertEquals(54L, decodeFromBytes(new byte[]{0x18, (byte)0x36}));
    }

    @Test
    public void testUnsignedOneByte55() {
        assertEquals(55L, decodeFromBytes(new byte[]{0x18, (byte)0x37}));
    }

    @Test
    public void testUnsignedOneByte56() {
        assertEquals(56L, decodeFromBytes(new byte[]{0x18, (byte)0x38}));
    }

    @Test
    public void testUnsignedOneByte57() {
        assertEquals(57L, decodeFromBytes(new byte[]{0x18, (byte)0x39}));
    }

    @Test
    public void testUnsignedOneByte58() {
        assertEquals(58L, decodeFromBytes(new byte[]{0x18, (byte)0x3A}));
    }

    @Test
    public void testUnsignedOneByte59() {
        assertEquals(59L, decodeFromBytes(new byte[]{0x18, (byte)0x3B}));
    }

    @Test
    public void testUnsignedOneByte60() {
        assertEquals(60L, decodeFromBytes(new byte[]{0x18, (byte)0x3C}));
    }

    @Test
    public void testUnsignedOneByte61() {
        assertEquals(61L, decodeFromBytes(new byte[]{0x18, (byte)0x3D}));
    }

    @Test
    public void testUnsignedOneByte62() {
        assertEquals(62L, decodeFromBytes(new byte[]{0x18, (byte)0x3E}));
    }

    @Test
    public void testUnsignedOneByte63() {
        assertEquals(63L, decodeFromBytes(new byte[]{0x18, (byte)0x3F}));
    }

    @Test
    public void testUnsignedTwoBytes256() {
        assertEquals(256L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x00}));
    }

    @Test
    public void testUnsignedTwoBytes257() {
        assertEquals(257L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x01}));
    }

    @Test
    public void testUnsignedTwoBytes258() {
        assertEquals(258L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x02}));
    }

    @Test
    public void testUnsignedTwoBytes259() {
        assertEquals(259L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x03}));
    }

    @Test
    public void testUnsignedTwoBytes260() {
        assertEquals(260L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x04}));
    }

    @Test
    public void testUnsignedTwoBytes261() {
        assertEquals(261L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x05}));
    }

    @Test
    public void testUnsignedTwoBytes262() {
        assertEquals(262L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x06}));
    }

    @Test
    public void testUnsignedTwoBytes263() {
        assertEquals(263L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x07}));
    }

    @Test
    public void testUnsignedTwoBytes264() {
        assertEquals(264L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x08}));
    }

    @Test
    public void testUnsignedTwoBytes265() {
        assertEquals(265L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x09}));
    }

    @Test
    public void testUnsignedTwoBytes266() {
        assertEquals(266L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0A}));
    }

    @Test
    public void testUnsignedTwoBytes267() {
        assertEquals(267L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0B}));
    }

    @Test
    public void testUnsignedTwoBytes268() {
        assertEquals(268L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0C}));
    }

    @Test
    public void testUnsignedTwoBytes269() {
        assertEquals(269L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0D}));
    }

    @Test
    public void testUnsignedTwoBytes270() {
        assertEquals(270L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0E}));
    }

    @Test
    public void testUnsignedTwoBytes271() {
        assertEquals(271L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x0F}));
    }

    @Test
    public void testUnsignedTwoBytes272() {
        assertEquals(272L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x10}));
    }

    @Test
    public void testUnsignedTwoBytes273() {
        assertEquals(273L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x11}));
    }

    @Test
    public void testUnsignedTwoBytes274() {
        assertEquals(274L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x12}));
    }

    @Test
    public void testUnsignedTwoBytes275() {
        assertEquals(275L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x13}));
    }

    @Test
    public void testUnsignedTwoBytes276() {
        assertEquals(276L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x14}));
    }

    @Test
    public void testUnsignedTwoBytes277() {
        assertEquals(277L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x15}));
    }

    @Test
    public void testUnsignedTwoBytes278() {
        assertEquals(278L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x16}));
    }

    @Test
    public void testUnsignedTwoBytes279() {
        assertEquals(279L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x17}));
    }

    @Test
    public void testUnsignedTwoBytes280() {
        assertEquals(280L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x18}));
    }

    @Test
    public void testUnsignedTwoBytes281() {
        assertEquals(281L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x19}));
    }

    @Test
    public void testUnsignedTwoBytes282() {
        assertEquals(282L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x1A}));
    }

    @Test
    public void testUnsignedTwoBytes283() {
        assertEquals(283L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x1B}));
    }

    @Test
    public void testUnsignedTwoBytes284() {
        assertEquals(284L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x1C}));
    }

    @Test
    public void testUnsignedTwoBytes285() {
        assertEquals(285L, decodeFromBytes(new byte[]{0x19, (byte)0x01, (byte)0x1D}));
    }

    @Test
    public void testUnsignedFourBytes65536() {
        assertEquals(65536L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testUnsignedFourBytes65537() {
        assertEquals(65537L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x01}));
    }

    @Test
    public void testUnsignedFourBytes65538() {
        assertEquals(65538L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x02}));
    }

    @Test
    public void testUnsignedFourBytes65539() {
        assertEquals(65539L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x03}));
    }

    @Test
    public void testUnsignedFourBytes65540() {
        assertEquals(65540L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x04}));
    }

    @Test
    public void testUnsignedFourBytes65541() {
        assertEquals(65541L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x05}));
    }

    @Test
    public void testUnsignedFourBytes65542() {
        assertEquals(65542L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x06}));
    }

    @Test
    public void testUnsignedFourBytes65543() {
        assertEquals(65543L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x07}));
    }

    @Test
    public void testUnsignedFourBytes65544() {
        assertEquals(65544L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x08}));
    }

    @Test
    public void testUnsignedFourBytes65545() {
        assertEquals(65545L, decodeFromBytes(new byte[]{(byte)0x1A, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x09}));
    }

    @Test
    public void testUnsignedEightBytes4294967296() {
        assertEquals(4294967296L, decodeFromBytes(new byte[]{0x1B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testUnsignedEightBytes4294967297() {
        assertEquals(4294967297L, decodeFromBytes(new byte[]{0x1B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01}));
    }

    @Test
    public void testUnsignedEightBytes4294967298() {
        assertEquals(4294967298L, decodeFromBytes(new byte[]{0x1B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x02}));
    }

    @Test
    public void testUnsignedEightBytes4294967299() {
        assertEquals(4294967299L, decodeFromBytes(new byte[]{0x1B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x03}));
    }

    @Test
    public void testUnsignedEightBytes4294967300() {
        assertEquals(4294967300L, decodeFromBytes(new byte[]{0x1B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x01, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x04}));
    }

    @Test
    public void testNegativeImmediate0() {
        assertEquals(-1L, decodeFromBytes(new byte[]{(byte)0x20}));
    }

    @Test
    public void testNegativeImmediate1() {
        assertEquals(-2L, decodeFromBytes(new byte[]{(byte)0x21}));
    }

    @Test
    public void testNegativeImmediate2() {
        assertEquals(-3L, decodeFromBytes(new byte[]{(byte)0x22}));
    }

    @Test
    public void testNegativeImmediate3() {
        assertEquals(-4L, decodeFromBytes(new byte[]{(byte)0x23}));
    }

    @Test
    public void testNegativeImmediate4() {
        assertEquals(-5L, decodeFromBytes(new byte[]{(byte)0x24}));
    }

    @Test
    public void testNegativeImmediate5() {
        assertEquals(-6L, decodeFromBytes(new byte[]{(byte)0x25}));
    }

    @Test
    public void testNegativeImmediate6() {
        assertEquals(-7L, decodeFromBytes(new byte[]{(byte)0x26}));
    }

    @Test
    public void testNegativeImmediate7() {
        assertEquals(-8L, decodeFromBytes(new byte[]{(byte)0x27}));
    }

    @Test
    public void testNegativeImmediate8() {
        assertEquals(-9L, decodeFromBytes(new byte[]{(byte)0x28}));
    }

    @Test
    public void testNegativeImmediate9() {
        assertEquals(-10L, decodeFromBytes(new byte[]{(byte)0x29}));
    }

    @Test
    public void testNegativeImmediate10() {
        assertEquals(-11L, decodeFromBytes(new byte[]{(byte)0x2A}));
    }

    @Test
    public void testNegativeImmediate11() {
        assertEquals(-12L, decodeFromBytes(new byte[]{(byte)0x2B}));
    }

    @Test
    public void testNegativeImmediate12() {
        assertEquals(-13L, decodeFromBytes(new byte[]{(byte)0x2C}));
    }

    @Test
    public void testNegativeImmediate13() {
        assertEquals(-14L, decodeFromBytes(new byte[]{(byte)0x2D}));
    }

    @Test
    public void testNegativeImmediate14() {
        assertEquals(-15L, decodeFromBytes(new byte[]{(byte)0x2E}));
    }

    @Test
    public void testNegativeImmediate15() {
        assertEquals(-16L, decodeFromBytes(new byte[]{(byte)0x2F}));
    }

    @Test
    public void testNegativeImmediate16() {
        assertEquals(-17L, decodeFromBytes(new byte[]{(byte)0x30}));
    }

    @Test
    public void testNegativeImmediate17() {
        assertEquals(-18L, decodeFromBytes(new byte[]{(byte)0x31}));
    }

    @Test
    public void testNegativeImmediate18() {
        assertEquals(-19L, decodeFromBytes(new byte[]{(byte)0x32}));
    }

    @Test
    public void testNegativeImmediate19() {
        assertEquals(-20L, decodeFromBytes(new byte[]{(byte)0x33}));
    }

    @Test
    public void testNegativeImmediate20() {
        assertEquals(-21L, decodeFromBytes(new byte[]{(byte)0x34}));
    }

    @Test
    public void testNegativeImmediate21() {
        assertEquals(-22L, decodeFromBytes(new byte[]{(byte)0x35}));
    }

    @Test
    public void testNegativeImmediate22() {
        assertEquals(-23L, decodeFromBytes(new byte[]{(byte)0x36}));
    }

    @Test
    public void testNegativeImmediate23() {
        assertEquals(-24L, decodeFromBytes(new byte[]{(byte)0x37}));
    }

    @Test
    public void testNegativeOneByte24() {
        assertEquals(-25L, decodeFromBytes(new byte[]{0x38, (byte)0x18}));
    }

    @Test
    public void testNegativeOneByte25() {
        assertEquals(-26L, decodeFromBytes(new byte[]{0x38, (byte)0x19}));
    }

    @Test
    public void testNegativeOneByte26() {
        assertEquals(-27L, decodeFromBytes(new byte[]{0x38, (byte)0x1A}));
    }

    @Test
    public void testNegativeOneByte27() {
        assertEquals(-28L, decodeFromBytes(new byte[]{0x38, (byte)0x1B}));
    }

    @Test
    public void testNegativeOneByte28() {
        assertEquals(-29L, decodeFromBytes(new byte[]{0x38, (byte)0x1C}));
    }

    @Test
    public void testNegativeOneByte29() {
        assertEquals(-30L, decodeFromBytes(new byte[]{0x38, (byte)0x1D}));
    }

    @Test
    public void testNegativeOneByte30() {
        assertEquals(-31L, decodeFromBytes(new byte[]{0x38, (byte)0x1E}));
    }

    @Test
    public void testNegativeOneByte31() {
        assertEquals(-32L, decodeFromBytes(new byte[]{0x38, (byte)0x1F}));
    }

    @Test
    public void testNegativeOneByte32() {
        assertEquals(-33L, decodeFromBytes(new byte[]{0x38, (byte)0x20}));
    }

    @Test
    public void testNegativeOneByte33() {
        assertEquals(-34L, decodeFromBytes(new byte[]{0x38, (byte)0x21}));
    }

    @Test
    public void testNegativeOneByte34() {
        assertEquals(-35L, decodeFromBytes(new byte[]{0x38, (byte)0x22}));
    }

    @Test
    public void testNegativeOneByte35() {
        assertEquals(-36L, decodeFromBytes(new byte[]{0x38, (byte)0x23}));
    }

    @Test
    public void testNegativeOneByte36() {
        assertEquals(-37L, decodeFromBytes(new byte[]{0x38, (byte)0x24}));
    }

    @Test
    public void testNegativeOneByte37() {
        assertEquals(-38L, decodeFromBytes(new byte[]{0x38, (byte)0x25}));
    }

    @Test
    public void testNegativeOneByte38() {
        assertEquals(-39L, decodeFromBytes(new byte[]{0x38, (byte)0x26}));
    }

    @Test
    public void testNegativeOneByte39() {
        assertEquals(-40L, decodeFromBytes(new byte[]{0x38, (byte)0x27}));
    }

    @Test
    public void testNegativeOneByte40() {
        assertEquals(-41L, decodeFromBytes(new byte[]{0x38, (byte)0x28}));
    }

    @Test
    public void testNegativeOneByte41() {
        assertEquals(-42L, decodeFromBytes(new byte[]{0x38, (byte)0x29}));
    }

    @Test
    public void testNegativeOneByte42() {
        assertEquals(-43L, decodeFromBytes(new byte[]{0x38, (byte)0x2A}));
    }

    @Test
    public void testNegativeOneByte43() {
        assertEquals(-44L, decodeFromBytes(new byte[]{0x38, (byte)0x2B}));
    }

    @Test
    public void testByteStringLen0() {
        assertArrayEquals(new byte[]{}, (byte[]) decodeFromBytes(new byte[]{(byte)0x40}));
    }

    @Test
    public void testByteStringLen1() {
        assertArrayEquals(new byte[]{1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x41, 0x01}));
    }

    @Test
    public void testByteStringLen2() {
        assertArrayEquals(new byte[]{1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x42, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen3() {
        assertArrayEquals(new byte[]{1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x43, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen4() {
        assertArrayEquals(new byte[]{1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x44, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen5() {
        assertArrayEquals(new byte[]{1,1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x45, 0x01, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen6() {
        assertArrayEquals(new byte[]{1,1,1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x46, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen7() {
        assertArrayEquals(new byte[]{1,1,1,1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x47, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen8() {
        assertArrayEquals(new byte[]{1,1,1,1,1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x48, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testByteStringLen9() {
        assertArrayEquals(new byte[]{1,1,1,1,1,1,1,1,1}, (byte[]) decodeFromBytes(new byte[]{(byte)0x49, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01}));
    }

    @Test
    public void testTextStringLen0() {
        assertEquals("", decodeFromBytes(new byte[]{(byte)0x60}));
    }

    @Test
    public void testTextStringLen1() {
        assertEquals("a", decodeFromBytes(new byte[]{(byte)0x61, (byte)'a'}));
    }

    @Test
    public void testTextStringLen2() {
        assertEquals("aa", decodeFromBytes(new byte[]{(byte)0x62, (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen3() {
        assertEquals("aaa", decodeFromBytes(new byte[]{(byte)0x63, (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen4() {
        assertEquals("aaaa", decodeFromBytes(new byte[]{(byte)0x64, (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen5() {
        assertEquals("aaaaa", decodeFromBytes(new byte[]{(byte)0x65, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen6() {
        assertEquals("aaaaaa", decodeFromBytes(new byte[]{(byte)0x66, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen7() {
        assertEquals("aaaaaaa", decodeFromBytes(new byte[]{(byte)0x67, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen8() {
        assertEquals("aaaaaaaa", decodeFromBytes(new byte[]{(byte)0x68, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen9() {
        assertEquals("aaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x69, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen10() {
        assertEquals("aaaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x6A, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen11() {
        assertEquals("aaaaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x6B, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen12() {
        assertEquals("aaaaaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x6C, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen13() {
        assertEquals("aaaaaaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x6D, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testTextStringLen14() {
        assertEquals("aaaaaaaaaaaaaa", decodeFromBytes(new byte[]{(byte)0x6E, (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a', (byte)'a'}));
    }

    @Test
    public void testArraySize0() {
        assertEquals(java.util.List.of(), decodeFromBytes(new byte[]{(byte)0x80}));
    }

    @Test
    public void testArraySize1() {
        assertEquals(java.util.List.of(0L), decodeFromBytes(new byte[]{(byte)0x81, (byte)0x00}));
    }

    @Test
    public void testArraySize2() {
        assertEquals(java.util.List.of(0L,0L), decodeFromBytes(new byte[]{(byte)0x82, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize3() {
        assertEquals(java.util.List.of(0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x83, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize4() {
        assertEquals(java.util.List.of(0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x84, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize5() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x85, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize6() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x86, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize7() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x87, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize8() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x88, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize9() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x89, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize10() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x8A, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize11() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x8B, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize12() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x8C, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize13() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x8D, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testArraySize14() {
        assertEquals(java.util.List.of(0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L,0L), decodeFromBytes(new byte[]{(byte)0x8E, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00, (byte)0x00}));
    }

    @Test
    public void testBoolFalse() {
        assertEquals(false, decodeFromBytes(new byte[]{(byte)0xF4}));
    }

    @Test
    public void testBoolTrue() {
        assertEquals(true, decodeFromBytes(new byte[]{(byte)0xF5}));
    }

    @Test
    public void testNull() {
        assertNull(decodeFromBytes(new byte[]{(byte)0xF6}));
    }

    @Test
    public void testDoubleZero() {
        assertEquals(0.0, decodeFromBytes(new byte[]{(byte)0xFB, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}));
    }

    @Test
    public void testDoubleOne() {
        assertEquals(1.0, decodeFromBytes(new byte[]{(byte)0xFB, 0x3F, (byte)0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}));
    }
}
