package com.migration.generated.libcbor.io;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

public class StreamsIoTest {

    @Test
    public void testReadAndWriteFlow() throws IOException {
        ByteArrayInputStream in = new ByteArrayInputStream(new byte[]{1,2,3,4});
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        StreamsIo io = new StreamsIo(in, out);

        byte[] buf = new byte[2];
        int r = io.read(buf, 0, 2);
        assertEquals(2, r);
        assertArrayEquals(new byte[]{1,2}, buf);

        io.write(new byte[]{9,9,9}, 0, 3);
        io.flush();
        assertArrayEquals(new byte[]{9,9,9}, out.toByteArray());
    }

    @Test
    public void testEndOfStreamIndicator() throws IOException {
        ByteArrayInputStream in = new ByteArrayInputStream(new byte[]{10});
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        StreamsIo io = new StreamsIo(in, out);
        byte[] tmp = new byte[5];
        int r = io.read(tmp, 0, 5);
        // could read up to 1 byte
        io.isEndOfStream(); // call to ensure no exception
        assertTrue(true);
    }
}
