package com.migration.generated.libcbor.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public final class CborArray extends CborItem {
    private final boolean indefinite;
    private final List<CborItem> items;
    private final int expectedSize;

    public CborArray(int expectedSize) {
        if (expectedSize < 0) {
            throw new IllegalArgumentException("Expected size must not be negative");
        }
        this.indefinite = false;
        this.expectedSize = expectedSize;
        this.items = new ArrayList<>(expectedSize);
    }

    public CborArray() {
        this.indefinite = true;
        this.expectedSize = -1;
        this.items = new ArrayList<>();
    }

    public boolean isIndefinite() {
        return indefinite;
    }

    public int expectedSize() {
        return expectedSize;
    }

    public void add(CborItem item) {
        if (item == null) {
            throw new IllegalArgumentException("Array item must not be null");
        }
        items.add(item);
    }

    public List<CborItem> items() {
        return Collections.unmodifiableList(items);
    }

    public int size() {
        return items.size();
    }

    @Override
    public CborType type() {
        return CborType.ARRAY;
    }

    @Override
    public CborItem deepCopy() {
        CborArray copy = indefinite ? new CborArray() : new CborArray(expectedSize);
        for (CborItem item : items) {
            copy.add(item.deepCopy());
        }
        return copy;
    }

    @Override
    public CborItem deepCopyDefinite() {
        CborArray copy = new CborArray(items.size());
        for (CborItem item : items) {
            copy.add(item.deepCopyDefinite());
        }
        return copy;
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborArray other && indefinite == other.indefinite && items.equals(other.items);
    }

    @Override
    public int hashCode() {
        return items.hashCode() * 31 + Boolean.hashCode(indefinite);
    }
}
