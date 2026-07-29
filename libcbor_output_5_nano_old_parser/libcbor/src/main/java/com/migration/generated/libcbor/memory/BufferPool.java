package com.migration.generated.libcbor.memory;

import java.nio.ByteBuffer;
import java.util.ArrayDeque;
import java.util.Queue;

/** Simple byte buffer pool to reuse ByteBuffers and reduce allocations. */
public class BufferPool {
    private final Queue<ByteBuffer> pool = new ArrayDeque<>();
    private final int maxBufferSize;

    public BufferPool(int maxBufferSize) {
        this.maxBufferSize = maxBufferSize;
    }

    public synchronized ByteBuffer acquire(int size) {
        ByteBuffer head = pool.peek();
        if (head != null && head.capacity() >= size) {
            pool.poll();
            head.clear();
            return head;
        }
        // Allocate a new buffer if none available
        return ByteBuffer.allocate(Math.max(size, 256));
    }

    public synchronized void release(ByteBuffer buffer) {
        if (buffer.capacity() <= maxBufferSize) {
            buffer.clear();
            pool.add(buffer);
        }
    }
}
