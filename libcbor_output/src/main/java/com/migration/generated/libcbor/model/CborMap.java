package com.migration.generated.libcbor.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public final class CborMap extends CborItem {
    private final boolean indefinite;
    private final List<CborPair> pairs;
    private final int expectedSize;

    public CborMap(int expectedSize) {
        if (expectedSize < 0) {
            throw new IllegalArgumentException("Expected size must not be negative");
        }
        this.indefinite = false;
        this.expectedSize = expectedSize;
        this.pairs = new ArrayList<>(expectedSize);
    }

    public CborMap() {
        this.indefinite = true;
        this.expectedSize = -1;
        this.pairs = new ArrayList<>();
    }

    public boolean isIndefinite() {
        return indefinite;
    }

    public void add(CborItem key, CborItem value) {
        pairs.add(new CborPair(key, value));
    }

    public List<CborPair> pairs() {
        return Collections.unmodifiableList(pairs);
    }

    public int size() {
        return pairs.size();
    }

    public int expectedSize() {
        return expectedSize;
    }

    @Override
    public CborType type() {
        return CborType.MAP;
    }

    @Override
    public CborItem deepCopy() {
        CborMap copy = indefinite ? new CborMap() : new CborMap(expectedSize);
        for (CborPair pair : pairs) {
            copy.pairs.add(pair.deepCopy());
        }
        return copy;
    }

    @Override
    public CborItem deepCopyDefinite() {
        CborMap copy = new CborMap(pairs.size());
        for (CborPair pair : pairs) {
            copy.pairs.add(pair.deepCopyDefinite());
        }
        return copy;
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof CborMap other && indefinite == other.indefinite && pairs.equals(other.pairs);
    }

    @Override
    public int hashCode() {
        return pairs.hashCode() * 31 + Boolean.hashCode(indefinite);
    }
}
