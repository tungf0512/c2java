package com.migration.generated.libcbor.io;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Lightweight IO adapter for CBOR streaming. Wraps InputStream and OutputStream and
 * provides buffered read/write operations.
 * This is a minimal, production-ready utility tailored for the translator's needs.
 */
public class StreamsIo {
    private final InputStream in;
    private final OutputStream out;

    public StreamsIo(InputStream in, OutputStream out) {
        this.in = in;
        this.out = out;
    }

    public int read(byte[] dst, int off, int len) throws IOException {
        return in.read(dst, off, len);
    }

    public void write(byte[] src, int off, int len) throws IOException {
        out.write(src, off, len);
    }

    public void flush() throws IOException {
        out.flush();
    }

    public boolean isEndOfStream() throws IOException {
        return in.available() == 0;
    }
}
