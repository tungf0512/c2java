package com.migration.generated.libcbor.memory;

import java.nio.ByteBuffer;

/** High-level memory allocator facade for CBOR encoding/decoding. */
public class MemoryAllocator {
    private final BufferPool pool;

    public MemoryAllocator(BufferPool pool) {
        this.pool = pool;
    }

    public ByteBuffer acquireBuffer(int size) {
        return pool.acquire(size);
    }

    public void releaseBuffer(ByteBuffer buffer) {
        pool.release(buffer);
    }
}
