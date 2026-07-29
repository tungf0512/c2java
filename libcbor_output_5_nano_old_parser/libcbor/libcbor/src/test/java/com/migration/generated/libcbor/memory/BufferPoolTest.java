package com.migration.generated.libcbor.memory;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.nio.ByteBuffer;

public class BufferPoolTest {

    @Test
    public void testAcquireReuseBufferFromPool() {
        BufferPool pool = new BufferPool(1024);
        ByteBuffer buf = ByteBuffer.allocate(512);
        // Put some data to ensure it's the same buffer when reused
        buf.put((byte)1);
        buf.flip();
        pool.release(buf);
        ByteBuffer got = pool.acquire(256);
        assertSame(buf, got, "Expected to reuse the same buffer from pool");
        assertEquals(0, got.position());
        assertTrue(got.capacity() >= 512);
    }

    @Test
    public void testAcquireAllocatesNewWhenPoolEmpty() {
        BufferPool pool = new BufferPool(1024);
        ByteBuffer b = pool.acquire(128);
        assertNotNull(b);
        // capacity should be max(size, 256)
        assertTrue(b.capacity() >= 256);
    }

    @Test
    public void testReleaseBufferTooLargeDiscarded() {
        BufferPool pool = new BufferPool(1024);
        ByteBuffer large = ByteBuffer.allocate(2048);
        pool.release(large);
        ByteBuffer b = pool.acquire(128);
        // Should not return the previously discarded large buffer
        assertNotSame(large, b);
    }
}
