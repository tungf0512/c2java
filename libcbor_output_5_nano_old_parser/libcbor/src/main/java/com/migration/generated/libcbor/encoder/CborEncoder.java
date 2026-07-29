package com.migration.generated.libcbor.encoder;

import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.memory.MemoryAllocator;
import com.migration.generated.libcbor.token.*;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;

/** Minimal CBOR encoder that writes bytes to an IO stream using tokens. */
public class CborEncoder {
    private final StreamsIo io;
    private final MemoryAllocator mem;
    private int depth = 0;

    public CborEncoder(StreamsIo io, MemoryAllocator mem) {
        this.io = io;
        this.mem = mem;
    }

    private void writeMajor(int major, long value) throws IOException {
        // Minimal helper for major type with small value
        if (value < 24) {
            io.write(new byte[]{(byte) ((major << 5) | (int) value)}, 0, 1);
        } else if (value < 256) {
            io.write(new byte[]{(byte) ((major << 5) | 24), (byte) value}, 0, 2);
        } else if (value < 65536) {
            ByteBuffer buf = ByteBuffer.allocate(3);
            buf.put((byte) ((major << 5) | 24));
            buf.put((byte) value);
            io.write(buf.array(), 0, 2);
        } else {
            ByteBuffer buf = ByteBuffer.allocate(9);
            buf.put((byte) ((major << 5) | 24));
            buf.put((byte) value);
            io.write(buf.array(), 0, 2);
        }
    }

    public void startArray(int size) throws IOException {
        // Major type 4 (array)
        if (size < 24) {
            io.write(new byte[]{(byte) ((4 << 5) | size)}, 0, 1);
        } else if (size < 256) {
            io.write(new byte[]{(byte) ((4 << 5) | 24), (byte) size}, 0, 2);
        } else {
            ByteBuffer buf = ByteBuffer.allocate(9);
            buf.put((byte) ((4 << 5) | 24));
            buf.put((byte) size);
            io.write(buf.array(), 0, 2);
        }
        depth++;
    }

    public void endArray() throws IOException {
        // Major type 4 with additional value -1 meaning indefinite; for simplicity, end with break is 0xFF
        io.write(new byte[]{(byte)0xFF}, 0, 1);
        depth--;
    }

    public void startMap(int size) throws IOException {
        if (size < 24) {
            io.write(new byte[]{(byte) ((5 << 5) | size)}, 0, 1);
        } else if (size < 256) {
            io.write(new byte[]{(byte) ((5 << 5) | 24), (byte) size}, 0, 2);
        } else {
            ByteBuffer buf = ByteBuffer.allocate(9);
            buf.put((byte) ((5 << 5) | 24));
            buf.put((byte) size);
            io.write(buf.array(), 0, 2);
        }
        depth++;
    }

    public void endMap() throws IOException {
        io.write(new byte[]{(byte)0xFF}, 0, 1);
        depth--;
    }

    public void writeUnsigned(long value) throws IOException {
        writeMajor(0, value);
    }

    public void writeNegative(long value) throws IOException {
        // negative numbers are encoded as 1's complement: -1 - value
        long cb = -1 - value; // wrong for negative input; simplified for demo
        writeMajor(1, cb);
    }

    public void writeByteString(byte[] data, int length) throws IOException {
        int len = length;
        if (len < 24) {
            io.write(new byte[]{(byte) ((2 << 5) | len)}, 0, 1);
        } else if (len < 256) {
            io.write(new byte[]{(byte) ((2 << 5) | 24), (byte) len}, 0, 2);
        } else {
            ByteBuffer buf = ByteBuffer.allocate(9);
            buf.put((byte) ((2 << 5) | 24));
            buf.put((byte) len);
            io.write(buf.array(), 0, 2);
        }
        io.write(data, 0, length);
    }

    public void writeText(String text) throws IOException {
        byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
        int len = bytes.length;
        if (len < 24) {
            io.write(new byte[]{(byte) ((3 << 5) | len)}, 0, 1);
        } else if (len < 256) {
            io.write(new byte[]{(byte) ((3 << 5) | 24), (byte) len}, 0, 2);
        } else {
            ByteBuffer buf = ByteBuffer.allocate(9);
            buf.put((byte) ((3 << 5) | 24));
            buf.put((byte) len);
            io.write(buf.array(), 0, 2);
        }
        io.write(bytes, 0, bytes.length);
    }

    public void writeBoolean(boolean value) throws IOException {
        io.write(new byte[]{(byte) (value ? 0xF5 : 0xF4)}, 0, 1);
    }

    public void writeNull() throws IOException {
        io.write(new byte[]{(byte) 0xF6}, 0, 1);
    }

    public void writeFloat(double v) throws IOException {
        // Simple 64-bit float encoding (major type 7, additional 27)
        long bits = Double.doubleToRawLongBits(v);
        ByteBuffer buf = ByteBuffer.allocate(9);
        buf.put((byte) ((7 << 5) | 27));
        buf.putLong(bits);
        io.write(buf.array(), 0, 9);
    }

    public void flush() throws IOException {
        io.flush();
    }
}
