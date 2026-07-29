package com.migration.generated.libcbor.decoder;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.memory.MemoryAllocator;
import com.migration.generated.libcbor.memory.BufferPool;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;

public class CborDecoderEdgeCases {

    private Object decodeFromBytes(byte[] input) throws IOException {
        StreamsIo io = new StreamsIo(new ByteArrayInputStream(input), new ByteArrayOutputStream());
        MemoryAllocator mem = new MemoryAllocator(new BufferPool(1024));
        com.migration.generated.libcbor.decoder.CborDecoder dec = new com.migration.generated.libcbor.decoder.CborDecoder(io, mem);
        return dec.decode();
    }

    @Test
    public void testArrayEmpty() throws IOException {
        Object o = decodeFromBytes(new byte[]{(byte)0x80});
        assertTrue(o instanceof List);
        assertEquals(0, ((List<?>)o).size());
    }

    @Test
    public void testArrayTwo() throws IOException {
        Object o = decodeFromBytes(new byte[]{(byte)0x82, 0x01, 0x02});
        assertTrue(o instanceof List);
        List<?> l = (List<?>) o;
        assertEquals(2, l.size());
        assertEquals(1L, l.get(0));
        assertEquals(2L, l.get(1));
    }

    @Test
    public void testMapEmpty() throws IOException {
        Object o = decodeFromBytes(new byte[]{(byte)0xA0});
        assertTrue(o instanceof Map);
        assertTrue(((Map<?,?>)o).isEmpty());
    }

    @Test
    public void testMapTwoEntries() throws IOException {
        // {"A":1, "B":2}
        byte[] data = new byte[]{(byte)0xA2, 0x61, 'A', 0x61, 'B', 0x02};
        Object o = decodeFromBytes(data);
        assertTrue(o instanceof Map);
        Map<?,?> m = (Map<?,?>) o;
        assertEquals(2, m.size());
        assertEquals(1L, m.get("A"));
        assertEquals(2L, m.get("B"));
    }

    @Test
    public void testArrayWithNestedArray() throws IOException {
        // [1, [2,3]]
        Object o = decodeFromBytes(new byte[]{(byte)0x82, 0x01, (byte)0x82, 0x02, 0x03});
        assertTrue(o instanceof List);
        List<?> outer = (List<?>) o;
        assertEquals(2, outer.size());
        assertEquals(1L, outer.get(0));
        assertTrue(outer.get(1) instanceof List);
        List<?> inner = (List<?>) outer.get(1);
        assertEquals(2, inner.size());
        assertEquals(2L, inner.get(0));
        assertEquals(3L, inner.get(1));
    }

    @Test
    public void testMapKeyStringValueInt() throws IOException {
        // {"A":2}
        Object o = decodeFromBytes(new byte[]{(byte)0xA1, 0x61, 'A', 0x02});
        assertTrue(o instanceof Map);
        Map<?,?> m = (Map<?,?>) o;
        assertEquals(1, m.size());
        assertEquals(2L, m.get("A"));
    }

    @Test
    public void testByteStringLength3() throws IOException {
        // major 2 length 3: 0x43
        Object o = decodeFromBytes(new byte[]{0x43, 0x01, 0x02, 0x03});
        assertTrue(o instanceof byte[]);
        byte[] arr = (byte[]) o;
        assertArrayEquals(new byte[]{1,2,3}, arr);
    }

    @Test
    public void testNegativeOneTwoThree() throws IOException {
        Object o1 = decodeFromBytes(new byte[]{(byte)0x20}); // -1
        Object o2 = decodeFromBytes(new byte[]{(byte)0x21}); // -2
        Object o3 = decodeFromBytes(new byte[]{(byte)0x23}); // -4
        assertEquals(-1L, o1);
        assertEquals(-2L, o2);
        assertEquals(-4L, o3);
    }

    @Test
    public void testTextLength4() throws IOException {
        Object o = decodeFromBytes(new byte[]{0x64, 'A','B','C','D'});
        assertEquals("ABCD", o);
    }
}
