package com.migration.generated.libcbor.decoder;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

// Note: These imports will fail because libcbor_output_2 is a fallback with no implementation
import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.memory.MemoryAllocator;
import com.migration.generated.libcbor.memory.BufferPool;
import com.migration.generated.libcbor.decoder.CborDecoder;

public class CborDecoderTest {

    private Object decodeFromBytes(byte[] input) throws IOException {
        StreamsIo io = new StreamsIo(new ByteArrayInputStream(input), new ByteArrayOutputStream());
        MemoryAllocator mem = new MemoryAllocator(new BufferPool(1024));
        CborDecoder dec = new CborDecoder(io, mem);
        return dec.decode();
    }

    @Test
    public void testUnsignedImmediate0() throws IOException {
        assertEquals(0L, decodeFromBytes(new byte[]{0x00}));
    }

    @Test
    public void testUnsignedImmediate5() throws IOException {
        assertEquals(5L, decodeFromBytes(new byte[]{0x05}));
    }

    @Test
    public void testUnsignedOneByte() throws IOException {
        assertEquals(42L, decodeFromBytes(new byte[]{0x18, 0x2A}));
    }

    @Test
    public void testUnsignedTwoBytes() throws IOException {
        assertEquals(258L, decodeFromBytes(new byte[]{0x19, 0x01, (byte)0x02}));
    }

    @Test
    public void testUnsignedFourBytes() throws IOException {
        assertEquals(256L, decodeFromBytes(new byte[]{(byte)0x1A, 0x00, 0x00, 0x01, 0x00}));
    }

    @Test
    public void testUnsignedEightBytes() throws IOException {
        assertEquals(65536L, decodeFromBytes(new byte[]{0x1B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00}));
    }

    @Test
    public void testTextShort() throws IOException {
        assertEquals("bar", decodeFromBytes(new byte[]{0x63, 'b', 'a', 'r'}));
    }

    @Test
    public void testTextLongOneByteLength() throws IOException {
        assertEquals("abcde", decodeFromBytes(new byte[]{0x78, 0x05, 'a', 'b', 'c', 'd', 'e'}));
    }

    @Test
    public void testTextLongTwoByteLength() throws IOException {
        assertEquals("abcde", decodeFromBytes(new byte[]{0x79, 0x00, 0x05, 'a', 'b', 'c', 'd', 'e'}));
    }

    @Test
    public void testTextEmpty() throws IOException {
        assertEquals("", decodeFromBytes(new byte[]{0x60}));
    }

    @Test
    public void testByteStringShort() throws IOException {
        assertArrayEquals(new byte[]{1,2,3}, (byte[]) decodeFromBytes(new byte[]{0x43, 0x01, 0x02, 0x03}));
    }

    @Test
    public void testByteStringEmpty() throws IOException {
        assertArrayEquals(new byte[0], (byte[]) decodeFromBytes(new byte[]{0x40}));
    }

    @Test
    public void testByteStringOneByteLength() throws IOException {
        assertArrayEquals(new byte[]{10,11,12,13,14},
            (byte[]) decodeFromBytes(new byte[]{0x58, 0x05, 10,11,12,13,14}));
    }

    @Test
    public void testEmptyInputNull() throws IOException {
        assertNull(decodeFromBytes(new byte[]{}));
    }

    @Test
    public void testUnsignedTwoBytesZeroHigh() throws IOException {
        assertEquals(256L, decodeFromBytes(new byte[]{0x19, 0x01, 0x00}));
    }

    @Test
    public void testUnsignedFourBytesZero() throws IOException {
        assertEquals(65536L, decodeFromBytes(new byte[]{(byte)0x1A, 0x00, 0x01, 0x00, 0x00}));
    }

    @Test
    public void testUnsignedEightBytesValue1() throws IOException {
        assertEquals(1L, decodeFromBytes(new byte[]{0x1B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01}));
    }

    @Test
    public void testByteStringLongOneByteLength() throws IOException {
        byte[] data = new byte[]{0x58, 0x08, 0,1,2,3,4,5,6,7};
        assertArrayEquals(new byte[]{0,1,2,3,4,5,6,7}, (byte[]) decodeFromBytes(data));
    }

    @Test
    public void testUnsignedOneByteSmallAndBytesFollow() throws IOException {
        assertEquals(1L, decodeFromBytes(new byte[]{0x01, 0x02}) );
    }

}
