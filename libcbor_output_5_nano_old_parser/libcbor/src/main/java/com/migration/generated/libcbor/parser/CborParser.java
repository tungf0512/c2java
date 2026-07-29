package com.migration.generated.libcbor.parser;

import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.token.*;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;

/** Minimal streaming CBOR parser that produces Token objects. */
public class CborParser {
    private final StreamsIo io;
    private boolean end = false;
    private final byte[] tmp = new byte[8];

    public CborParser(StreamsIo io) {
        this.io = io;
    }

    // Simple helper to fill tmp buffer
    private int fill(int n) throws IOException {
        int read = 0;
        while (read < n) {
            int r = io.read(tmp, read, n - read);
            if (r == -1) return -1;
            read += r;
        }
        return read;
    }

    public boolean hasNext() {
        return !end;
    }

    public com.migration.generated.libcbor.token.Token next() throws IOException {
        if (end) throw new IOException("EOF");
        // Very small subset: read major type and immediate value if small
        int b = io.read(tmp, 0, 1);
        if (b <= 0) {
            end = true;
            return new NullToken();
        }
        int hi = tmp[0] & 0xFF;
        int major = (hi >> 5) & 0x07;
        int additional = hi & 0x1F;
        switch (major) {
            case 0: // unsigned int
                if (additional < 24) {
                    return new UnsignedIntToken(additional);
                } else if (additional == 24) {
                    int v = readUint(1);
                    return new UnsignedIntToken(v);
                } else if (additional == 25) {
                    int v = readUint(2);
                    return new UnsignedIntToken(v);
                } else if (additional == 26) {
                    int v = readUint(4);
                    return new UnsignedIntToken(v);
                } else {
                    int v = readUint(8);
                    return new UnsignedIntToken(v);
                }
            case 1: // negative int
                if (additional < 24) {
                    long val = -1 - additional;
                    return new NegativeIntToken(val);
                } else {
                    int len = (additional == 24 ? 1 : (additional == 25 ? 2 : (additional == 26 ? 4 : 8)));
                    long v = readUint64(len);
                    return new NegativeIntToken(-1 - v);
                }
            case 2: // byte string
                // For simplicity, treat as empty or small length if additional < 24
                if (additional < 24) {
                    if (additional == 0) return new ByteStringToken(new byte[0], 0);
                    // read that many bytes
                    byte[] arr = new byte[additional];
                    readFully(arr);
                    return new ByteStringToken(arr, additional);
                }
                // fallback: read length from subsequent bytes and skip actual data for simplicity
                int len = readLength(additional);
                byte[] data = new byte[len];
                readFully(data);
                return new ByteStringToken(data, len);
            case 3: // text string
                int tlen = readLength(additional);
                byte[] tdata = new byte[tlen];
                readFully(tdata);
                return new TextStringToken(new String(tdata));
            case 4:
            case 5:
            case 6:
            case 7:
            default:
                // Not implemented fully; return NullToken to indicate end/unsupported currently
                end = true;
                return new NullToken();
        }
    }

    private int readUint(int n) throws IOException {
        byte[] buf = new byte[n];
        readFully(buf);
        int val = 0;
        for (byte b : buf) val = (val << 8) | (b & 0xFF);
        return val;
    }

    private long readUint64(int n) throws IOException {
        byte[] buf = new byte[n];
        readFully(buf);
        long val = 0;
        for (byte b : buf) val = (val << 8) | (b & 0xFF);
        return val;
    }

    private int readLength(int additional) throws IOException {
        int len = additional;
        if (additional == 24) len = readUint(1);
        else if (additional == 25) len = readUint(2);
        else if (additional == 26) len = readUint(4);
        else if (additional == 27) len = (int) readUint64(8);
        return len;
    }

    private void readFully(byte[] dst) throws IOException {
        int off = 0;
        while (off < dst.length) {
            int r = io.read(dst, off, dst.length - off);
            if (r == -1) throw new IOException("Unexpected EOF");
            off += r;
        }
    }
}
