package com.migration.generated.libcbor;

@FunctionalInterface
public interface CborAllocator {
    byte[] allocate(int size);

    CborAllocator DEFAULT = byte[]::new;
}
